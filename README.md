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
  08:15  Feeding         (priority=3, 10 min)
  08:00  Morning walk    (priority=2, 30 min)
  18:00  Evening walk    (priority=1, 20 min)

-- Mochi (Tabby Cat) --
  08:15  Feeding         (priority=3, 10 min)
  08:05  Litter box      (priority=1, 15 min)
  08:10  Grooming        (priority=1, 15 min)

Conflicts detected:
  Biscuit's 'Feeding' overlaps with Mochi's 'Litter box'
  Biscuit's 'Feeding' overlaps with Mochi's 'Grooming'
  Biscuit's 'Morning walk' overlaps with Mochi's 'Feeding'
  Biscuit's 'Morning walk' overlaps with Mochi's 'Litter box'
  Biscuit's 'Morning walk' overlaps with Mochi's 'Grooming'
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

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.assign_schedule` | Tasks with a fixed `due_time` keep it; flexible (no due_time) tasks are sorted by descending `priority` before being assigned a slot. Final output is ordered by `(start_time, -priority, duration)`. |
| Filtering | `Scheduler.filter_pending` | Excludes completed tasks (`Task.completed`) from scheduling. There's no "skip if time runs out" — if the 08:00–20:00 day fills up, `_find_earliest_slot`/`_find_nearest_slot` return `None` and the task falls back to a default slot rather than being dropped. |
| Conflict handling | `Scheduler._occurrences_conflict`, `Scheduler.find_conflicts` | Two occurrences conflict if their time windows overlap, unless both tasks are marked `concurrent_ok` (e.g. tasks that can happen alongside anything else). `find_conflicts` checks every pair of occurrences across all pets and returns a `ScheduleConflict` for each overlap. |
| Recurring tasks | `Task.frequency`, `Task.due_times`, `Scheduler.assign_schedule` | A flexible task (no fixed time) with `frequency > 1` gets that many occurrences spread evenly across the day (`DAY_START_MINUTES`–`DAY_END_MINUTES`), nudged via `_find_nearest_slot` to the nearest free time if its ideal slot conflicts with something else. A task that *does* need fixed times for each occurrence must set `due_times` (one entry per occurrence) instead of the singular `due_time` — `Task.__post_init__` raises `ValueError` if `due_time` is combined with `frequency > 1`, or if `due_times` doesn't have exactly `frequency` entries. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
