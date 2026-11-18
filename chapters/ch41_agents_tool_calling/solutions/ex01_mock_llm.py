"""
Exercise 01 — A Deterministic Mock LLM and an Output Parser        [Tier: ★ Core]
Chapter 41 · Pattern: test double + defensive parsing · Target time: 25 min

Problem
-------
Agent code is hard to test against a real model: answers vary, calls cost money and need a network.
Build two deterministic stand-ins and the parser every agent needs:

1. ``ScriptedLLM(responses)`` returns its canned responses in order, one per ``complete(messages)``
   call, and records a copy of every message list it was shown. Running out of script is an error.
2. ``RuleBasedLLM(rules, default)`` looks at the *last* message's content and returns the response
   of the first rule whose regex matches (a rule's response is a function of the regex match).
3. ``parse_model_output(raw)`` turns raw model text into either ``ToolCall(id, name, arguments)``
   or ``Final(content)``. The wire format is JSON:
   ``{"type": "tool_call", "id": "call_1", "name": "get_weather", "arguments": {"city": "Oslo"}}``
   or ``{"type": "final", "content": "..."}``. Plain text (not starting with ``{``) is a final
   answer. Models often wrap JSON in ```json fences and sometimes send ``arguments`` as a JSON
   *string*; accept both. Anything else malformed raises ``ModelOutputError``.

Examples
--------
>>> parse_model_output('{"type": "final", "content": "hi"}')
Final(content='hi')
>>> parse_model_output('```json\\n{"type":"tool_call","id":"c1","name":"f","arguments":"{}"}\\n```')
ToolCall(id='c1', name='f', arguments={})

Constraints
-----------
- Standard library only; no randomness; identical input -> identical output.

Approach ladder
---------------
1. Brute force — ``json.loads`` and index keys directly: crashes with KeyError/TypeError on the
   first malformed output, which in production is every few thousand calls.
2. Improved   — try/except around ``json.loads``: catches syntax errors but still accepts
   ``{"type": "tool_call"}`` with no name, which fails later, far from the cause.
3. Optimal    — normalise (strip fences), parse, then validate every field and raise one typed
   ``ModelOutputError`` with a precise message that can be fed back to the model. O(n) in the
   length of the output.

Hints
-----
- Strip a leading ```` ```json ```` line and a trailing ```` ``` ```` before parsing.
- ``isinstance(x, dict)`` checks are cheap; do them all before building the dataclass.
- ``copy.deepcopy`` the messages you record, or later mutation by the caller rewrites history.

Follow-ups
----------
- How would you mock a *streaming* model? (Yield the scripted text in chunks — see Ch. 42.)
- How do you keep scripts in sync with prompt changes? (Golden-transcript tests.)
"""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass, field
from typing import Callable


class ModelOutputError(ValueError):
    """Raised when model output cannot be interpreted as a tool call or final answer."""


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass(frozen=True)
class Final:
    content: str


_FENCE = re.compile(r"^```[a-zA-Z]*\s*\n(.*?)\n?```\s*$", re.DOTALL)


def strip_code_fence(text: str) -> str:
    """Remove a single surrounding Markdown code fence, if present."""
    text = text.strip()
    m = _FENCE.match(text)
    return m.group(1).strip() if m else text


def parse_model_output(raw: str) -> ToolCall | Final:
    text = strip_code_fence(raw)
    if not text.startswith("{"):
        return Final(text)  # plain prose is a final answer
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ModelOutputError(f"invalid JSON ({exc.msg}, char {exc.pos})") from None
    if not isinstance(obj, dict):
        raise ModelOutputError("top-level JSON must be an object")
    kind = obj.get("type")
    if kind == "final":
        content = obj.get("content")
        if not isinstance(content, str):
            raise ModelOutputError("final.content must be a string")
        return Final(content)
    if kind == "tool_call":
        name, call_id, args = obj.get("name"), obj.get("id", "call_0"), obj.get("arguments", {})
        if not isinstance(name, str) or not name:
            raise ModelOutputError("tool_call.name must be a non-empty string")
        if isinstance(args, str):  # some APIs send arguments as a JSON-encoded string
            try:
                args = json.loads(args) if args.strip() else {}
            except json.JSONDecodeError:
                raise ModelOutputError("tool_call.arguments is not valid JSON") from None
        if not isinstance(args, dict):
            raise ModelOutputError("tool_call.arguments must be an object")
        return ToolCall(str(call_id), name, args)
    raise ModelOutputError(f"unknown type: {kind!r}")


@dataclass
class ScriptedLLM:
    """Returns canned responses in order; records every prompt it receives."""

    responses: list[str]
    calls: list[list[dict]] = field(default_factory=list)

    def complete(self, messages: list[dict]) -> str:
        self.calls.append(copy.deepcopy(messages))
        if len(self.calls) > len(self.responses):
            raise RuntimeError(f"script exhausted after {len(self.responses)} responses")
        return self.responses[len(self.calls) - 1]


Rule = tuple[str, Callable[[re.Match], str]]


@dataclass
class RuleBasedLLM:
    """First regex (searched in the last message's content) that matches decides the reply."""

    rules: list[Rule]
    default: str = '{"type": "final", "content": "I am not sure."}'
    calls: int = 0

    def complete(self, messages: list[dict]) -> str:
        self.calls += 1
        last = messages[-1]["content"] if messages else ""
        for pattern, respond in self.rules:
            m = re.search(pattern, last, flags=re.IGNORECASE)
            if m:
                return respond(m)
        return self.default


def main() -> None:
    print("== parse_model_output")
    samples = [
        '{"type": "final", "content": "Paris is the capital of France."}',
        '```json\n{"type": "tool_call", "id": "call_7", "name": "get_weather", '
        '"arguments": "{\\"city\\": \\"Oslo\\"}"}\n```',
        "The answer is 42.",
        '{"type": "tool_call", "arguments": {}}',
        '{"type": "tool_call", "name": "f", "arguments": [1, 2]}',
        '{"type": "final", "content": "unterminated}',
        '{"type": "dance"}',
    ]
    for s in samples:
        try:
            print("  ok  ", parse_model_output(s))
        except ModelOutputError as exc:
            print("  ERR ", exc)

    print("== ScriptedLLM")
    llm = ScriptedLLM(['{"type": "final", "content": "one"}', "two"])
    msgs = [{"role": "user", "content": "hello"}]
    print("  reply 1:", parse_model_output(llm.complete(msgs)))
    msgs.append({"role": "user", "content": "again"})
    print("  reply 2:", parse_model_output(llm.complete(msgs)))
    print("  prompts recorded:", [len(c) for c in llm.calls])
    try:
        llm.complete(msgs)
    except RuntimeError as exc:
        print("  reply 3: RuntimeError:", exc)

    print("== RuleBasedLLM")
    bot = RuleBasedLLM(rules=[
        (r"weather in (\w+)", lambda m: json.dumps(
            {"type": "tool_call", "id": "c1", "name": "get_weather",
             "arguments": {"city": m.group(1).title()}})),
        (r"\bhello\b", lambda m: '{"type": "final", "content": "Hi there!"}'),
    ])
    for q in ["What's the weather in lisbon?", "hello bot", "What is love?"]:
        out = parse_model_output(bot.complete([{"role": "user", "content": q}]))
        print(f"  {q!r:32} -> {out}")


if __name__ == "__main__":
    main()
