from pawpal_system import Pet, Task


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
