"""
Exercise 07 — In-Memory KV Database with Nested Transactions [Tier: ◆ Extended]
Chapter 29 · Pattern: undo log stack + command interpreter · Target time: 45 min

Problem
-------
Build a tiny key-value database and a command interpreter for it.

    SET <key> <value>   store value
    GET <key>           print the value, or NULL
    DELETE <key>        remove the key (no-op if absent)
    COUNT <value>       print how many keys currently hold exactly this value
    BEGIN               open a (possibly nested) transaction
    ROLLBACK            undo every change made in the innermost open transaction;
                        print NO TRANSACTION if none is open
    COMMIT              fold the innermost transaction into its parent (or make it
                        permanent if it is the outermost); print NO TRANSACTION if none
    END                 stop processing

`run(commands) -> list[str]` executes the lines and returns everything that would be
printed. GET and COUNT must be O(1); BEGIN must be O(1) — no copying the whole database.

Examples
--------
>>> run(["SET a 10", "BEGIN", "SET a 20", "GET a", "ROLLBACK", "GET a", "END"])
['20', '10']

Constraints
-----------
- Up to 10**5 commands; nesting depth up to 10**3; keys and values have no spaces.

Approach ladder
---------------
1. Brute force — BEGIN pushes a full copy of the dict; ROLLBACK pops it. O(n) per BEGIN
   and O(n) memory per level. COUNT scans all values: O(n).
2. Improved   — keep a `value -> count` dict alongside the data so COUNT is O(1).
3. Optimal    — an *undo log* per transaction: before the first write to a key inside a
   transaction, remember its old value (or a MISSING sentinel). ROLLBACK replays the log;
   COMMIT merges the log into the parent's (parent's older entry wins). Cost is
   proportional to the number of keys changed, not the size of the database.

Hints
-----
- Funnel every mutation through one private `_write(key, value_or_MISSING)` that
  updates data, value counts and the undo log. Then SET, DELETE and ROLLBACK are trivial.
- ROLLBACK must not record into the undo log it is replaying.

Follow-ups
----------
- Make COMMIT close *all* transactions (a common variant) — a one-line change.
- Persistence: append each committed change to a write-ahead log and replay on start.
- Isolation between two concurrent clients (MVCC, see the time-based KV store).
"""
from __future__ import annotations

from collections import Counter

MISSING = object()          # sentinel: "key did not exist"


class SnapshotDB:
    """Rung 1: copy-on-BEGIN. Simple and correct, but O(n) per BEGIN and per COUNT."""

    def __init__(self) -> None:
        self.data: dict[str, str] = {}
        self.stack: list[dict[str, str]] = []

    def set(self, key: str, value: str) -> None:
        self.data[key] = value

    def get(self, key: str) -> str | None:
        return self.data.get(key)

    def delete(self, key: str) -> None:
        self.data.pop(key, None)

    def count(self, value: str) -> int:
        return sum(1 for v in self.data.values() if v == value)

    def begin(self) -> None:
        self.stack.append(dict(self.data))

    def rollback(self) -> bool:
        if not self.stack:
            return False
        self.data = self.stack.pop()
        return True

    def commit(self) -> bool:
        if not self.stack:
            return False
        self.stack.pop()
        return True


class Database:
    """Rung 3: undo logs. All operations O(1) except ROLLBACK/COMMIT = O(keys touched)."""

    def __init__(self) -> None:
        self.data: dict[str, str] = {}
        self.counts: Counter[str] = Counter()
        self.undo: list[dict[str, object]] = []      # one dict per open transaction

    def _write(self, key: str, value: object, log: bool = True) -> None:
        old = self.data.get(key, MISSING)
        if old is value or old == value:
            return
        if log and self.undo:
            self.undo[-1].setdefault(key, old)       # first write in this txn wins
        if old is not MISSING:
            self.counts[old] -= 1
            if not self.counts[old]:
                del self.counts[old]
        if value is MISSING:
            del self.data[key]
        else:
            self.data[key] = value
            self.counts[value] += 1

    def set(self, key: str, value: str) -> None:
        self._write(key, value)

    def get(self, key: str) -> str | None:
        return self.data.get(key)

    def delete(self, key: str) -> None:
        if key in self.data:
            self._write(key, MISSING)

    def count(self, value: str) -> int:
        return self.counts.get(value, 0)

    def begin(self) -> None:
        self.undo.append({})

    def rollback(self) -> bool:
        if not self.undo:
            return False
        for key, old in self.undo.pop().items():
            self._write(key, old, log=False)
        return True

    def commit(self) -> bool:
        if not self.undo:
            return False
        child = self.undo.pop()
        if self.undo:                                # merge into the parent transaction
            parent = self.undo[-1]
            for key, old in child.items():
                parent.setdefault(key, old)
        return True


class Stop(Exception):
    """Raised by `execute` on END."""


def execute(db, line: str) -> str | None:
    """Run one command line against db; return the text it prints (or None)."""
    parts = line.split()
    if not parts:
        return None
    cmd, args = parts[0].upper(), parts[1:]
    if cmd == "END":
        raise Stop
    if cmd == "SET" and len(args) == 2:
        db.set(*args)
    elif cmd == "GET" and len(args) == 1:
        value = db.get(args[0])
        return "NULL" if value is None else value
    elif cmd in ("DELETE", "UNSET") and len(args) == 1:
        db.delete(args[0])
    elif cmd == "COUNT" and len(args) == 1:
        return str(db.count(args[0]))
    elif cmd == "BEGIN" and not args:
        db.begin()
    elif cmd == "ROLLBACK" and not args:
        return None if db.rollback() else "NO TRANSACTION"
    elif cmd == "COMMIT" and not args:
        return None if db.commit() else "NO TRANSACTION"
    else:
        return f"ERROR: {cmd}"
    return None


def run(commands: list[str], db_factory=Database) -> list[str]:
    db = db_factory()
    out: list[str] = []
    for line in commands:
        try:
            result = execute(db, line)
        except Stop:
            break
        if result is not None:
            out.append(result)
    return out


SCRIPT = """\
SET a 10
SET b 10
COUNT 10
BEGIN
SET a 20
DELETE b
COUNT 10
BEGIN
SET a 30
GET a
ROLLBACK
GET a
GET b
COMMIT
ROLLBACK
GET a
COUNT 20
BEGIN
SET c 5
BEGIN
SET c 6
COMMIT
ROLLBACK
GET c
FROB x
END
GET a"""


def main() -> None:
    lines = SCRIPT.splitlines()
    db = Database()
    width = max(len(line) for line in lines)
    print(f"{'command':<{width}}  | output         | open txns | data")
    for line in lines:
        try:
            result = execute(db, line)
        except Stop:
            print(f"{line:<{width}}  | (stop)")
            break
        print(f"{line:<{width}}  | {result or '':<14} | {len(db.undo):^9} | {dict(sorted(db.data.items()))}")
    print("snapshot DB gives the same outputs:", run(lines) == run(lines, SnapshotDB))
    print("COUNT index after script:", dict(sorted(db.counts.items())))


if __name__ == "__main__":
    main()
