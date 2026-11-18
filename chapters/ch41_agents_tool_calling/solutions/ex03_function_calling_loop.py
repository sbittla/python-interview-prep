"""
Exercise 03 — The Function-Calling Loop                             [Tier: ★ Core]
Chapter 41 · Pattern: agent loop (model -> tool -> model) · Target time: 30 min

Problem
-------
Implement ``run_tool_loop(llm, registry, user_message, max_turns=6)``, the loop at the heart of
every tool-using assistant:

1. Start the transcript with a system message and the user's message.
2. Ask the model (``llm.complete(messages, tool_schemas)``) for its next move.
3. Append the raw reply as an ``assistant`` message and parse it (Exercise 01's parser).
   - A ``Final`` ends the loop with ``stop_reason="final"``.
   - A ``ToolCall`` is dispatched through the registry (Exercise 02). The result — or the error,
     as data — is appended as a ``tool`` message carrying the ``tool_call_id`` and the tool name.
   - Unparseable output is answered with a corrective ``user`` message; the loop continues.
4. After ``max_turns`` model calls without a final answer, stop with ``stop_reason="max_turns"``.

Tool failures must never crash the loop: they become ``{"ok": false, "error": "..."}`` payloads so
the model can recover. Return a ``LoopResult(answer, messages, tool_log, turns, stop_reason)``.

Examples
--------
>>> result = run_tool_loop(WeatherModel(), build_registry(), "What's the weather in Oslo?")
>>> result.stop_reason, result.answer
('final', 'It is 4.0 C and sleet in Oslo.')

Constraints
-----------
- ``max_turns`` bounds model calls (cost and latency), not tool calls.
- Tool payloads are serialised with ``json.dumps(..., sort_keys=True)`` for determinism.

Approach ladder
---------------
1. Brute force — one model call, execute the tool, paste the result into the answer yourself:
   handles exactly one tool call and no multi-step reasoning.
2. Improved   — ``while True`` loop: supports chains of calls, but a confused model loops (and
   bills) forever, and one tool exception kills the request.
3. Optimal    — bounded loop, errors as observations, transcript kept as the single source of
   state. O(T) model calls for T turns; transcript grows O(T) messages.

Hints
-----
- Keep the *raw* assistant text in the transcript; the provider needs it on the next call.
- Catch ``ToolError`` (bad name/arguments) and any other ``Exception`` from the tool separately so
  the error message says which kind it was.

Follow-ups
----------
- Parallel tool calls: the model returns several calls in one turn; run them concurrently and
  append one ``tool`` message per call id.
- How do you stop a model that keeps calling the same tool? (Ex. 04: repeated-action detection.)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from ex01_mock_llm import Final, ModelOutputError, parse_model_output
from ex02_tool_schema import ToolError, ToolRegistry

SYSTEM_PROMPT = ("You are a weather assistant. Call tools by replying with JSON "
                 '{"type": "tool_call", ...}; answer with {"type": "final", ...}.')

WEATHER = {"Oslo": (4.0, "sleet"), "Lisbon": (19.0, "sunny"), "Cairo": (31.0, "clear")}


def get_weather(city: str) -> dict:
    """Current temperature (Celsius) and conditions for a city.

    Args:
        city: City name.
    """
    if city not in WEATHER:
        raise LookupError(f"no weather station for {city!r}")
    temp, cond = WEATHER[city]
    return {"city": city, "temp_c": temp, "conditions": cond}


def build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(get_weather)
    return reg


@dataclass
class WeatherModel:
    """A mock *policy*: reads the transcript and decides the next move deterministically.

    It stands in for an LLM. Real models decide using learned behaviour; this one uses rules, which
    is exactly what makes the agent loop around it testable.
    """

    calls: int = 0

    def complete(self, messages: list[dict], tools: list[dict]) -> str:
        self.calls += 1
        question = next(m["content"] for m in reversed(messages) if m["role"] == "user")
        cities = [c for c in re.findall(r"\b([A-Z][a-z]+)\b", question) if c not in {"What", "Is"}]
        seen = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
        if len(seen) < len(cities):  # still need data for the next city
            city = cities[len(seen)]
            return json.dumps({"type": "tool_call", "id": f"call_{self.calls}",
                               "name": "get_weather", "arguments": {"city": city}})
        failed = [c for c, r in zip(cities, seen) if not r["ok"]]
        if failed:
            text = f"Sorry, I could not get the weather for {', '.join(failed)}."
        elif len(cities) == 1:
            r = seen[0]["result"]
            text = f"It is {r['temp_c']} C and {r['conditions']} in {r['city']}."
        else:
            a, b = seen[0]["result"], seen[1]["result"]
            warm, cold = (a, b) if a["temp_c"] >= b["temp_c"] else (b, a)
            text = (f"{warm['city']} is warmer than {cold['city']} by "
                    f"{warm['temp_c'] - cold['temp_c']:.1f} C.")
        return json.dumps({"type": "final", "content": text})


@dataclass
class LoopResult:
    answer: str | None
    messages: list[dict]
    tool_log: list[tuple[str, dict, bool]] = field(default_factory=list)
    turns: int = 0
    stop_reason: str = ""


def run_tool_loop(llm, registry: ToolRegistry, user_message: str, *,
                  system: str = SYSTEM_PROMPT, max_turns: int = 6) -> LoopResult:
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user_message}]
    tool_log: list[tuple[str, dict, bool]] = []
    for turn in range(1, max_turns + 1):
        raw = llm.complete(messages, registry.schemas())
        messages.append({"role": "assistant", "content": raw})
        try:
            out = parse_model_output(raw)
        except ModelOutputError as exc:
            messages.append({"role": "user",
                             "content": f"Your last reply was invalid ({exc}). Reply with valid JSON."})
            continue
        if isinstance(out, Final):
            return LoopResult(out.content, messages, tool_log, turn, "final")
        try:
            payload = {"ok": True, "result": registry.call(out.name, out.arguments)}
        except ToolError as exc:  # unknown tool / bad arguments: the model's fault
            payload = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        except Exception as exc:  # the tool itself failed
            payload = {"ok": False, "error": f"tool raised {type(exc).__name__}: {exc}"}
        tool_log.append((out.name, out.arguments, payload["ok"]))
        messages.append({"role": "tool", "tool_call_id": out.id, "name": out.name,
                         "content": json.dumps(payload, sort_keys=True)})
    return LoopResult(None, messages, tool_log, max_turns, "max_turns")


class StubbornModel:
    """Misbehaving mock: always calls the same tool, never answers."""

    def complete(self, messages: list[dict], tools: list[dict]) -> str:
        return '{"type": "tool_call", "id": "c", "name": "get_weather", "arguments": {"city": "Oslo"}}'


def print_transcript(messages: list[dict]) -> None:
    for m in messages:
        extra = f" [{m['name']} id={m['tool_call_id']}]" if m["role"] == "tool" else ""
        content = m["content"] if len(m["content"]) <= 90 else m["content"][:87] + "..."
        print(f"    {m['role']:9}{extra}: {content}")


def main() -> None:
    registry = build_registry()
    for question in ["What's the weather in Oslo?",
                     "Is it warmer in Lisbon or Cairo?",
                     "What's the weather in Atlantis?"]:
        res = run_tool_loop(WeatherModel(), registry, question)
        print(f"Q: {question}")
        print(f"  stop={res.stop_reason} turns={res.turns} tools={res.tool_log}")
        print(f"  A: {res.answer}")
    print("Full transcript for the comparison question:")
    print_transcript(run_tool_loop(WeatherModel(), registry, "Is it warmer in Lisbon or Cairo?").messages)
    res = run_tool_loop(StubbornModel(), registry, "Weather?", max_turns=3)
    print(f"Stubborn model: stop={res.stop_reason} turns={res.turns} answer={res.answer} "
          f"tool calls={len(res.tool_log)}")


if __name__ == "__main__":
    main()
