import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _new_id() -> str:
    return uuid.uuid4().hex[:8]


def _time_to_minutes(due_time: str) -> int:
    hours, minutes = due_time.split(":")
    return int(hours) * 60 + int(minutes)


def _minutes_to_time(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


DAY_START_MINUTES = _time_to_minutes("08:00")
DAY_END_MINUTES = _time_to_minutes("20:00")


@dataclass
class Task:
    description: str
    duration: int
    priority: int
    due_time: Optional[str] = None
    due_times: Optional[List[str]] = None
    frequency: int = 0
    completed: bool = False
    concurrent_ok: bool = False
    task_id: str = field(default_factory=_new_id)

    def __post_init__(self) -> None:
        slot_count = max(1, self.frequency)
        if self.due_time is not None and slot_count > 1:
            raise ValueError(
                "A task with frequency > 1 needs one due_time per occurrence; "
                "set due_times instead of due_time."
            )
        if self.due_times is not None and len(self.due_times) != slot_count:
            raise ValueError(
                f"due_times must have exactly {slot_count} entries to match frequency, "
                f"got {len(self.due_times)}."
            )

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def fixed_due_times(self) -> List[str]:
        """Return this task's fixed due times, or an empty list if it has none."""
        if self.due_times is not None:
            return self.due_times
        if self.due_time is not None:
            return [self.due_time]
        return []


@dataclass
class ScheduledTask:
    """A task placed at a specific time, whether from its own due_time or auto-assigned by the Scheduler."""

    task: Task
    start_time: str

    def time_window(self) -> tuple:
        """Return the (start, end) minute range this occurrence occupies."""
        start = _time_to_minutes(self.start_time)
        return start, start + self.task.duration


@dataclass
class Pet:
    name: str
    breed: str
    tasks: List[Task] = field(default_factory=list)
    pet_id: str = field(default_factory=_new_id)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def list_tasks(self) -> List[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Return the task with the given id, or None if not found."""
        return next((t for t in self.tasks if t.task_id == task_id), None)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]


@dataclass
class Schedule:
    pet: Pet
    occurrences: List[ScheduledTask] = field(default_factory=list)


@dataclass
class ScheduleConflict:
    pet_a: Pet
    task_a: Task
    pet_b: Pet
    task_b: Task
    start_a: str
    start_b: str


@dataclass
class CombinedSchedule:
    owner: "Owner"
    pet_schedules: Dict[str, Schedule] = field(default_factory=dict)
    conflicts: List[ScheduleConflict] = field(default_factory=list)


@dataclass
class Owner:
    name: str
    pets: Dict[str, Pet] = field(default_factory=dict)

    def edit_name(self, new_name: str) -> None:
        """Update the owner's name."""
        self.name = new_name

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets[pet.pet_id] = pet

    def list_pets(self) -> List[Pet]:
        """Return a list of all pets owned by this owner."""
        return list(self.pets.values())

    def get_pet(self, pet_id: str) -> Pet:
        """Return the pet with the given id, raising KeyError if not found."""
        pet = self.pets.get(pet_id)
        if pet is None:
            raise KeyError(f"No pet with id {pet_id!r}")
        return pet

    def edit_basic_pet_info(
        self,
        pet_id: str,
        new_name: Optional[str] = None,
        new_breed: Optional[str] = None,
    ) -> None:
        """Update the name and/or breed of the pet with the given id."""
        pet = self.get_pet(pet_id)
        if new_name is not None:
            pet.name = new_name
        if new_breed is not None:
            pet.breed = new_breed

    def add_task(self, pet_id: str, task: Task) -> None:
        """Add a task to the pet with the given id."""
        self.get_pet(pet_id).add_task(task)

    def edit_task(self, pet_id: str, task_id: str, new_task: Task) -> None:
        """Replace the given pet's task with new_task, keeping the original task id."""
        pet = self.get_pet(pet_id)
        for index, task in enumerate(pet.tasks):
            if task.task_id == task_id:
                new_task.task_id = task_id
                pet.tasks[index] = new_task
                return
        raise KeyError(f"No task with id {task_id!r} for pet {pet_id!r}")

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets.values() for task in pet.tasks]

    def generate_daily_schedule(self, pet_id: str) -> Schedule:
        """Generate the ordered daily schedule for the given pet."""
        return Scheduler(self).generate_pet_schedule(pet_id)


@dataclass
class Scheduler:
    owner: Owner

    def filter_pending(self, tasks: List[Task]) -> List[Task]:
        """Return only the tasks that are not yet completed."""
        return [t for t in tasks if not t.completed]

    def _occurrences_conflict(self, task_a: Task, start_a: int, task_b: Task, start_b: int) -> bool:
        """Return True if the two windows overlap and the tasks aren't mutually okay with that."""
        if task_a.concurrent_ok and task_b.concurrent_ok:
            return False
        end_a = start_a + task_a.duration
        end_b = start_b + task_b.duration
        return start_a < end_b and start_b < end_a

    def _find_nearest_slot(self, task: Task, ideal: int, occupied: List[tuple]) -> Optional[int]:
        """Return the start minute closest to ideal (within the day) that doesn't conflict with occupied.

        Passing ideal=DAY_START_MINUTES finds the earliest free slot, since every
        candidate is then at or after ideal and "closest" reduces to "earliest".
        """
        ideal = max(DAY_START_MINUTES, min(ideal, DAY_END_MINUTES - task.duration))
        candidates = range(DAY_START_MINUTES, DAY_END_MINUTES - task.duration + 1)
        for candidate in sorted(candidates, key=lambda c: (abs(c - ideal), c)):
            if not any(self._occurrences_conflict(task, candidate, o_task, o_start) for o_task, o_start in occupied):
                return candidate
        return None

    def assign_schedule(self, tasks: List[Task]) -> List[ScheduledTask]:
        """Resolve a start time for every task.

        Tasks with a fixed due_time (or, for frequency > 1, one due_time per
        occurrence via due_times) keep those times. Tasks without any fixed time
        are auto-assigned the earliest free slot between 08:00-20:00; if their
        frequency is greater than 1, that many slots are spread evenly across the
        day instead, nudged to the nearest free time when their ideal slot
        conflicts with something else.
        """
        fixed = [t for t in tasks if t.fixed_due_times()]
        flexible = sorted((t for t in tasks if not t.fixed_due_times()), key=lambda t: -t.priority)

        fixed_times: List[tuple] = [(t, due_time) for t in fixed for due_time in t.fixed_due_times()]
        occupied: List[tuple] = [(t, _time_to_minutes(due_time)) for t, due_time in fixed_times]
        occurrences: List[ScheduledTask] = [
            ScheduledTask(task=t, start_time=due_time) for t, due_time in fixed_times
        ]

        for task in flexible:
            slot_count = max(1, task.frequency)
            if slot_count == 1:
                start = self._find_nearest_slot(task, DAY_START_MINUTES, occupied)
                if start is None:
                    start = DAY_START_MINUTES
                occupied.append((task, start))
                occurrences.append(ScheduledTask(task=task, start_time=_minutes_to_time(start)))
            else:
                span = DAY_END_MINUTES - DAY_START_MINUTES - task.duration
                for i in range(slot_count):
                    ideal = DAY_START_MINUTES + round(i * span / (slot_count - 1))
                    start = self._find_nearest_slot(task, ideal, occupied)
                    if start is None:
                        start = ideal
                    occupied.append((task, start))
                    occurrences.append(ScheduledTask(task=task, start_time=_minutes_to_time(start)))

        return sorted(occurrences, key=lambda o: (o.start_time, -o.task.priority, o.task.duration))

    def find_conflicts(self, pet_occurrences: List[tuple]) -> List[ScheduleConflict]:
        """Flag overlapping time windows between any two occurrences (same pet or different pets), unless both are concurrent_ok."""
        conflicts: List[ScheduleConflict] = []
        for i, (pet_a, occurrence_a) in enumerate(pet_occurrences):
            start_a, _ = occurrence_a.time_window()
            for pet_b, occurrence_b in pet_occurrences[i + 1 :]:
                start_b, _ = occurrence_b.time_window()
                if self._occurrences_conflict(occurrence_a.task, start_a, occurrence_b.task, start_b):
                    conflicts.append(
                        ScheduleConflict(
                            pet_a,
                            occurrence_a.task,
                            pet_b,
                            occurrence_b.task,
                            occurrence_a.start_time,
                            occurrence_b.start_time,
                        )
                    )
        return conflicts

    def generate_pet_schedule(self, pet_id: str, include_completed: bool = False) -> Schedule:
        """Build an ordered schedule of one pet's tasks, auto-assigning times where needed."""
        pet = self.owner.get_pet(pet_id)
        tasks = pet.list_tasks() if include_completed else self.filter_pending(pet.list_tasks())
        return Schedule(pet=pet, occurrences=self.assign_schedule(tasks))

    def generate_combined_schedule(self, include_completed: bool = False) -> CombinedSchedule:
        """Build per-pet schedules for all pets, auto-assigning times with awareness of every pet's tasks, and detect conflicts across them."""
        pet_by_task_id: Dict[str, Pet] = {}
        all_tasks: List[Task] = []
        for pet in self.owner.list_pets():
            tasks = pet.list_tasks() if include_completed else self.filter_pending(pet.list_tasks())
            for task in tasks:
                pet_by_task_id[task.task_id] = pet
                all_tasks.append(task)

        occurrences = self.assign_schedule(all_tasks)

        pet_schedules = {pet_id: Schedule(pet=pet) for pet_id, pet in self.owner.pets.items()}
        for occurrence in occurrences:
            pet = pet_by_task_id[occurrence.task.task_id]
            pet_schedules[pet.pet_id].occurrences.append(occurrence)

        pet_tasks = [(pet_by_task_id[occurrence.task.task_id], occurrence) for occurrence in occurrences]
        conflicts = self.find_conflicts(pet_tasks)
        return CombinedSchedule(owner=self.owner, pet_schedules=pet_schedules, conflicts=conflicts)
