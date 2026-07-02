# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

While playing around with generating a schedule in the Streamlit app, I eventually noticed that tasks without a set due time did not have a time listed in the schedule. I thought this was weird when it was next to tasks that did have a set due time so I made a goal to implement a feature that would automatically assign times to tasks without given due times, so that when generating a schedule, all tasks would have a time to do it. To be practical, I specified that the automatically assigned time should always avoid conflict with tasks with set due times, be between normal awake hours of 8am to 10pm, and evenly distribute recurring tasks throughout the day (ex. Feeding task with 3 occurences should have times that are about breakfast, lunch, and dinner).

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

- Modified `pawpal_system.py`: added `ScheduledTask` (a task paired with a
  resolved `start_time`), and rewrote `Scheduler` with `_occurrences_conflict`,
  `_find_nearest_slot` (searches outward from an "ideal" minute for the closest
  conflict-free slot), and `assign_schedule` (splits tasks into fixed vs.
  flexible, places fixed tasks first, then slots flexible tasks in priority
  order — single slot via nearest-to-day-start, multiple slots spread evenly
  across the day via `DAY_START_MINUTES + i * span / (slot_count - 1)`).
  `find_conflicts` was updated to work off resolved start times.
- Updated `app.py` and `main.py` so the CLI/Streamlit schedule views display
  each task's resolved `start_time` and label auto-assigned (vs. fixed) times.
- Extended `tests/test_pawpal.py` with cases for: a flexible task getting
  auto-assigned the earliest open slot, a flexible task being nudged around an
  existing fixed booking, and a frequency > 1 task getting evenly spread
  occurrences.
- In a follow-up pass, the agent refactored its own first implementation:
  collapsed a separate `_find_earliest_slot` helper into `_find_nearest_slot`
  by calling it with `ideal=DAY_START_MINUTES` (since "closest to day start"
  and "earliest" are equivalent once every candidate is at or after that
  minute), replaced a hand-rolled expanding-radius search with a simpler
  `sorted(candidates, key=lambda c: (abs(c - ideal), c))`, and added a
  `Task.fixed_due_times()` helper to remove duplicated
  `due_time`/`due_times` branching in `assign_schedule` and `find_conflicts`.

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

- Manually verified the Streamlit UI shows a proper schedule for each pet, with each task getting assigned a time if not given already, and that the times are in order. Initially, the schedule placed recurring tasks with assigned times next to each other, even if they were in the wrong order of the overall schedule (ex. 8:20 Feeding, 19:00 Feeding, 9:00 Walk)
- Ran the full pytest suite after both the initial implementation and the
  refactor pass to confirm behavior didn't change.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
