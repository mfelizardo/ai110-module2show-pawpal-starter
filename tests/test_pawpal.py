from pawpal_system import Owner, Pet, Scheduler, Task


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
