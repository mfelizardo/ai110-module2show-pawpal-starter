import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _new_id() -> str:
    return uuid.uuid4().hex[:8]


@dataclass
class Task:
    task_name: str
    duration: int
    priority: int
    task_id: str = field(default_factory=_new_id)


@dataclass
class Pet:
    name: str
    breed: str
    tasks: List[Task] = field(default_factory=list)
    pet_id: str = field(default_factory=_new_id)


@dataclass
class Schedule:
    pet: Pet
    ordered_tasks: List[Task] = field(default_factory=list)


@dataclass
class Owner:
    name: str
    pets: Dict[str, Pet] = field(default_factory=dict)

    def edit_name(self, new_name: str) -> None:
        pass

    def edit_basic_pet_info(
        self,
        pet_id: str,
        new_name: Optional[str] = None,
        new_breed: Optional[str] = None,
    ) -> None:
        pass

    def add_task(self, pet_id: str, task: Task) -> None:
        pass

    def edit_task(self, pet_id: str, task_id: str, new_task: Task) -> None:
        pass

    def generate_daily_schedule(self, pet_id: str) -> Schedule:
        pass
