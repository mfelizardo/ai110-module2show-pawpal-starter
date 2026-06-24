from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    task_name: str
    duration: int
    priority: int


@dataclass
class Pet:
    name: str
    breed: str
    tasks: List[Task] = field(default_factory=list)


@dataclass
class Schedule:
    pet_name: str
    pet_breed: str
    ordered_tasks: List[Task] = field(default_factory=list)


@dataclass
class Owner:
    name: str
    pet: Pet

    def edit_name(self, new_name: str) -> None:
        pass

    def edit_basic_pet_info(self, pet_name: str) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, old_task: Task, new_task: Task) -> None:
        pass

    def generate_daily_schedule(self) -> Schedule:
        pass
