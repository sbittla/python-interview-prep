from contextlib import closing
import math
import sqlite3

import numpy as np
import pandas as pd


def small():
    days = ["2026-03-01", "2026-03-02", "2026-03-03", "2026-03-04", "2026-03-05", "2026-03-06",
            "2026-03-07", "2026-03-10", "2026-03-11"]
    return pd.DataFrame({"date": pd.to_datetime(days), "store": ["s"] * len(days),
                         "revenue": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 20.0]})


def test_small_hand_computed(load):
    m = load("ex08_rolling_windows")
    wf = m.window_features(small())
    assert wf["run_total"].tolist() == [1, 3, 6, 10, 15, 21, 28, 38, 58]
    assert math.isnan(wf["prev"].iloc[0]) and wf["prev"].iloc[1] == 1.0
    assert wf["dod_pct"].iloc[1] == 100.0
    assert wf["rows_7"].isna().sum() == 6
    assert wf["rows_7"].iloc[6:].tolist() == [4.0, round(37 / 7, 2), round(55 / 7, 2)]
    # calendar window for 03-10 covers 03-04..03-10 -> 4, 5, 6, 7, 10
    assert wf["days_7"].iloc[7] == 6.4
    assert wf["days_7"].iloc[0] == 1.0          # time windows use whatever rows exist


def test_brute_force(load):
    m = load("ex08_rolling_windows")
    vals = [float(v) for v in range(1, 12)]
    assert np.allclose(m.brute_force_rows_7(vals), pd.Series(vals).rolling(7).mean(), equal_nan=True)


def test_two_stores_do_not_mix(load):
    m = load("ex08_rolling_windows")
    a = small()
    b = small().assign(store="t", revenue=lambda d: d["revenue"] * 100)
    wf = m.window_features(pd.concat([b, a], ignore_index=True))
    assert wf["store"].tolist() == ["s"] * 9 + ["t"] * 9
    assert wf["run_total"].iloc[8] == 58 and wf["run_total"].iloc[17] == 5800
    assert math.isnan(wf["prev"].iloc[9])


def test_matches_sql_on_real_data(load):
    m = load("ex08_rolling_windows")
    sales = m.load_sales()
    wf = m.window_features(sales)
    with closing(sqlite3.connect(":memory:")) as conn:
        sales.assign(date=sales["date"].dt.strftime("%Y-%m-%d")).to_sql("sales", conn, index=False)
        sql = m.sql_window_features(conn)
    num = ["revenue", "run_total", "prev", "dod_pct", "rows_7", "days_7"]
    assert sql["store"].equals(wf["store"]) and sql["date"].equals(wf["date"])
    assert np.allclose(sql[num].to_numpy(float), wf[num].to_numpy(float), equal_nan=True, atol=0.011)
