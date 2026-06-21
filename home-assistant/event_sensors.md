# Home Assistant Automations Work Best When Sensors Represent Events

A useful mental model for Home Assistant is that automations are easier to reason about when sensors represent a real event instead of a vague condition.

A vibration sensor on a washing machine is a good example. The raw signal is not really "laundry is done." It is closer to "the machine is currently vibrating." That is useful, but it is not the event I actually care about.

The event I care about is usually a transition:

- the washer started running
- the washer stopped running after previously being active
- the washer has been idle long enough that the cycle is probably done
- the laundry has not been moved yet

Those are much more automation-friendly than a single fuzzy state like `washer_vibrating`.

The better pattern is to turn raw sensor noise into a small state machine:

```text
idle -> running -> maybe_done -> done -> emptied
```

Then automations can subscribe to meaningful events instead of trying to infer intent from the raw sensor every time.

For example, instead of writing an automation that says:

```text
If vibration is off, notify me that laundry is done.
```

I want something closer to:

```text
If the washer was running, and then vibration has been low for 5 minutes, mark the washer done and notify me once.
```

That distinction matters because sensors are noisy. A washer can pause mid-cycle. A dishwasher can stop vibrating during a soak phase. A vibration sensor can miss a few samples. If the automation only looks at the current reading, it will fire at the wrong time.

State machines give the automation memory. They let me encode context like "this was running earlier" and "this has been quiet long enough to count as finished." That is the difference between an alert that feels smart and an alert that feels random.

This also makes the rest of the system cleaner. Once I have a reliable `washer_done` event, I can reuse it anywhere:

- send a phone notification
- announce it on a speaker
- turn on a laundry room light
- add a Todoist task
- suppress duplicate notifications until the door is opened or the load is cleared

The main TIL: the best Home Assistant automations usually do not come from adding more conditions to one giant rule. They come from creating better intermediate signals.

Raw sensors should describe what they directly observe. Helper entities, timers, template sensors, and automations can translate that raw observation into the real-world event I care about.

That makes the system less fragile and easier to extend.
