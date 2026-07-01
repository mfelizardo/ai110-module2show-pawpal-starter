from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Jordan")

biscuit = Pet("Biscuit", "Golden Retriever")
mochi = Pet("Mochi", "Tabby Cat")
owner.add_pet(biscuit)
owner.add_pet(mochi)

owner.add_task(
    biscuit.pet_id,
    Task("Morning walk", duration=30, priority=2, due_time="08:00"),
)
owner.add_task(
    biscuit.pet_id,
    Task("Feeding", duration=10, priority=3, due_time="08:15", concurrent_ok=True),
)
owner.add_task(
    biscuit.pet_id,
    Task("Evening walk", duration=20, priority=1, due_time="18:00"),
)

owner.add_task(
    mochi.pet_id,
    Task("Litter box", duration=15, priority=1, due_time="08:05"),
)
owner.add_task(
    mochi.pet_id,
    Task("Feeding", duration=10, priority=3, due_time="08:15", concurrent_ok=True),
)
owner.add_task(
    mochi.pet_id,
    Task("Grooming", duration=15, priority=1, due_time="08:10"),
)

scheduler = Scheduler(owner)
combined = scheduler.generate_combined_schedule()

print(f"Today's Schedule for {owner.name}'s pets\n")

for pet_schedule in combined.pet_schedules.values():
    print(f"-- {pet_schedule.pet.name} ({pet_schedule.pet.breed}) --")
    for task in pet_schedule.ordered_tasks:
        print(f"  {task.due_time}  {task.description:<15} (priority={task.priority}, {task.duration} min)")
    print()

if combined.conflicts:
    print("Conflicts detected:")
    for conflict in combined.conflicts:
        print(
            f"  {conflict.pet_a.name}'s '{conflict.task_a.description}' overlaps "
            f"with {conflict.pet_b.name}'s '{conflict.task_b.description}'"
        )
else:
    print("No conflicts detected.")
