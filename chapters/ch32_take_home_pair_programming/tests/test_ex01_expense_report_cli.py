import io
import json
from decimal import Decimal

import pytest

M = "ex01_expense_report_cli"
HEAD = "date,category,amount,note"


def test_parse_valid_and_normalise(load):
    m = load(M)
    txns, errors = m.parse_rows([HEAD, "2024-03-01, Food ,1.10,x",
                                 '2024-03-02,food,"2.20","a, b"'])
    assert errors == []
    assert [t.category for t in txns] == ["food", "food"]
    assert txns[1].note == "a, b"                       # quoted comma kept
    assert sum(t.amount for t in txns) == Decimal("3.30")


@pytest.mark.parametrize("row, reason", [
    ("x,food,1,", "bad date 'x'"),
    ("2024-02-30,food,1,", "bad date '2024-02-30'"),
    ("20240301,food,1,", "bad date '20240301'"),          # accepted by 3.11+ fromisoformat
    ("2024-W10-1,food,1,", "bad date '2024-W10-1'"),
    ("2024-3-01,food,1,", "bad date '2024-3-01'"),
    ("2024-03-01,food,abc,", "bad amount 'abc'"),
    ("2024-03-01,food,NaN,", "bad amount 'NaN'"),
    ("2024-03-01,,1,", "missing category"),
    ("2024-03-01,food", "missing column(s)"),
])
def test_bad_rows_reported_with_line(load, row, reason):
    m = load(M)
    txns, errors = m.parse_rows([HEAD, "2024-03-01,ok,1,", row])
    assert len(txns) == 1
    assert errors == [f"line 3: {reason}"]


def test_header_problems(load):
    m = load(M)
    assert m.parse_rows([]) == ([], ["line 1: empty file"])
    txns, errors = m.parse_rows(["a,b,c", "2024-03-01,food,1,"])
    assert txns == [] and errors[0].startswith("line 1: unknown header")
    assert m.parse_rows([HEAD, "", "2024-03-01,f,1,"])[1] == []   # blank line tolerated


def test_summarize_sort_month_and_refunds(load):
    m = load(M)
    txns, _ = m.parse_rows([HEAD, "2024-03-01,b,5,", "2024-03-02,a,5,", "2024-03-03,c,9,",
                            "2024-03-04,c,-2,", "2024-04-01,a,100,"])
    assert m.summarize(txns, "2024-03") == [("c", Decimal("7")), ("a", Decimal("5")),
                                            ("b", Decimal("5"))]
    assert m.summarize(txns)[0] == ("a", Decimal("105"))
    assert m.summarize(txns, "1999-01") == []


def test_render(load):
    m = load(M)
    s = [("rent", Decimal("1200")), ("bus", Decimal("2.9"))]
    assert m.render_text(s).splitlines() == ["rent      1200.00", "bus          2.90",
                                             "TOTAL     1202.90"]
    assert m.render_text([]) == "no transactions\n"
    assert list(json.loads(m.render_json(s)).items()) == [("rent", "1200.00"), ("bus", "2.90")]


def run(m, argv):
    out, err = io.StringIO(), io.StringIO()
    return m.cli(argv, out, err), out.getvalue(), err.getvalue()


def test_cli_end_to_end(load, tmp_path):
    m = load(M)
    f = tmp_path / "t.csv"
    f.write_text(HEAD + "\n2024-03-01,food,1.5,\n2024-03-02,food,zz,\n", encoding="utf-8")
    code, out, err = run(m, [str(f), "--format", "json"])
    assert code == 0 and json.loads(out) == {"food": "1.50"}
    assert "line 3: bad amount 'zz'" in err
    assert run(m, [str(f), "--strict"])[0] == 1
    code, out, err = run(m, [str(tmp_path / "nope.csv")])
    assert code == 1 and out == "" and "nope.csv" in err


def test_cli_on_repo_data(load):
    m = load(M)
    code, out, err = run(m, [str(m.DATA), "--month", "2024-03"])
    assert code == 0
    assert out.splitlines()[-1].split() == ["TOTAL", "1317.15"]
    assert err.count("warning:") == 3


@pytest.mark.parametrize("args", [["--month", "2024-13"], ["--month", "202403"],
                                  ["--month", "2024-3"], ["--format", "xml"]])
def test_cli_bad_arguments_exit_2(load, tmp_path, capsys, args):
    m = load(M)
    f = tmp_path / "t.csv"
    f.write_text(HEAD + "\n", encoding="utf-8")
    code, out, err = run(m, [str(f), *args])
    assert code == 2 and out == "" and "usage:" in err   # usage goes to OUR err stream
    assert capsys.readouterr() == ("", "")               # nothing leaked to the real streams


def test_cli_no_args_and_help(load, capsys):
    m = load(M)
    code, out, err = run(m, [])
    assert code == 2 and "usage:" in err
    code, out, err = run(m, ["--help"])
    assert code == 0 and out.startswith("usage:") and err == ""
    assert capsys.readouterr() == ("", "")


def test_cli_unreadable_inputs_exit_1_without_traceback(load, tmp_path):
    m = load(M)
    code, out, err = run(m, [str(tmp_path)])                    # a directory
    assert code == 1 and out == "" and err.startswith("error: cannot read")
    bad = tmp_path / "latin1.csv"
    bad.write_bytes(HEAD.encode() + b"\n2024-03-01,caf\xe9,1,\n")
    code, out, err = run(m, [str(bad)])
    assert code == 1 and err == "error: latin1.csv is not UTF-8 text\n"


def test_strict_on_clean_file_exits_0(load, tmp_path):
    m = load(M)
    f = tmp_path / "ok.csv"
    f.write_text(HEAD + "\n2024-03-01,food,2.50,\n", encoding="utf-8")
    code, out, err = run(m, [str(f), "--strict"])
    assert code == 0 and err == "" and out.splitlines()[-1].split() == ["TOTAL", "2.50"]


def test_line_numbers_count_quoted_newlines(load):
    m = load(M)
    lines = [HEAD + "\n", '2024-03-01,food,1,"two\n', 'line note"\n', "2024-03-02,food,zz,\n"]
    txns, errors = m.parse_rows(lines)
    assert txns[0].note == "two\nline note"
    assert errors == ["line 4: bad amount 'zz'"]              # physical line, not record 3
