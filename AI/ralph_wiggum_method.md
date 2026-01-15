# Ralph Wiggum Method for Coding Agents

Today I learned about the Ralph Wiggum method for prompting coding agents. The core idea is to treat each task as a clean slate so the agent does not accidentally blend context or assumptions from earlier work.

The original version stresses starting a brand new context for every task. The Claude Code plugin version is similar, but the key difference is making the reset explicit: always open a fresh context before the next request.

This helps avoid context bleed, reduces accidental coupling between tasks, and keeps responses focused on the immediate problem.
