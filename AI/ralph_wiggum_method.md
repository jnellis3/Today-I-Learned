# Ralph Wiggum Method for Coding Agents

Today I learned about the Ralph Wiggum method for prompting coding agents. The idea is simple: start each task as if the agent knows nothing about prior work unless you explicitly reintroduce it.

## What it is

The method treats each request as a clean slate. You open a fresh context, restate the goal, and provide only the relevant inputs for that task. It is a deliberate reset so the agent does not blend assumptions from a previous conversation into the next one.

## How to use it

1. Start a new chat or session for each task.
2. Provide a clear goal, constraints, and any files or commands you want used.
3. If context from a prior task matters, explicitly paste it in (or link to the file) rather than assuming the agent remembers.
4. Close the loop with a short summary or checklist so the next task can reference it directly.

## Why it helps

- Prevents context bleed and hidden assumptions.
- Keeps solutions narrow and focused on the current task.
- Makes reviews easier because the prompt captures the real requirements.

## Tradeoffs

The reset means you must re-provide context when it matters, which can feel repetitive. The payoff is fewer accidental regressions and clearer task boundaries.
