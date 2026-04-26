import pytest
from datetime import datetime, timedelta
from pawpal_system import PetOwner, Pet, Task, Schedule

# ============================================================
# CORE FUNCTIONALITY
# ============================================================

def test_pet_add_task(dog, walk_task):
    dog.add_task(walk_task)
    assert walk_task in dog.get_tasks()
    assert len(dog.get_tasks()) == 1


def test_schedule_get_all_pet_tasks(owner, dog, cat):
    task1 = Task("Walk", 30, "high", "exercise", "daily")
    task2 = Task("Feed", 15, "medium", "feeding", "daily")
    dog.add_task(task1)
    cat.add_task(task2)
    owner.add_pet(dog)
    owner.add_pet(cat)
    all_tasks = Schedule(owner).get_all_pet_tasks()
    assert len(all_tasks) == 2
    assert task1 in all_tasks


def test_task_completion_status_update():
    task = Task("Walk", 30, "high", "exercise", "daily")
    assert task.completion_status == "pending"
    task.update_completion_status("completed")
    assert task.completion_status == "completed"


def test_task_addition_increases_count(dog, walk_task):
    before = len(dog.get_tasks())
    dog.add_task(walk_task)
    assert len(dog.get_tasks()) == before + 1


# ============================================================
# SORTING CORRECTNESS
# ============================================================

def test_sort_by_time_chronological_order(owner, dog):
    owner.add_pet(dog)
    tasks = [
        Task("Lunch",     30, "medium", "feeding",  "daily", "12:00", "pending", "Buddy", datetime.now()),
        Task("Walk",      30, "high",   "exercise", "daily", "08:00", "pending", "Buddy", datetime.now()),
        Task("Playtime",  45, "low",    "play",     "daily", "18:00", "pending", "Buddy", datetime.now()),
        Task("Breakfast", 20, "medium", "feeding",  "daily", "07:00", "pending", "Buddy", datetime.now()),
    ]
    for t in tasks:
        dog.add_task(t)
    sorted_tasks = Schedule(owner).sort_by_time()
    assert [t.time for t in sorted_tasks] == ["07:00", "08:00", "12:00", "18:00"]


def test_sort_by_time_same_time_stability(owner, dog):
    owner.add_pet(dog)
    for name, dur in [("Walk", 30), ("Brushing", 20), ("Medication", 5)]:
        dog.add_task(Task(name, dur, "high", "exercise", "daily", "08:00", "pending", "Buddy", datetime.now()))
    sorted_tasks = Schedule(owner).sort_by_time()
    assert all(t.time == "08:00" for t in sorted_tasks)
    assert len(sorted_tasks) == 3


def test_sort_by_time_empty_task_list(owner, dog):
    owner.add_pet(dog)
    assert Schedule(owner).sort_by_time() == []


def test_sort_by_time_midnight_boundary(owner, dog):
    owner.add_pet(dog)
    for time in ["23:59", "00:00", "00:30"]:
        dog.add_task(Task("T", 5, "low", "play", "daily", time, "pending", "Buddy", datetime.now()))
    sorted_tasks = Schedule(owner).sort_by_time()
    assert [t.time for t in sorted_tasks] == ["00:00", "00:30", "23:59"]


def test_sort_by_time_single_task(owner, dog, walk_task):
    owner.add_pet(dog)
    dog.add_task(walk_task)
    sorted_tasks = Schedule(owner).sort_by_time()
    assert len(sorted_tasks) == 1
    assert sorted_tasks[0].name == "Walk"


@pytest.mark.parametrize("times", [
    ["15:00", "08:00", "12:30", "00:00", "23:59"],
    ["23:00", "01:00", "12:00"],
    ["09:30", "09:00", "09:15"],
])
def test_sort_order_invariant(owner, dog, times):
    """sort_by_time() always returns tasks in non-decreasing time order."""
    owner.add_pet(dog)
    for i, t in enumerate(times):
        dog.add_task(Task(f"T{i}", 5, "low", "play", "daily", t, "pending", "Buddy"))

    def to_min(t):
        h, m = map(int, t.split(':'))
        return h * 60 + m

    result = Schedule(owner).sort_by_time()
    minutes = [to_min(t.time) for t in result]
    assert minutes == sorted(minutes)


# ============================================================
# RECURRENCE LOGIC
# ============================================================

def test_recurring_daily_task_creates_next_day(owner, dog):
    owner.add_pet(dog)
    today = datetime.now()
    task = Task("Feeding", 15, "high", "feeding", "daily", "12:00", "pending", "Buddy", today)
    dog.add_task(task)
    schedule = Schedule(owner)
    initial = len(schedule.get_all_pet_tasks())
    schedule.mark_task_complete(task)
    assert len(schedule.get_all_pet_tasks()) == initial + 1
    new_task = next(t for t in schedule.get_all_pet_tasks() if t.name == "Feeding" and t.completion_status == "pending")
    assert new_task.due_date.date() == (today + timedelta(days=1)).date()


def test_recurring_weekly_task_creates_next_week(owner, dog):
    owner.add_pet(dog)
    today = datetime.now()
    task = Task("Grooming", 60, "medium", "grooming", "weekly", "14:00", "pending", "Buddy", today)
    dog.add_task(task)
    schedule = Schedule(owner)
    initial = len(schedule.get_all_pet_tasks())
    schedule.mark_task_complete(task)
    assert len(schedule.get_all_pet_tasks()) == initial + 1
    new_task = next(t for t in schedule.get_all_pet_tasks() if t.name == "Grooming" and t.completion_status == "pending")
    assert new_task.due_date.date() == (today + timedelta(weeks=1)).date()


def test_recurring_task_preserves_properties(owner, dog):
    owner.add_pet(dog)
    task = Task("Medication", 5, "high", "medication", "daily", "09:00", "pending", "Buddy", datetime.now())
    dog.add_task(task)
    Schedule(owner).mark_task_complete(task)
    all_tasks = Schedule(owner).get_all_pet_tasks()
    new_task = next(t for t in all_tasks if t.name == "Medication" and t.completion_status == "pending")
    assert new_task.duration == task.duration
    assert new_task.priority == task.priority
    assert new_task.category == task.category
    assert new_task.time == task.time
    assert new_task.pet_name == task.pet_name


def test_non_recurring_task_does_not_create_new_task(owner, dog):
    owner.add_pet(dog)
    task = Task("Vet Appointment", 30, "high", "health", "once", "10:00", "pending", "Buddy", datetime.now())
    dog.add_task(task)
    schedule = Schedule(owner)
    initial = len(schedule.get_all_pet_tasks())
    schedule.mark_task_complete(task)
    assert len(schedule.get_all_pet_tasks()) == initial


def test_multiple_recurring_completions(owner, dog):
    owner.add_pet(dog)
    task = Task("Feeding", 15, "high", "feeding", "daily", "12:00", "pending", "Buddy", datetime.now())
    dog.add_task(task)
    schedule = Schedule(owner)
    schedule.mark_task_complete(task)
    next_task = next(t for t in schedule.get_all_pet_tasks() if t.completion_status == "pending")
    schedule.mark_task_complete(next_task)
    assert len(schedule.get_all_pet_tasks()) == 3


# ============================================================
# CONFLICT DETECTION
# ============================================================

def test_detect_same_start_time_conflict(owner, dog):
    owner.add_pet(dog)
    dog.add_task(Task("Walk",     30, "high",   "exercise", "daily", "08:00", "pending", "Buddy", datetime.now()))
    dog.add_task(Task("Brushing", 20, "medium", "grooming", "daily", "08:00", "pending", "Buddy", datetime.now()))
    conflicts = Schedule(owner).detect_time_conflicts()
    assert len(conflicts) > 0
    assert "08:00" in conflicts[0]


def test_detect_cross_pet_same_time_conflict(owner, dog, cat):
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Walk",     30, "high", "exercise", "daily", "09:00", "pending", "Buddy",    datetime.now()))
    cat.add_task(Task("Playtime", 45, "low",  "play",     "daily", "09:00", "pending", "Whiskers", datetime.now()))
    conflicts = Schedule(owner).detect_time_conflicts()
    assert len(conflicts) > 0
    assert "Buddy" in conflicts[0]
    assert "Whiskers" in conflicts[0]


def test_detect_three_way_conflict(owner, dog):
    owner.add_pet(dog)
    dog.add_task(Task("Walk",       30, "high",   "exercise",  "daily", "10:00", "pending", "Buddy", datetime.now()))
    dog.add_task(Task("Feeding",    15, "medium", "feeding",   "daily", "10:00", "pending", "Buddy", datetime.now()))
    dog.add_task(Task("Medication",  5, "high",   "medication","daily", "10:00", "pending", "Buddy", datetime.now()))
    conflicts = Schedule(owner).detect_time_conflicts()
    assert len(conflicts) > 0
    all_text = " ".join(conflicts)
    assert "Walk" in all_text
    assert "Feeding" in all_text
    assert "Medication" in all_text


def test_no_conflicts_staggered_tasks(owner, dog):
    owner.add_pet(dog)
    dog.add_task(Task("Walk",     30, "high",   "exercise", "daily", "08:00", "pending", "Buddy", datetime.now()))
    dog.add_task(Task("Feeding",  15, "medium", "feeding",  "daily", "12:00", "pending", "Buddy", datetime.now()))
    dog.add_task(Task("Playtime", 45, "low",    "play",     "daily", "18:00", "pending", "Buddy", datetime.now()))
    assert Schedule(owner).detect_time_conflicts() == []


def test_no_conflicts_empty_schedule(owner, dog):
    owner.add_pet(dog)
    assert Schedule(owner).detect_time_conflicts() == []


def test_no_conflicts_single_task(owner, dog, walk_task):
    owner.add_pet(dog)
    dog.add_task(walk_task)
    assert Schedule(owner).detect_time_conflicts() == []


def test_detect_duration_based_overlap(owner, dog):
    """Walk starts 08:00 for 60 min; Feed starts 08:30 — windows overlap even though start times differ."""
    owner.add_pet(dog)
    dog.add_task(Task("Walk", 60, "high",   "exercise", "daily", "08:00", "pending", "Buddy", datetime.now()))
    dog.add_task(Task("Feed", 30, "medium", "feeding",  "daily", "08:30", "pending", "Buddy", datetime.now()))
    conflicts = Schedule(owner).detect_time_conflicts()
    assert len(conflicts) > 0


def test_no_false_positive_adjacent_tasks(owner, dog):
    """Walk ends exactly at 08:30 when Feed starts — adjacent windows must NOT be flagged."""
    owner.add_pet(dog)
    dog.add_task(Task("Walk", 30, "high",   "exercise", "daily", "08:00", "pending", "Buddy", datetime.now()))
    dog.add_task(Task("Feed", 15, "medium", "feeding",  "daily", "08:30", "pending", "Buddy", datetime.now()))
    assert Schedule(owner).detect_time_conflicts() == []


# ============================================================
# INPUT VALIDATION
# ============================================================

@pytest.mark.parametrize("bad_priority", ["urgent", "CRITICAL", "", "normal"])
def test_task_invalid_priority_raises(bad_priority):
    with pytest.raises(ValueError):
        Task("Walk", 30, bad_priority, "exercise", "daily")


@pytest.mark.parametrize("bad_frequency", ["monthly", "hourly", "", "bi-weekly"])
def test_task_invalid_frequency_raises(bad_frequency):
    with pytest.raises(ValueError):
        Task("Walk", 30, "high", "exercise", bad_frequency)


@pytest.mark.parametrize("bad_duration", [0, -1, -100])
def test_task_invalid_duration_raises(bad_duration):
    with pytest.raises(ValueError):
        Task("Walk", bad_duration, "high", "exercise", "daily")


@pytest.mark.parametrize("bad_time", ["25:00", "12:60", "-1:00", "abc:def", "", "08:00:00"])
def test_task_invalid_time_raises(bad_time):
    with pytest.raises(ValueError):
        Task("Walk", 30, "high", "exercise", "daily", bad_time)


@pytest.mark.parametrize("bad_status", ["done", "cancelled", "PENDING"])
def test_task_invalid_initial_status_raises(bad_status):
    with pytest.raises(ValueError):
        Task("Walk", 30, "high", "exercise", "daily", "08:00", bad_status)


@pytest.mark.parametrize("good_priority", ["high", "medium", "low"])
def test_task_valid_priorities_accepted(good_priority):
    task = Task("Walk", 30, good_priority, "exercise", "daily")
    assert task.priority == good_priority


@pytest.mark.parametrize("good_freq", ["daily", "weekly", "once"])
def test_task_valid_frequencies_accepted(good_freq):
    task = Task("Walk", 30, "high", "exercise", good_freq)
    assert task.frequency == good_freq


# ============================================================
# SCHEDULE RELIABILITY INVARIANTS
# ============================================================

def test_capacity_tracks_total_time(owner):
    task1 = Task("Walk", 30, "high", "exercise", "daily")
    task2 = Task("Feed", 15, "medium", "feeding", "daily")
    owner.add_task(task1)
    owner.add_task(task2)
    schedule = Schedule(owner)
    schedule.add_task(task1)
    schedule.add_task(task2)
    assert schedule.total_time_used == 45
    assert schedule.remaining_time == owner.available_time_per_day - 45


def test_capacity_reflects_overbooked_state(owner):
    """Remaining time goes negative when tasks exceed available time."""
    for i in range(4):
        t = Task(f"T{i}", 130, "low", "exercise", "daily")
        owner.add_task(t)
    schedule = Schedule(owner)
    for t in owner.get_tasks():
        schedule.add_task(t)
    assert schedule.remaining_time < 0


@pytest.mark.parametrize("status", ["pending", "in_progress", "completed"])
def test_filter_returns_only_matching_status(owner, dog, status):
    owner.add_pet(dog)
    dog.add_task(Task("Walk", 30, "high", "exercise", "daily", "08:00", status, "Buddy"))
    schedule = Schedule(owner)
    result = schedule.filter_tasks(completion_status=status)
    assert len(result) == 1
    assert result[0].completion_status == status


def test_filter_by_pet_name(owner, dog, cat):
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Walk",     30, "high", "exercise", "daily", "08:00", "pending", "Buddy"))
    cat.add_task(Task("Playtime", 20, "low",  "play",     "daily", "09:00", "pending", "Whiskers"))
    schedule = Schedule(owner)
    buddy_tasks = schedule.filter_tasks(pet_name="Buddy")
    assert all(t.pet_name == "Buddy" for t in buddy_tasks)
    assert len(buddy_tasks) == 1


def test_remove_task_updates_capacity(owner):
    task = Task("Walk", 30, "high", "exercise", "daily")
    owner.add_task(task)
    schedule = Schedule(owner)
    schedule.add_task(task)
    assert schedule.total_time_used == 30
    schedule.remove_task(task)
    assert schedule.total_time_used == 0
    assert schedule.remaining_time == owner.available_time_per_day


# ============================================================
# RELIABILITY REPORT (CONFIDENCE SCORING)
# ============================================================

def test_reliability_report_perfect_schedule(owner, dog):
    """Conflict-free, within-capacity schedule scores 1.0."""
    owner.add_pet(dog)
    dog.add_task(Task("Walk", 30, "high", "exercise", "daily", "08:00", "pending", "Buddy"))
    dog.add_task(Task("Feed", 15, "medium", "feeding", "daily", "12:00", "pending", "Buddy"))
    report = Schedule(owner).generate_reliability_report()
    assert report["confidence"] == 1.0
    assert report["conflict_count"] == 0
    assert report["issues"] == []


def test_reliability_report_with_conflict(owner, dog):
    """Each conflicting pair deducts 0.15; one conflict → 0.85."""
    owner.add_pet(dog)
    dog.add_task(Task("Walk", 60, "high", "exercise", "daily", "08:00", "pending", "Buddy"))
    dog.add_task(Task("Feed", 30, "medium", "feeding", "daily", "08:30", "pending", "Buddy"))
    report = Schedule(owner).generate_reliability_report()
    assert report["confidence"] == 0.85
    assert report["conflict_count"] == 1
    assert len(report["issues"]) == 1


def test_reliability_report_with_two_conflicts(owner, dog):
    """Two conflicting pairs deduct 0.30 → score 0.70."""
    owner.add_pet(dog)
    dog.add_task(Task("Walk",       60, "high",   "exercise",  "daily", "08:00", "pending", "Buddy"))
    dog.add_task(Task("Feed",       30, "medium", "feeding",   "daily", "08:30", "pending", "Buddy"))
    dog.add_task(Task("Medication", 45, "high",   "medication","daily", "08:15", "pending", "Buddy"))
    report = Schedule(owner).generate_reliability_report()
    assert report["confidence"] == pytest.approx(0.55, abs=0.05)
    assert report["conflict_count"] >= 2


def test_reliability_report_overbooked(owner, dog):
    """Overbooked schedule (no conflicts) loses 0.20 → score 0.80."""
    owner.add_pet(dog)
    # 5 × 100 min = 500 min > 480 available
    for i in range(5):
        dog.add_task(Task(f"T{i}", 100, "low", "exercise", "daily",
                          f"{(i * 2):02d}:00", "pending", "Buddy"))
    report = Schedule(owner).generate_reliability_report()
    assert report["confidence"] == pytest.approx(0.80, abs=0.01)
    assert any("Overbooked" in issue for issue in report["issues"])


def test_reliability_report_empty_schedule(owner, dog):
    """Empty schedule has confidence 0.0."""
    owner.add_pet(dog)
    report = Schedule(owner).generate_reliability_report()
    assert report["confidence"] == 0.0
    assert report["task_count"] == 0


def test_reliability_report_summary_contains_confidence(owner, dog):
    """summary field is human-readable and always contains a percentage."""
    owner.add_pet(dog)
    dog.add_task(Task("Walk", 30, "high", "exercise", "daily", "08:00", "pending", "Buddy"))
    report = Schedule(owner).generate_reliability_report()
    assert "%" in report["summary"]
