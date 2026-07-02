import datetime
import json
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant.")

PRIORITY_LABELS = {"Low": 1, "Medium": 2, "High": 3}
PRIORITY_NAMES = {value: name for name, value in PRIORITY_LABELS.items()}

DATA_FILE = Path(__file__).resolve().parent / "pawpal_data.json"


def task_to_dict(task: Task) -> dict:
    return {
        "task_id": task.task_id,
        "description": task.description,
        "duration": task.duration,
        "priority": task.priority,
        "due_time": task.due_time,
        "due_times": task.due_times,
        "frequency": task.frequency,
        "completed": task.completed,
        "concurrent_ok": task.concurrent_ok,
    }


def pet_to_dict(pet: Pet) -> dict:
    return {
        "pet_id": pet.pet_id,
        "name": pet.name,
        "breed": pet.breed,
        "tasks": [task_to_dict(task) for task in pet.tasks],
    }


def owner_to_dict(owner: Owner) -> dict:
    return {"name": owner.name, "pets": [pet_to_dict(pet) for pet in owner.pets.values()]}


def owner_from_dict(data: dict) -> Owner:
    owner = Owner(name=data["name"])
    for pet_data in data["pets"]:
        pet = Pet(name=pet_data["name"], breed=pet_data["breed"], pet_id=pet_data["pet_id"])
        pet.tasks = [Task(**task_data) for task_data in pet_data["tasks"]]
        owner.pets[pet.pet_id] = pet
    return owner


def save_state(owner: Owner) -> None:
    """Persist the owner to disk so a browser refresh (a brand-new Streamlit session) can reload it."""
    DATA_FILE.write_text(json.dumps(owner_to_dict(owner), indent=2))


def load_state() -> Owner | None:
    """Load the previously saved owner, or None if there's nothing usable on disk yet."""
    if not DATA_FILE.exists():
        return None
    try:
        return owner_from_dict(json.loads(DATA_FILE.read_text()))
    except Exception:
        return None


def init_state() -> None:
    """Create the owner (and everything hanging off it) exactly once per session.

    Streamlit reruns this whole script on every interaction, so the Owner object
    is stored in st.session_state and reused across reruns instead of being
    recreated. It's also loaded from/saved to disk so a full page refresh (which
    starts a brand-new session with empty session_state) can pick up where the
    last session left off.
    """
    if "owner" not in st.session_state:
        st.session_state.owner = load_state() or Owner("Jordan")
    if "selected_pet_id" not in st.session_state:
        st.session_state.selected_pet_id = None
    if "show_schedule" not in st.session_state:
        st.session_state.show_schedule = False


init_state()
owner: Owner = st.session_state.owner

try:
    st.divider()

    st.subheader("Owner")
    new_name = st.text_input("Owner name", value=owner.name)
    if new_name != owner.name:
        owner.edit_name(new_name)

    st.divider()

    st.subheader("Pets")

    with st.form("add_pet_form", clear_on_submit=True):
        st.markdown("**Add a pet**")
        col1, col2 = st.columns(2)
        with col1:
            pet_name = st.text_input("Pet name")
        with col2:
            pet_breed = st.text_input("Breed/species")
        if st.form_submit_button("Add pet") and pet_name:
            new_pet = Pet(name=pet_name, breed=pet_breed)
            owner.add_pet(new_pet)
            st.session_state.selected_pet_id = new_pet.pet_id

    pets = owner.list_pets()

    if not pets:
        st.info("Add a pet above to get started.")
        st.stop()

    pet_ids = [pet.pet_id for pet in pets]
    default_index = (
        pet_ids.index(st.session_state.selected_pet_id)
        if st.session_state.selected_pet_id in pet_ids
        else 0
    )
    selected_pet_id = st.selectbox(
        "Select pet",
        pet_ids,
        index=default_index,
        format_func=lambda pid: owner.get_pet(pid).name,
    )
    st.session_state.selected_pet_id = selected_pet_id
    selected_pet = owner.get_pet(selected_pet_id)

    with st.expander(f"Edit {selected_pet.name}'s info"):
        with st.form("edit_pet_form"):
            edit_name = st.text_input("Name", value=selected_pet.name)
            edit_breed = st.text_input("Breed/species", value=selected_pet.breed)
            if st.form_submit_button("Save pet info"):
                owner.edit_basic_pet_info(selected_pet_id, new_name=edit_name, new_breed=edit_breed)

    st.divider()

    st.subheader(f"Tasks for {selected_pet.name}")

    st.markdown("**Add a task**")
    check_col1, check_col2, _ = st.columns(3)
    with check_col1:
        has_due_time = st.checkbox("Has a fixed due time", value=True, key="add_task_has_due_time")
    with check_col2:
        add_frequency = st.number_input(
            "Frequency (per day)", min_value=0, max_value=10, value=1, key="add_task_frequency"
        )
    add_slot_count = max(1, int(add_frequency))

    with st.form("add_task_form", clear_on_submit=True):
        description = st.text_input("Task description")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority_label = st.selectbox("Priority", list(PRIORITY_LABELS.keys()), index=1)

        due_time_value = None
        due_times_values = None
        if has_due_time:
            if add_slot_count == 1:
                due_time_value = st.time_input("Due time", value=datetime.time(8, 0))
            else:
                st.caption(f"This task happens {add_slot_count}x/day — set a due time for each occurrence.")
                due_times_values = [
                    st.time_input(f"Due time #{i + 1}", value=datetime.time(8, 0), key=f"add_due_time_{i}")
                    for i in range(add_slot_count)
                ]

        concurrent_ok = st.checkbox("Okay to happen at the same time as another pet's task")

        if st.form_submit_button("Add task") and description:
            owner.add_task(
                selected_pet_id,
                Task(
                    description=description,
                    duration=int(duration),
                    priority=PRIORITY_LABELS[priority_label],
                    due_time=due_time_value.strftime("%H:%M") if due_time_value else None,
                    due_times=(
                        [t.strftime("%H:%M") for t in due_times_values] if due_times_values else None
                    ),
                    frequency=int(add_frequency),
                    concurrent_ok=concurrent_ok,
                ),
            )

    tasks = selected_pet.list_tasks()

    if not tasks:
        st.info("No tasks yet for this pet. Add one above.")
    else:
        for task in tasks:
            due_label = ", ".join(task.due_times) if task.due_times else (task.due_time or "no fixed time")
            header = f"{'✅' if task.completed else '⬜'} {task.description} — {PRIORITY_NAMES[task.priority]} priority, {task.duration} min, {due_label}"
            with st.expander(header):
                completed = st.checkbox("Completed", value=task.completed, key=f"completed_{task.task_id}")
                if completed != task.completed:
                    task.mark_complete() if completed else task.mark_incomplete()

                e_has_due_time = st.checkbox(
                    "Has a fixed due time",
                    value=task.due_time is not None or task.due_times is not None,
                    key=f"has_due_time_{task.task_id}",
                )
                e_frequency = st.number_input(
                    "Frequency (per day)",
                    min_value=0,
                    max_value=10,
                    value=task.frequency,
                    key=f"frequency_{task.task_id}",
                )
                e_slot_count = max(1, int(e_frequency))

                with st.form(f"edit_task_form_{task.task_id}"):
                    e_description = st.text_input("Description", value=task.description)
                    e_duration = st.number_input(
                        "Duration (minutes)", min_value=1, max_value=240, value=task.duration
                    )
                    e_priority_label = st.selectbox(
                        "Priority",
                        list(PRIORITY_LABELS.keys()),
                        index=list(PRIORITY_LABELS.values()).index(task.priority),
                    )

                    e_due_time_value = None
                    e_due_times_values = None
                    if e_has_due_time:
                        existing_due_times = task.due_times or []
                        if e_slot_count == 1:
                            e_due_time_value = st.time_input(
                                "Due time",
                                value=(
                                    datetime.datetime.strptime(task.due_time, "%H:%M").time()
                                    if task.due_time
                                    else datetime.time(8, 0)
                                ),
                            )
                        else:
                            st.caption(
                                f"This task happens {e_slot_count}x/day — set a due time for each occurrence."
                            )
                            e_due_times_values = [
                                st.time_input(
                                    f"Due time #{i + 1}",
                                    value=(
                                        datetime.datetime.strptime(existing_due_times[i], "%H:%M").time()
                                        if i < len(existing_due_times)
                                        else datetime.time(8, 0)
                                    ),
                                    key=f"edit_due_time_{task.task_id}_{i}",
                                )
                                for i in range(e_slot_count)
                            ]

                    e_concurrent_ok = st.checkbox("Okay to happen at the same time", value=task.concurrent_ok)

                    save_col, delete_col = st.columns(2)
                    with save_col:
                        save_clicked = st.form_submit_button("Save changes")
                    with delete_col:
                        delete_clicked = st.form_submit_button("Delete task")

                    if save_clicked:
                        owner.edit_task(
                            selected_pet_id,
                            task.task_id,
                            Task(
                                description=e_description,
                                duration=int(e_duration),
                                priority=PRIORITY_LABELS[e_priority_label],
                                due_time=e_due_time_value.strftime("%H:%M") if e_due_time_value else None,
                                due_times=(
                                    [t.strftime("%H:%M") for t in e_due_times_values]
                                    if e_due_times_values
                                    else None
                                ),
                                frequency=int(e_frequency),
                                completed=task.completed,
                                concurrent_ok=e_concurrent_ok,
                            ),
                        )
                        st.rerun()
                    if delete_clicked:
                        selected_pet.remove_task(task.task_id)
                        st.rerun()

    st.divider()

    st.subheader("Schedule")
    include_completed = st.checkbox("Include completed tasks", value=False)
    if st.button("Generate schedule"):
        st.session_state.show_schedule = True

    if st.session_state.show_schedule:
        scheduler = Scheduler(owner)
        combined = scheduler.generate_combined_schedule(include_completed=include_completed)

        for pet_schedule in combined.pet_schedules.values():
            st.markdown(f"**{pet_schedule.pet.name}** ({pet_schedule.pet.breed})")
            if not pet_schedule.occurrences:
                st.write("No pending tasks.")
                continue
            for occurrence in pet_schedule.occurrences:
                task = occurrence.task
                auto_label = "" if (task.due_time or task.due_times) else " (auto-assigned)"
                st.write(f"  {occurrence.start_time}  {task.description} ({task.duration} min){auto_label}")

        if combined.conflicts:
            st.warning("Scheduling conflicts detected:")
            for conflict in combined.conflicts:
                st.write(
                    f"- {conflict.pet_a.name}'s '{conflict.task_a.description}' ({conflict.start_a}) overlaps "
                    f"with {conflict.pet_b.name}'s '{conflict.task_b.description}' ({conflict.start_b})"
                )
        else:
            st.success("No conflicts detected.")
finally:
    save_state(owner)
