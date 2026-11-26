"""
Exercise 02 — Seeded Leitner Scheduler                         [Tier: ★ Core]
Chapter 44 · Pattern: state machine + priority ordering · Target time: 25 min

Problem
-------
Drill the concept bank with Leitner boxes on the same ladder as §3.4.
Days are integers (day 0 = first study day). Every card starts in box 0,
due on day 0.

- Answer right: move up one box. Box b (1..len(ladder)) is next due
  ``ladder[b - 1]`` days later; moving past the last box **retires** the card.
- Answer wrong: back to box 0, due ``ladder[0]`` days later; count a lapse.

With the default ladder (1, 3, 7, 21) a card answered right every time is
reviewed on days 0, 1, 4, 11 and 32, then retired — the §3.4 schedule.

Implement ``Leitner(ids, ladder=LADDER, seed=0, daily_cap=None)`` with

- ``due(day)`` — ids of active cards with ``due <= day``, most urgent first:
  sorted by (due day, box, id), so overdue and weak cards come first;
- ``session(day)`` — the first ``daily_cap`` ids of ``due(day)`` (all if
  None), returned in a shuffled order from ``random.Random(seed * 1_000_003
  + day)`` so you cannot learn answers by position; the same seed and day
  always give the same order;
- ``review(card_id, day, correct)`` — apply the rules; raise ``KeyError``
  for an unknown id and ``ValueError`` if the card is retired or not yet due;
- ``simulate(days, recall)`` — for each day 0..days-1 run that day's session,
  asking ``recall(card_id, box, day) -> bool``; return a list of
  ``(day, [(card_id, correct), ...])`` for days with at least one review.

Examples
--------
>>> s = Leitner(["a"])
>>> [d for d, _ in s.simulate(40, lambda c, b, d: True)]
[0, 1, 4, 11, 32]
>>> s.retired
{'a'}

Constraints
-----------
- ids are unique non-empty strings; ladder is strictly increasing positive
  ints; daily_cap is None or >= 1 (``ValueError`` otherwise).
- Deterministic: no wall-clock time, no global ``random`` state.

Approach ladder
---------------
1. Re-scan the whole deck every day and review everything — O(n) per day and
   no spacing at all; it trains recognition, not recall.
2. Store a due day per card; scan for due cards — O(n log n) per day (sort by
   urgency). Simple and plenty for a deck of a few hundred cards.
3. A heap keyed by (due, box, id) makes ``due`` O(k log n) for k due cards;
   only worth it for very large decks. Rung 2 is the reference.

Follow-ups
----------
- Why shuffle after capping, not before? Capping picks *which* cards (by
  urgency); shuffling only hides *order*.
- Add per-section caps so one weak section cannot starve the others.
- Wrong-but-tempting: resetting a wrong card to "due today" — it then repeats
  immediately and you rehearse short-term memory, not recall.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

LADDER = (1, 3, 7, 21)
BANK_PATH = Path(__file__).resolve().parent.parent / "data" / "qa_bank.json"


@dataclass
class Card:
    id: str
    box: int = 0
    due: int = 0
    reviews: int = 0
    lapses: int = 0


class Leitner:
    def __init__(self, ids: Iterable[str], ladder: tuple[int, ...] = LADDER,
                 seed: int = 0, daily_cap: int | None = None) -> None:
        ids = list(ids)
        if len(set(ids)) != len(ids) or not all(isinstance(i, str) and i for i in ids):
            raise ValueError("ids must be unique non-empty strings")
        ladder = tuple(ladder)
        if not ladder or any(not isinstance(g, int) or g <= 0 for g in ladder) \
                or any(a >= b for a, b in zip(ladder, ladder[1:])):
            raise ValueError("ladder must be strictly increasing positive ints")
        if daily_cap is not None and daily_cap < 1:
            raise ValueError("daily_cap must be None or >= 1")
        self.ladder, self.seed, self.daily_cap = ladder, seed, daily_cap
        self.cards = {i: Card(i) for i in ids}
        self.retired: set[str] = set()

    def due(self, day: int) -> list[str]:
        active = [c for c in self.cards.values() if c.id not in self.retired and c.due <= day]
        active.sort(key=lambda c: (c.due, c.box, c.id))
        return [c.id for c in active]

    def session(self, day: int) -> list[str]:
        picked = self.due(day)
        if self.daily_cap is not None:
            picked = picked[: self.daily_cap]
        random.Random(self.seed * 1_000_003 + day).shuffle(picked)
        return picked

    def review(self, card_id: str, day: int, correct: bool) -> None:
        card = self.cards[card_id]                     # KeyError for unknown ids
        if card_id in self.retired:
            raise ValueError(f"{card_id} is retired")
        if card.due > day:
            raise ValueError(f"{card_id} is not due until day {card.due}")
        card.reviews += 1
        if correct:
            card.box += 1
            if card.box > len(self.ladder):
                self.retired.add(card_id)
            else:
                card.due = day + self.ladder[card.box - 1]
        else:
            card.box, card.lapses = 0, card.lapses + 1
            card.due = day + self.ladder[0]

    def simulate(self, days: int, recall: Callable[[str, int, int], bool]
                 ) -> list[tuple[int, list[tuple[str, bool]]]]:
        log = []
        for day in range(days):
            results = []
            for cid in self.session(day):
                ok = bool(recall(cid, self.cards[cid].box, day))
                self.review(cid, day, ok)
                results.append((cid, ok))
            if results:
                log.append((day, results))
        return log


def main() -> None:
    perfect = Leitner(["py01"])
    print("always right, review days:", [d for d, _ in perfect.simulate(40, lambda c, b, d: True)],
          "retired:", sorted(perfect.retired))

    flaky = Leitner(["al02"])
    answers = iter([True, True, False] + [True] * 5)
    days = [d for d, _ in flaky.simulate(60, lambda c, b, d: next(answers))]
    print("right, right, wrong, then right:", days, "lapses:", flaky.cards["al02"].lapses)

    ids = [e["id"] for e in json.loads(BANK_PATH.read_text(encoding="utf-8"))]
    rng = random.Random(44)
    # A learner who knows a card better the higher its box is (60 % in box 0 → 100 % in box 4).
    deck = Leitner(ids, seed=7, daily_cap=25)
    log = deck.simulate(45, lambda cid, box, day: rng.random() < 0.6 + 0.1 * box)
    print(f"deck of {len(ids)} cards, cap 25/day, 45 days")
    for day, results in log[:4]:
        print(f"  day {day:2d}: {len(results):2d} reviews, first three {[c for c, _ in results[:3]]}")
    print("  study days:", len(log), "| total reviews:", sum(len(r) for _, r in log))
    print("  retired:", len(deck.retired), "| still active:", len(ids) - len(deck.retired))
    boxes = [0] * (len(LADDER) + 1)
    for c in deck.cards.values():
        if c.id not in deck.retired:
            boxes[c.box] += 1
    print("  active cards per box 0..4:", boxes)
    worst = sorted(deck.cards.values(), key=lambda c: (-c.lapses, c.id))[:3]
    print("  most lapses:", [(c.id, c.lapses) for c in worst])
    print("same seed, same day -> same order:",
          Leitner(ids, seed=7).session(0) == Leitner(ids, seed=7).session(0))


if __name__ == "__main__":
    main()
