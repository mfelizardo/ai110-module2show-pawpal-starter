import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _new_id() -> str:
    return uuid.uuid4().hex[:8]


def _time_to_minutes(due_time: str) -> int:
    hours, minutes = due_time.split(":")
    return int(hours) * 60 + int(minutes)


@dataclass
class Task:
    description: str
    duration: int
    priority: int
    due_time: Optional[str] = None
    frequency: int = 0
    completed: bool = False
    concurrent_ok: bool = False
    task_id: str = field(default_factory=_new_id)

    def mark_complete(self) -> None:
        self.completed = True

    def mark_incomplete(self) -> None:
        self.completed = False

    def time_window(self) -> Optional[tuple]:
        if self.due_time is None:
            return None
        start = _time_to_minutes(self.due_time)
        return start, start + self.duration


@dataclass
class Pet:
    name: str
    breed: str
    tasks: List[Task] = field(default_factory=list)
    pet_id: str = field(default_factory=_new_id)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def list_tasks(self) -> List[Task]:
        return list(self.tasks)

    def get_task(self, task_id: str) -> Optional[Task]:
        return next((t for t in self.tasks if t.task_id == task_id), None)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.task_id != task_id]


@dataclass
class Schedule:
    pet: Pet
    ordered_tasks: List[Task] = field(default_factory=list)


@dataclass
class ScheduleConflict:
    pet_a: Pet
    task_a: Task
    pet_b: Pet
    task_b: Task


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
        self.name = new_name

    def add_pet(self, pet: Pet) -> None:
        self.pets[pet.pet_id] = pet

    def list_pets(self) -> List[Pet]:
        return list(self.pets.values())

    def get_pet(self, pet_id: str) -> Pet:
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
        pet = self.get_pet(pet_id)
        if new_name is not None:
            pet.name = new_name
        if new_breed is not None:
            pet.breed = new_breed

    def add_task(self, pet_id: str, task: Task) -> None:
        self.get_pet(pet_id).add_task(task)

    def edit_task(self, pet_id: str, task_id: str, new_task: Task) -> None:
        pet = self.get_pet(pet_id)
        for index, task in enumerate(pet.tasks):
            if task.task_id == task_id:
                new_task.task_id = task_id
                pet.tasks[index] = new_task
                return
        raise KeyError(f"No task with id {task_id!r} for pet {pet_id!r}")

    def get_all_tasks(self) -> List[Task]:
        return [task for pet in self.pets.values() for task in pet.tasks]

    def generate_daily_schedule(self, pet_id: str) -> Schedule:
        return Scheduler(self).generate_pet_schedule(pet_id)


@dataclass
class Scheduler:
    owner: Owner

    def filter_pending(self, tasks: List[Task]) -> List[Task]:
        return [t for t in tasks if not t.completed]

    def order_tasks(self, tasks: List[Task]) -> List[Task]:
        return sorted(tasks, key=lambda t: (-t.priority, t.due_time or "", t.duration))

    def find_conflicts(self, pet_tasks: List[tuple]) -> List[ScheduleConflict]:
        """pet_tasks: list of (Pet, Task) pairs. Flags overlapping time windows
        between any two tasks belonging to different pets, unless both tasks
        are marked concurrent_ok (e.g. feeding two pets together)."""
        conflicts: List[ScheduleConflict] = []
        for i, (pet_a, task_a) in enumerate(pet_tasks):
            window_a = task_a.time_window()
            if window_a is None:
                continue
            for pet_b, task_b in pet_tasks[i + 1 :]:
                if pet_a.pet_id == pet_b.pet_id:
                    continue
                if task_a.concurrent_ok and task_b.concurrent_ok:
                    continue
                window_b = task_b.time_window()
                if window_b is None:
                    continue
                if window_a[0] < window_b[1] and window_b[0] < window_a[1]:
                    conflicts.append(ScheduleConflict(pet_a, task_a, pet_b, task_b))
        return conflicts

    def generate_pet_schedule(self, pet_id: str, include_completed: bool = False) -> Schedule:
        pet = self.owner.get_pet(pet_id)
        tasks = pet.list_tasks() if include_completed else self.filter_pending(pet.list_tasks())
        return Schedule(pet=pet, ordered_tasks=self.order_tasks(tasks))

    def generate_combined_schedule(self, include_completed: bool = False) -> CombinedSchedule:
        pet_schedules = {
            pet_id: self.generate_pet_schedule(pet_id, include_completed=include_completed)
            for pet_id in self.owner.pets
        }
        pet_tasks = [
            (schedule.pet, task)
            for schedule in pet_schedules.values()
            for task in schedule.ordered_tasks
        ]
        conflicts = self.find_conflicts(pet_tasks)
        return CombinedSchedule(owner=self.owner, pet_schedules=pet_schedules, conflicts=conflicts)
