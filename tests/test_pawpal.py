import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_due_time_with_frequency_greater_than_one_is_rejected():
    with pytest.raises(ValueError):
        Task(description="Feeding", duration=15, priority=1, due_time="08:00", frequency=3)


def test_due_times_length_must_match_frequency():
    with pytest.raises(ValueError):
        Task(description="Feeding", duration=15, priority=1, due_times=["08:00", "12:00"], frequency=3)


def test_due_times_matching_frequency_is_accepted_and_scheduled():
    pet = Pet(name="Fido", breed="Labrador")
    pet.add_task(
        Task(
            description="Feeding",
            duration=15,
            priority=1,
            due_times=["08:00", "12:00", "18:00"],
            frequency=3,
        )
    )

    schedule = _schedule_for(pet)

    start_times = sorted(o.start_time for o in schedule.occurrences)
    assert start_times == ["08:00", "12:00", "18:00"]


def test_mark_complete_changes_status():
    task = Task(description="Walk", duration=30, priority=1)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Fido", breed="Labrador")
    assert len(pet.tasks) == 0

    pet.add_task(Task(description="Feed", duration=10, priority=1))

    assert len(pet.tasks) == 1


def _schedule_for(pet):
    owner = Owner(name="Owner")
    owner.add_pet(pet)
    return Scheduler(owner).generate_pet_schedule(pet.pet_id)


def test_task_without_due_time_is_assigned_earliest_free_slot():
    pet = Pet(name="Fido", breed="Labrador")
    pet.add_task(Task(description="Vet call", duration=20, priority=2, due_time="08:00"))
    pet.add_task(Task(description="Feed", duration=20, priority=1))

    schedule = _schedule_for(pet)

    feed = next(o for o in schedule.occurrences if o.task.description == "Feed")
    assert feed.start_time == "08:20"


def test_high_frequency_task_gets_evenly_spread_slots():
    pet = Pet(name="Fido", breed="Labrador")
    pet.add_task(Task(description="Feeding", duration=15, priority=1, frequency=3))

    schedule = _schedule_for(pet)

    feedings = sorted(o.start_time for o in schedule.occurrences)
    assert len(feedings) == 3
    assert feedings[0] == "08:00"
    assert feedings[-1] < "20:00"
    assert feedings[0] < feedings[1] < feedings[2]


def test_auto_assigned_tasks_avoid_conflicts_across_pets():
    owner = Owner(name="Owner")
    dog = Pet(name="Dog", breed="Labrador")
    cat = Pet(name="Cat", breed="Tabby")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(description="Walk", duration=30, priority=2, due_time="08:00"))
    cat.add_task(Task(description="Groom", duration=30, priority=2, due_time="08:00"))
    cat.add_task(Task(description="Play", duration=20, priority=1))

    combined = Scheduler(owner).generate_combined_schedule()

    play = next(
        o
        for schedule in combined.pet_schedules.values()
        for o in schedule.occurrences
        if o.task.description == "Play"
    )
    assert play.start_time == "08:30"
    assert len(combined.conflicts) == 1
    assert {combined.conflicts[0].task_a.description, combined.conflicts[0].task_b.description} == {
        "Walk",
        "Groom",
    }


# --- Sorting correctness ---


def test_schedule_occurrences_are_returned_in_chronological_order():
    pet = Pet(name="Fido", breed="Labrador")
    pet.add_task(Task(description="Evening walk", duration=15, priority=1, due_time="18:00"))
    pet.add_task(Task(description="Morning feed", duration=15, priority=1, due_time="08:00"))
    pet.add_task(Task(description="Midday play", duration=15, priority=1, due_time="12:00"))

    schedule = _schedule_for(pet)

    start_times = [o.start_time for o in schedule.occurrences]
    assert start_times == sorted(start_times)
    assert start_times == ["08:00", "12:00", "18:00"]


def test_same_start_time_breaks_tie_by_priority_then_duration():
    pet = Pet(name="Fido", breed="Labrador")
    pet.add_task(Task(description="Low priority", duration=10, priority=1, due_time="09:00"))
    pet.add_task(Task(description="High priority", duration=20, priority=5, due_time="09:00"))

    schedule = _schedule_for(pet)

    descriptions = [o.task.description for o in schedule.occurrences]
    assert descriptions == ["High priority", "Low priority"]


# --- Conflict detection ---


def test_duplicate_due_times_are_flagged_as_a_conflict():
    owner = Owner(name="Owner")
    pet = Pet(name="Fido", breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task(description="Feed", duration=15, priority=1, due_time="09:00"))
    pet.add_task(Task(description="Medicate", duration=15, priority=1, due_time="09:00"))

    combined = Scheduler(owner).generate_combined_schedule()

    assert len(combined.conflicts) == 1
    assert combined.conflicts[0].start_a == combined.conflicts[0].start_b == "09:00"


def test_concurrent_ok_tasks_at_the_same_time_are_not_flagged():
    owner = Owner(name="Owner")
    pet = Pet(name="Fido", breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task(description="Feed", duration=15, priority=1, due_time="09:00", concurrent_ok=True))
    pet.add_task(Task(description="Medicate", duration=15, priority=1, due_time="09:00", concurrent_ok=True))

    combined = Scheduler(owner).generate_combined_schedule()

    assert combined.conflicts == []


def test_recurring_task_occurrences_overlapping_a_fixed_task_are_each_flagged():
    owner = Owner(name="Owner")
    pet = Pet(name="Fido", breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task(description="Fixed vet visit", duration=720, priority=1, due_time="08:00"))
    pet.add_task(Task(description="Feeding", duration=15, priority=1, frequency=3))

    combined = Scheduler(owner).generate_combined_schedule()

    assert len(combined.conflicts) == 3
    for conflict in combined.conflicts:
        assert {conflict.task_a.description, conflict.task_b.description} == {
            "Fixed vet visit",
            "Feeding",
        }


# --- Recurring task edge cases ---


def test_frequency_two_task_spreads_to_day_start_and_day_end():
    pet = Pet(name="Fido", breed="Labrador")
    pet.add_task(Task(description="Meds", duration=10, priority=1, frequency=2))

    schedule = _schedule_for(pet)

    start_times = sorted(o.start_time for o in schedule.occurrences)
    assert start_times == ["08:00", "19:50"]


def test_task_on_a_fully_booked_day_still_gets_a_fallback_time():
    pet = Pet(name="Fido", breed="Labrador")
    pet.add_task(Task(description="All day monitoring", duration=720, priority=1, due_time="08:00"))
    pet.add_task(Task(description="Extra walk", duration=10, priority=1))

    schedule = _schedule_for(pet)

    extra = next(o for o in schedule.occurrences if o.task.description == "Extra walk")
    assert extra.start_time == "08:00"


# --- Completed task handling ---


def test_completed_tasks_are_excluded_from_the_schedule_by_default():
    pet = Pet(name="Fido", breed="Labrador")
    task = Task(description="Feed", duration=10, priority=1, due_time="08:00")
    task.mark_complete()
    pet.add_task(task)

    schedule = _schedule_for(pet)

    assert schedule.occurrences == []


def test_include_completed_true_still_returns_completed_tasks():
    owner = Owner(name="Owner")
    pet = Pet(name="Fido", breed="Labrador")
    owner.add_pet(pet)
    task = Task(description="Feed", duration=10, priority=1, due_time="08:00")
    task.mark_complete()
    pet.add_task(task)

    schedule = Scheduler(owner).generate_pet_schedule(pet.pet_id, include_completed=True)

    assert len(schedule.occurrences) == 1
