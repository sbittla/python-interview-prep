"""
Exercise 04 — A ReAct Loop with Step Limits and Stop Conditions     [Tier: ★ Core]
Chapter 41 · Pattern: agent loop + termination guards · Target time: 35 min

Problem
-------
ReAct ("Reason + Act") agents interleave free-text reasoning with tool use in a plain-text format::

    Thought: I need Lisbon's population first.
    Action: lookup[population of Lisbon]
    Observation: 545000                <- written by *your* code, never by the model
    ...
    Thought: I can answer now.
    Final Answer: 545000

1. ``parse_react(text)`` returns ``("final", answer)`` or ``("action", tool, tool_input)``; text
   containing neither raises ``ReactParseError``. If a reply contains both an Action and a Final
   Answer, the Action wins only if it comes first (models sometimes "hallucinate" a final answer
   after an action — the observation was not real yet).
2. ``run_react(llm, tools, question, max_steps=5)`` builds the prompt (question + scratchpad of
   previous Thought/Action/Observation lines), calls ``llm.complete(prompt)``, runs the action and
   appends ``Observation: <result>``. Stop conditions, checked in this order each step:
   - ``final_answer``   — the model produced a Final Answer;
   - ``repeated_action`` — the same (tool, input) as the previous step (a loop that will not end);
   - ``parse_errors``   — two consecutive unparseable replies;
   - ``max_steps``      — step budget exhausted.
   Unknown tools and tool exceptions become observations (``Observation: error: ...``).
   Return ``ReactResult(answer, stop_reason, steps, scratchpad)``.

Examples
--------
>>> parse_react("Thought: easy\\nFinal Answer: 4")
('final', '4')
>>> parse_react("Thought: look it up\\nAction: lookup[Oslo]")
('action', 'lookup', 'Oslo')

Constraints
-----------
- Truncate the text after the first ``Action:`` line — anything the model wrote after it,
  including an invented ``Observation:``, is discarded.

Approach ladder
---------------
1. Brute force — loop until the model says "Final Answer": an infinite loop away from an outage.
2. Improved   — add ``max_steps``: terminates, but wastes the whole budget on an obvious loop.
3. Optimal    — several cheap guards (repeat detection, parse-error streak, step cap) that each
   name *why* the run stopped — essential for debugging and dashboards. O(steps) model calls.

Hints
-----
- A regex such as ``^Action:\\s*(\\w+)\\[(.*)\\]\\s*$`` with ``re.MULTILINE`` finds the action.
- Compare ``match.start()`` positions to decide which of Action/Final Answer came first.

Follow-ups
----------
- ReAct vs native function calling: ReAct is provider-agnostic and shows reasoning; native tool
  calls give structured arguments and fewer parse failures.
- How would you add a token budget as another stop condition?
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

_ACTION = re.compile(r"^Action:\s*(\w+)\[(.*)\]\s*$", re.MULTILINE)
_FINAL = re.compile(r"^Final Answer:\s*(.*)$", re.MULTILINE)


class ReactParseError(ValueError):
    pass


def parse_react(text: str) -> tuple:
    action, final = _ACTION.search(text), _FINAL.search(text)
    if action and (not final or action.start() < final.start()):
        return ("action", action.group(1), action.group(2).strip())
    if final:
        return ("final", final.group(1).strip())
    raise ReactParseError("expected 'Action: tool[input]' or 'Final Answer: ...'")


def thought_of(text: str) -> str:
    m = re.search(r"^Thought:\s*(.*)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


@dataclass
class ReactResult:
    answer: str | None
    stop_reason: str
    steps: int
    scratchpad: list[str] = field(default_factory=list)


PROMPT = """Answer the question. Use this format:
Thought: <reasoning>
Action: <tool>[<input>]   (tools: {tools})
or
Final Answer: <answer>

Question: {question}
{scratchpad}"""


def run_react(llm, tools: dict[str, Callable[[str], str]], question: str,
              max_steps: int = 5) -> ReactResult:
    scratchpad: list[str] = []
    last_action: tuple[str, str] | None = None
    parse_streak = 0
    for step in range(1, max_steps + 1):
        prompt = PROMPT.format(tools=", ".join(sorted(tools)), question=question,
                               scratchpad="\n".join(scratchpad))
        reply = llm.complete(prompt)
        try:
            parsed = parse_react(reply)
        except ReactParseError as exc:
            parse_streak += 1
            if parse_streak >= 2:
                return ReactResult(None, "parse_errors", step, scratchpad)
            scratchpad.append(f"Observation: error: {exc}")
            continue
        parse_streak = 0
        if parsed[0] == "final":
            scratchpad.append(f"Final Answer: {parsed[1]}")
            return ReactResult(parsed[1], "final_answer", step, scratchpad)
        _, tool, tool_input = parsed
        if last_action == (tool, tool_input):
            return ReactResult(None, "repeated_action", step, scratchpad)
        last_action = (tool, tool_input)
        scratchpad.append(f"Thought: {thought_of(reply)}")
        scratchpad.append(f"Action: {tool}[{tool_input}]")
        if tool not in tools:
            observation = f"error: unknown tool {tool!r}"
        else:
            try:
                observation = str(tools[tool](tool_input))
            except Exception as exc:
                observation = f"error: {type(exc).__name__}: {exc}"
        scratchpad.append(f"Observation: {observation}")
    return ReactResult(None, "max_steps", max_steps, scratchpad)


# ---- tools and scripted models -----------------------------------------------------------------
FACTS = {"population of lisbon": "545000", "population of porto": "232000"}


def lookup(query: str) -> str:
    key = query.lower().strip()
    if key not in FACTS:
        raise KeyError(f"no fact for {query!r}")
    return FACTS[key]


def calculate(expression: str) -> str:
    # Demo-grade guard; Exercise 10 replaces eval with a real AST-based evaluator.
    if not re.fullmatch(r"[\d\s+\-*/().]+", expression) or "**" in expression:
        raise ValueError("only + - * / and parentheses are allowed")
    return str(eval(expression, {"__builtins__": {}}))  # input restricted by the regex above


class Scripted:
    def __init__(self, replies: list[str]) -> None:
        self.replies, self.prompts = replies, []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.replies[min(len(self.prompts), len(self.replies)) - 1]


def main() -> None:
    tools = {"lookup": lookup, "calculate": calculate}
    scenarios = {
        "happy path": Scripted([
            "Thought: I need Lisbon's population.\nAction: lookup[population of Lisbon]\n"
            "Observation: 999 (hallucinated - must be ignored)",
            "Thought: Now Porto.\nAction: lookup[population of Porto]",
            "Thought: Add them.\nAction: calculate[545000 + 232000]",
            "Thought: Done.\nFinal Answer: 777000",
        ]),
        "recovers from tool error": Scripted([
            "Thought: Look it up.\nAction: lookup[Lisbon]",
            "Thought: Wrong key, be specific.\nAction: lookup[population of Lisbon]",
            "Final Answer: 545000",
        ]),
        "stuck in a loop": Scripted([
            "Thought: Search.\nAction: lookup[population of Porto]",
            "Thought: Search again.\nAction: lookup[population of Porto]",
        ]),
        "never parses": Scripted(["I think the answer might be big.", "Still thinking..."]),
        "rambles forever": Scripted([f"Thought: try {i}.\nAction: calculate[{i} + {i}]"
                                     for i in range(1, 10)]),
    }
    for name, llm in scenarios.items():
        res = run_react(llm, tools, "What is the combined population of Lisbon and Porto?",
                        max_steps=4)
        print(f"== {name}: stop={res.stop_reason} steps={res.steps} answer={res.answer}")
        for line in res.scratchpad:
            print("   ", line)
    print("== last prompt sent in the happy path:")
    print(scenarios["happy path"].prompts[-1])


if __name__ == "__main__":
    main()
