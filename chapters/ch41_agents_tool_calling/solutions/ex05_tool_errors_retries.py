"""
Exercise 05 — Tool Error Handling and Retries                       [Tier: ★ Core]
Chapter 41 · Pattern: error classification + bounded retry · Target time: 30 min

Problem
-------
Tools fail. A good agent runtime distinguishes *who* should fix the failure:

=============  ==========================================  =====================================
class          examples                                    what the runtime does
=============  ==========================================  =====================================
transient      TimeoutError, ConnectionError, HTTP 429/503 retry with exponential backoff
invalid_input  ValueError, KeyError, TypeError, 400/404     no retry; tell the *model* what was
                                                            wrong so it can fix its arguments
internal       anything else (bugs)                        no retry; generic message to the
                                                            model, details only in your logs
=============  ==========================================  =====================================

Implement:

- ``classify(exc) -> str`` returning one of the three classes above.
- ``execute_with_retries(fn, args, max_attempts=3, base_delay=0.5, max_delay=4.0, sleep=...)``
  that calls ``fn(**args)``, retries only transient errors, sleeping
  ``min(max_delay, base_delay * 2**(attempt-1))`` between attempts (``sleep`` is injected so tests
  run instantly), and returns a ``ToolOutcome(ok, result, error_type, message, attempts)``.
- ``to_observation(outcome) -> str``: a JSON string for the model. Internal errors must not leak
  exception text (it may contain secrets, paths or stack details).

Finally, ``run_agent`` shows a mock model that sends a bad argument, reads the error observation
and corrects itself on the next turn.

Examples
--------
>>> classify(TimeoutError()), classify(ValueError()), classify(ZeroDivisionError())
('transient', 'invalid_input', 'internal')

Constraints
-----------
- Deterministic: no jitter here (Chapter 42 adds full jitter); delays are recorded, not slept.

Approach ladder
---------------
1. Brute force — let exceptions propagate: one flaky API call kills the whole conversation.
2. Improved   — catch everything and retry everything: retries bad input pointlessly (it will fail
   identically) and multiplies load on a struggling dependency.
3. Optimal    — classify, retry only transient failures with capped backoff, feed fixable errors to
   the model as data. Worst case ``max_attempts`` calls and sum(delays) waiting.

Hints
-----
- ``isinstance(exc, (TimeoutError, ConnectionError, TransientToolError))``.
- Record the attempt count on success too — it is a useful metric (retry rate).

Follow-ups
----------
- Add a per-request *retry budget* so many tools cannot multiply retries (retry storms).
- What if the tool is not idempotent (e.g. "send email")? Retry only with an idempotency key.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


class TransientToolError(Exception):
    """Raised by tools for retryable failures such as HTTP 429 or 503."""


TRANSIENT = (TransientToolError, TimeoutError, ConnectionError)
INVALID_INPUT = (ValueError, KeyError, TypeError, LookupError)


def classify(exc: BaseException) -> str:
    if isinstance(exc, TRANSIENT):
        return "transient"
    if isinstance(exc, INVALID_INPUT):
        return "invalid_input"
    return "internal"


@dataclass
class ToolOutcome:
    ok: bool
    result: Any = None
    error_type: str | None = None
    message: str = ""
    attempts: int = 0


def execute_with_retries(fn: Callable[..., Any], args: dict, *, max_attempts: int = 3,
                         base_delay: float = 0.5, max_delay: float = 4.0,
                         sleep: Callable[[float], None] = lambda s: None) -> ToolOutcome:
    for attempt in range(1, max_attempts + 1):
        try:
            return ToolOutcome(True, fn(**args), attempts=attempt)
        except Exception as exc:  # noqa: BLE001 - classified below
            kind = classify(exc)
            if kind != "transient" or attempt == max_attempts:
                return ToolOutcome(False, None, kind, f"{type(exc).__name__}: {exc}", attempt)
            sleep(min(max_delay, base_delay * 2 ** (attempt - 1)))
    raise AssertionError("unreachable")


def to_observation(outcome: ToolOutcome) -> str:
    if outcome.ok:
        return json.dumps({"ok": True, "result": outcome.result}, sort_keys=True)
    message = outcome.message
    if outcome.error_type == "internal":
        message = "the tool failed unexpectedly; try a different approach or tell the user"
    return json.dumps({"ok": False, "error": {
        "type": outcome.error_type, "message": message,
        "retryable": False,  # we already retried transient errors ourselves
        "attempts": outcome.attempts}}, sort_keys=True)


# ---- demo tools -----------------------------------------------------------------------------
class FlakyRates:
    """Fails with a transient error the first ``fail_times`` calls."""

    def __init__(self, fail_times: int) -> None:
        self.fail_times, self.calls = fail_times, 0

    def __call__(self, currency: str) -> float:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise TransientToolError("503 Service Unavailable")
        return {"EUR": 0.92, "GBP": 0.79}[currency]


def convert(amount: float, currency: str) -> float:
    if not isinstance(amount, (int, float)):
        raise TypeError(f"amount must be a number, got {type(amount).__name__}")
    rates = {"EUR": 0.92, "GBP": 0.79}
    if currency not in rates:
        raise ValueError(f"unsupported currency {currency!r}; use one of {sorted(rates)}")
    return round(amount * rates[currency], 2)


def buggy_tool(x: int) -> int:
    secret = "db-password=hunter2"  # noqa: F841 - pretend this leaks into the message
    raise ZeroDivisionError(f"division by zero while using {secret}")


class SelfCorrectingModel:
    """Mock model: first call uses a bad argument, then fixes it from the error observation."""

    def complete(self, messages: list[dict]) -> dict:
        tool_msgs = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
        if not tool_msgs:
            return {"tool": "convert", "args": {"amount": "100", "currency": "EUR"}}
        last = tool_msgs[-1]
        if not last["ok"] and "amount must be a number" in last["error"]["message"]:
            return {"tool": "convert", "args": {"amount": 100, "currency": "EUR"}}
        if last["ok"]:
            return {"final": f"100 USD is {last['result']} EUR."}
        return {"final": "Sorry, the conversion failed."}


def run_agent(model, tools: dict[str, Callable], question: str, max_turns: int = 4):
    messages = [{"role": "user", "content": question}]
    for _ in range(max_turns):
        move = model.complete(messages)
        if "final" in move:
            return move["final"], messages
        outcome = execute_with_retries(tools[move["tool"]], move["args"])
        messages.append({"role": "assistant", "content": json.dumps(move, sort_keys=True)})
        messages.append({"role": "tool", "content": to_observation(outcome)})
    return None, messages


def main() -> None:
    delays: list[float] = []
    print("== retries")
    cases = [
        ("flaky (2 failures)", FlakyRates(2), {"currency": "EUR"}),
        ("flaky (9 failures)", FlakyRates(9), {"currency": "EUR"}),
        ("bad input", convert, {"amount": 5, "currency": "JPY"}),
        ("internal bug", buggy_tool, {"x": 1}),
    ]
    for label, fn, args in cases:
        delays.clear()
        out = execute_with_retries(fn, args, max_attempts=4, sleep=delays.append)
        calls = getattr(fn, "calls", out.attempts)
        print(f"  {label:20} ok={out.ok} attempts={out.attempts} calls={calls} "
              f"slept={delays} type={out.error_type}")
        print(f"  {'':20} observation={to_observation(out)}")
    print("== self-correcting agent")
    answer, messages = run_agent(SelfCorrectingModel(), {"convert": convert}, "100 USD in EUR?")
    for m in messages:
        print(f"  {m['role']:9}: {m['content']}")
    print("  answer:", answer)


if __name__ == "__main__":
    main()
