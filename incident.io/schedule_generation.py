from datetime import timedelta
from helper import parse_time
    
def generate_base_schedule(schedule: dict, from_dt: str, until_dt: str) -> list:
    """Generate the base schedule entries from the schedule definition between from_dt and until_dt."""
    # Basic validation of schedule
    if not schedule.get("users") or not schedule.get("handover_start_at") or not schedule.get("handover_interval_days"):
        raise ValueError("Schedule definition is missing required fields.")
    
    users = schedule["users"]
    start = parse_time(schedule["handover_start_at"])
    interval = timedelta(days=schedule["handover_interval_days"])
    
    # Generate entries
    entries = []
    idx = 0
    while start < until_dt:
        end = start + interval
        entries.append({
            "user": users[idx % len(users)],
            "start_at": start,
            "end_at": end
        })
        start = end
        idx += 1
    
    # Truncate to [from, until]
    truncated = []
    for e in entries:
        s, e_end = max(e["start_at"], from_dt), min(e["end_at"], until_dt)
        if s < e_end:
            truncated.append({"user": e["user"], "start_at": s, "end_at": e_end})
    return truncated


def apply_overrides(base: list, overrides: list) -> list:
    """
    Apply overrides to the base schedule entries.
    Overrides can split base entries into multiple segments.
    Later overrides in the list take precedence over earlier ones.
    """
    parsed_overrides = []
    for o in overrides:
        parsed_overrides.append({
            "user": o["user"],
            "start_at": parse_time(o["start_at"]),
            "end_at": parse_time(o["end_at"])
        })

    result = []
    for entry in base:
        e_start, e_end = entry["start_at"], entry["end_at"]
        
        # Find overrides intersecting this base shift
        relevant = [o for o in parsed_overrides if not (o["end_at"] <= e_start or o["start_at"] >= e_end)]
        if not relevant:
            result.append(entry)
            continue
        
        # Build boundary points (base + all relevant overrides)
        points = {e_start, e_end}
        for o in relevant:
            points.add(max(o["start_at"], e_start))
            points.add(min(o["end_at"], e_end))
        points = sorted(points)

        # Walk through consecutive segments
        for i in range(len(points) - 1):
            seg_start, seg_end = points[i], points[i + 1]
            # active overrides during this segment
            active = [o for o in relevant if o["start_at"] <= seg_start and o["end_at"] >= seg_end]
            if active:
                # latest override in file wins if overlap
                user = active[-1]["user"]
            else:
                user = entry["user"]
            if seg_start < seg_end:
                result.append({"user": user, "start_at": seg_start, "end_at": seg_end})

    return result


def merge_adjacent(entries: list) -> list:
    """Merge adjacent schedule entries for the same user."""
    if not entries:
        return []
    merged = [entries[0]]
    for e in entries[1:]:
        last = merged[-1]
        if e["user"] == last["user"] and e["start_at"] == last["end_at"]:
            last["end_at"] = e["end_at"]
        else:
            merged.append(e)
    return merged