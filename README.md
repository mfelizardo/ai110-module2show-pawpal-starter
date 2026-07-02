# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

```
Today's Schedule for Jordan's pets

-- Biscuit (Golden Retriever) --
  08:00  Morning walk    (priority=2, 30 min)
  12:00  Feeding         (priority=3, 10 min)
  18:00  Evening walk    (priority=1, 20 min)

-- Mochi (Tabby Cat) --
  08:05  Litter box      (priority=1, 15 min)
  08:10  Grooming        (priority=1, 15 min)
  12:00  Feeding         (priority=3, 10 min)

Conflicts detected:
  Biscuit's 'Morning walk' (08:00) overlaps with Mochi's 'Litter box' (08:05)
  Biscuit's 'Morning walk' (08:00) overlaps with Mochi's 'Grooming' (08:10)
  Mochi's 'Litter box' (08:05) overlaps with Mochi's 'Grooming' (08:10)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

```
============================================================================================================ test session starts =============================================================================================================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Mikey\Desktop\CodePath Courses\AI Engineering\Project2\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 17 items                                                                                                                                                                                                                            

tests\test_pawpal.py .................                                                                                                                                                                                                  [100%]

============================================================================================================= 17 passed in 0.07s =============================================================================================================
```

### What the tests cover

`tests/test_pawpal.py` exercises the scheduling engine end-to-end, grouped by behavior:

- **Task validation** — `due_time` combined with `frequency > 1` is rejected, and `due_times` must have exactly one entry per occurrence.
- **Sorting correctness** — a mix of due times comes back in chronological order, and occurrences with the same start time break ties by descending priority, then duration.
- **Conflict detection** — identical/overlapping due times are flagged as conflicts, `concurrent_ok` tasks are exempt from those flags, and conflicts are detected both across pets and across a single recurring task's occurrences.
- **Recurring tasks** — `frequency > 1` tasks are spread evenly across the day (including the `frequency = 2` boundary landing exactly at day start/end), and fixed `due_times` matching the frequency are honored.
- **Auto-assignment & fallback** — flexible tasks take the earliest free slot, avoid conflicts across pets, and still get a (non-crashing) fallback time when the day is fully booked.
- **Completed task handling** — completed tasks are excluded from a generated schedule by default, but included when `include_completed=True`.
- **Basic model behavior** — `mark_complete`/`add_task` update state as expected.

### Confidence Level: 5/5 stars

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.assign_schedule` | Tasks with a fixed `due_time` keep it; flexible (no due_time) tasks are sorted by descending `priority` before being assigned a slot. Final output is ordered by `(start_time, -priority, duration)`. |
| Filtering | `Scheduler.filter_pending` | Excludes completed tasks (`Task.completed`) from scheduling. There's no "skip if time runs out" — if the 08:00–20:00 day fills up, `_find_nearest_slot` returns `None` and the task falls back to a default slot rather than being dropped. |
| Conflict handling | `Scheduler._occurrences_conflict`, `Scheduler.find_conflicts` | Two occurrences conflict if their time windows overlap, unless both tasks are marked `concurrent_ok` (e.g. tasks that can happen alongside anything else). `find_conflicts` checks every pair of occurrences across all pets and returns a `ScheduleConflict` for each overlap. |
| Recurring tasks | `Task.frequency`, `Task.due_times`, `Scheduler.assign_schedule` | A flexible task (no fixed time) with `frequency > 1` gets that many occurrences spread evenly across the day (`DAY_START_MINUTES`–`DAY_END_MINUTES`), nudged via `_find_nearest_slot` to the nearest free time if its ideal slot conflicts with something else. A task that *does* need fixed times for each occurrence must set `due_times` (one entry per occurrence) instead of the singular `due_time` — `Task.__post_init__` raises `ValueError` if `due_time` is combined with `frequency > 1`, or if `due_times` doesn't have exactly `frequency` entries. |

## 📸 Demo Walkthrough

### Main UI features

The Streamlit app (`app.py`) is organized into four sections, top to bottom:

- **Owner** — a single text input for the owner's name, editable at any time.
- **Pets** — a form to add a new pet (name + breed/species), and a dropdown to switch between existing pets. An expander lets you edit a pet's name/breed in place.
- **Tasks** — for the currently selected pet, a form to add a task (description, duration, priority, optional fixed due time(s), frequency per day, and whether it's okay for the task to overlap another pet's task). Existing tasks are listed as expanders where you can mark a task complete/incomplete, edit any field, or delete the task.
- **Schedule** — a "Generate schedule" button (with an "Include completed tasks" toggle) that runs the `Scheduler` and displays each pet's ordered task list plus any conflict warnings.

All state (owner, pets, tasks) is persisted to `pawpal_data.json` after every interaction, so a browser refresh picks up right where you left off.

### Example workflow

This mirrors the scenario printed by `python main.py` (see the CLI output below), built up one step at a time through the UI:

1. Open the app and set the owner name to "Jordan" (the default).
2. Add a pet, **Biscuit (Golden Retriever)**, via the "Add a pet" form — it becomes the selected pet automatically.
3. With Biscuit selected, add three tasks:
   - "Morning walk", 30 min, Medium priority, fixed due time 08:00.
   - "Feeding", 10 min, High priority, fixed due time 12:00, "Okay to happen at the same time" checked (`concurrent_ok`).
   - "Evening walk", 20 min, Low priority, fixed due time 18:00.
4. Add a second pet, **Mochi (Tabby Cat)**, and switch the pet selector to her.
5. With Mochi selected, add three tasks:
   - "Litter box", 15 min, Low priority, fixed due time 08:05.
   - "Grooming", 15 min, Low priority, fixed due time 08:10.
   - "Feeding", 10 min, High priority, fixed due time 12:00, `concurrent_ok` checked.
6. Click **Generate schedule**. Each pet's tasks appear sorted by time (08:00, 12:00, 18:00 for Biscuit; 08:05, 08:10, 12:00 for Mochi), and a conflict warning lists every overlapping pair in the 08:00–08:25 morning cluster — Biscuit's 08:00 walk overlaps Mochi's 08:05 litter box and 08:10 grooming, and Mochi's litter box overlaps her own grooming. The two `concurrent_ok` Feeding tasks share the exact same 12:00 slot but never appear in the conflict list, since both opted in to happening at the same time.
7. Check "Completed" on Biscuit's morning walk and regenerate the schedule — it drops out of Biscuit's list. Toggle "Include completed tasks" to bring it back.

### Key Scheduler behaviors shown

- **Sorting** — tasks with a fixed `due_time` keep it; flexible tasks (no due time) are auto-assigned the earliest open slot between 08:00–20:00. The final list for each pet is ordered by start time, then descending priority, then duration for same-time ties.
- **Conflict warnings** — any two occurrences (same pet or across pets) whose time windows overlap are flagged, unless both tasks are marked `concurrent_ok` (e.g. the two 12:00 feedings above).
- **Recurring tasks** — a task with `frequency > 1` either gets evenly spaced auto-assigned slots across the day, or, if it needs specific times, one `due_times` entry per occurrence.
- **Completed task filtering** — completed tasks are excluded from the generated schedule by default.

### Sample CLI output (`python main.py`)

```
Today's Schedule for Jordan's pets

-- Biscuit (Golden Retriever) --
  08:00  Morning walk    (priority=2, 30 min)
  12:00  Feeding         (priority=3, 10 min)
  18:00  Evening walk    (priority=1, 20 min)

-- Mochi (Tabby Cat) --
  08:05  Litter box      (priority=1, 15 min)
  08:10  Grooming        (priority=1, 15 min)
  12:00  Feeding         (priority=3, 10 min)

Conflicts detected:
  Biscuit's 'Morning walk' (08:00) overlaps with Mochi's 'Litter box' (08:05)
  Biscuit's 'Morning walk' (08:00) overlaps with Mochi's 'Grooming' (08:10)
  Mochi's 'Litter box' (08:05) overlaps with Mochi's 'Grooming' (08:10)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
