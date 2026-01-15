# Using Claude Code in a CLI Pipeline

I started experimenting with Claude Code as a step in a CLI pipeline so I can keep prompts and outputs reproducible. The idea is to treat it like any other command: pass input on stdin, capture output to a file, and chain it with linting or formatting steps.

A basic pattern is to keep prompts in version control, then run them through a small shell script that feeds context from the repo. That makes it easier to review changes, compare runs, and keep the tool focused on a narrow task.

It feels similar to running a formatter or a test runner, but with the extra step of verifying the generated output before it lands in the branch.
