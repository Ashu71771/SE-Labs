
"""Conference room and equipment scheduling system."""

import json
from datetime import datetime

# Global state
reservations = {}
equipment_pool = {"projector": 2, "microphone": 4, "webcam": 1}
conflicts = []
reservation_counter = {"next_id": 1}


def schedule_room(room_id, time_slot, equipment_list=None):
    """Schedule a room and allocate the requested equipment."""
    if equipment_list is None:
        equipment_list = []

    if not isinstance(time_slot, str) or "-" not in time_slot:
        raise ValueError("Time slot must use the format HH-HH.")

    try:
        start, end = map(int, time_slot.split("-"))
    except ValueError as error:
        raise ValueError("Time slot must use the format HH-HH.") from error

    if not 0 <= start < end <= 24:
        raise ValueError("Time slot must have valid, increasing hours.")

    for reservation in reservations.values():
        if (
            reservation["room"] == room_id
            and reservation["slot"] == time_slot
        ):
            message = f"{room_id} double-booked at {time_slot}"
            conflicts.append(message)
            raise ValueError(message)

    for equipment in equipment_list:
        if equipment not in equipment_pool:
            raise ValueError(f"Unknown equipment: {equipment}")
        if equipment_pool[equipment] <= 0:
            raise ValueError(f"Equipment unavailable: {equipment}")

    for equipment in equipment_list:
        equipment_pool[equipment] -= 1

    reservation_id = reservation_counter["next_id"]
    reservation_counter["next_id"] += 1

    reservations[reservation_id] = {
        "room": room_id,
        "slot": time_slot,
        "equipment": equipment_list.copy(),
    }

    return reservation_id


def cancel_reservation(reservation_id):
    """Cancel a reservation and return its equipment."""
    reservation = reservations.get(reservation_id)

    if reservation is None:
        print(f"Reservation {reservation_id} does not exist.")
        return

    for equipment in reservation["equipment"]:
        equipment_pool[equipment] += 1

    del reservations[reservation_id]


def slot_hours(time_slot):
    """Return the duration of a time slot expressed as start-end hours."""
    if not isinstance(time_slot, str) or "-" not in time_slot:
        raise ValueError("Time slot must use the format HH-HH.")

    try:
        start, end = map(int, time_slot.split("-"))
    except ValueError as error:
        raise ValueError("Time slot must use the format HH-HH.") from error

    if not 0 <= start < end <= 24:
        raise ValueError("Time slot must have valid, increasing hours.")

    return end - start


def export_schedule(file="schedule.json"):
    """Export reservations to a JSON file."""
    with open(file, "w", encoding="utf-8") as output_file:
        json.dump(reservations, output_file, indent=4)


def log_conflicts(file="conflicts.log"):
    """Append conflicts to a log file and display its contents."""
    with open(file, "a", encoding="utf-8") as log_file:
        for conflict in conflicts:
            log_file.write(f"{datetime.now()} {conflict}\n")

    with open(file, "r", encoding="utf-8") as log_file:
        print(log_file.read())


def main():
    """Run a demonstration of the room scheduling system."""
    schedule_room("Board-1", "09-11")

    try:
        schedule_room("Board-1", "09-11")
    except ValueError as error:
        print(f"Scheduling error: {error}")

    reservation_id = schedule_room("Huddle-3", "10-12")
    print(
        "Slot length for reservation:",
        slot_hours(reservations[reservation_id]["slot"]),
    )

    cancel_reservation(77)

    slot = input(
        "Slot for Board-2, like 10-12 (Enter for 10-12): "
    ) or "10-12"

    try:
        schedule_room("Board-2", slot, ["projector", "webcam"])
    except ValueError as error:
        print(f"Scheduling error: {error}")

    export_schedule()
    log_conflicts()

    print("Equipment left:", equipment_pool)
    print("Reservations:", reservations)


if __name__ == "__main__":
    main()
