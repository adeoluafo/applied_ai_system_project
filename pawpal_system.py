from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pawpal")

@dataclass
class Pet:
    name: str
    type: str
    age: int
    special_needs: str

    def __post_init__(self):
        self.tasks = []  # List of Task objects specific to this pet

    def get_pet_info(self) -> str:
        """Return a string with the pet's information."""
        return f"{self.name} is a {self.age}-year-old {self.type} with special needs: {self.special_needs}"

    def add_task(self, task: Task):
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from the pet's task list if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self):
        """Return the list of tasks for this pet."""
        return self.tasks

@dataclass
class Task:
    name: str
    duration: int
    priority: str
    category: str
    frequency: str
    time: str = "00:00"  # HH:MM format
    completion_status: str = "pending"  # "pending", "completed", "in_progress"
    pet_name: str = ""  # Name of the pet this task belongs to
    due_date: datetime = None  # Due date for the task

    def __post_init__(self):
        _VALID_PRIORITIES = {"high", "medium", "low"}
        _VALID_FREQUENCIES = {"daily", "weekly", "once"}
        _VALID_STATUSES = {"pending", "completed", "in_progress"}

        if self.duration <= 0:
            raise ValueError(f"Task duration must be positive, got {self.duration}")
        if self.priority not in _VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {_VALID_PRIORITIES}, got '{self.priority}'")
        if self.frequency not in _VALID_FREQUENCIES:
            raise ValueError(f"Frequency must be one of {_VALID_FREQUENCIES}, got '{self.frequency}'")
        if self.completion_status not in _VALID_STATUSES:
            raise ValueError(f"Completion status must be one of {_VALID_STATUSES}, got '{self.completion_status}'")
        try:
            h, m = map(int, self.time.split(':'))
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError()
        except ValueError:
            raise ValueError(f"Time must be HH:MM format (00:00–23:59), got '{self.time}'")

    def update_priority(self, new_priority: str):
        """Update the task's priority."""
        self.priority = new_priority

    def update_duration(self, new_duration: int):
        """Update the task's duration."""
        self.duration = new_duration

    def update_completion_status(self, new_status: str):
        """Update the task's completion status."""
        if new_status in ["pending", "completed", "in_progress"]:
            self.completion_status = new_status
        else:
            raise ValueError("Invalid status. Must be 'pending', 'completed', or 'in_progress'")

    def create_recurring_task(self):
        """Create a new instance of this task for the next occurrence if it's recurring."""
        if self.frequency.lower() in ["daily", "weekly"] and self.completion_status == "completed":
            # Calculate next due date
            if self.due_date is None:
                self.due_date = datetime.now()
            
            if self.frequency.lower() == "daily":
                next_due_date = self.due_date + timedelta(days=1)
            elif self.frequency.lower() == "weekly":
                next_due_date = self.due_date + timedelta(weeks=1)
            
            # Create new task with same properties but reset status and updated due date
            new_task = Task(
                name=self.name,
                duration=self.duration,
                priority=self.priority,
                category=self.category,
                frequency=self.frequency,
                time=self.time,
                completion_status="pending",
                pet_name=self.pet_name,
                due_date=next_due_date
            )
            return new_task
        return None

    def get_task_details(self) -> str:
        """Return a string with the task's details."""
        due_date_str = self.due_date.strftime("%Y-%m-%d") if self.due_date else "None"
        return f"Task: {self.name}, Duration: {self.duration} min, Priority: {self.priority}, Category: {self.category}, Frequency: {self.frequency}, Time: {self.time}, Status: {self.completion_status}, Pet: {self.pet_name}, Due: {due_date_str}"

class PetOwner:
    def __init__(self, name: str, available_time_per_day: int, preferences: str):
        self.name = name
        self.available_time_per_day = available_time_per_day
        self.preferences = preferences
        self.tasks = []
        self.pets = []  # Added: list of Pet objects

    def add_task(self, task: Task):
        """Add a task to the owner's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from the owner's task list if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self):
        """Return the list of tasks for the owner."""
        return self.tasks

    def add_pet(self, pet: Pet):
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet):
        """Remove a pet from the owner's pet list if it exists."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_pets(self):
        """Return the list of pets for the owner."""
        return self.pets

class Schedule:
    def __init__(self, owner: PetOwner):
        self.owner = owner
        self.tasks = []  # Copy or reference owner's tasks? For now, separate list for scheduled tasks
        self.total_time_used = 0
        self.remaining_time = owner.available_time_per_day

    def get_all_pet_tasks(self):
        """Retrieve all tasks from the owner's pets."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def sort_by_time(self):
        """Sort and return all pet tasks by time (earliest to latest)."""
        def time_to_minutes(t):
            h, m = map(int, t.split(':'))
            return h * 60 + m
        return sorted(self.get_all_pet_tasks(), key=lambda task: time_to_minutes(task.time))

    def filter_tasks(self, completion_status: str = None, pet_name: str = None):
        """Filter tasks by completion status and/or pet name.
        
        Args:
            completion_status: Filter by status ("pending", "completed", "in_progress")
            pet_name: Filter by pet name
            
        Returns:
            List of filtered tasks
        """
        tasks = self.get_all_pet_tasks()
        
        if completion_status:
            tasks = [task for task in tasks if task.completion_status == completion_status]
        
        if pet_name:
            tasks = [task for task in tasks if task.pet_name == pet_name]
            
        return tasks

    def mark_task_complete(self, task: Task):
        """Mark a task as completed and create recurring task if applicable."""
        task.update_completion_status("completed")
        logger.info("Task completed: '%s' (%s)", task.name, task.pet_name)

        new_task = task.create_recurring_task()
        if new_task:
            for pet in self.owner.pets:
                if pet.name == task.pet_name:
                    pet.add_task(new_task)
                    logger.info(
                        "Recurring task queued: '%s' due %s",
                        new_task.name,
                        new_task.due_date.strftime("%Y-%m-%d") if new_task.due_date else "unknown",
                    )
                    break

    def detect_time_conflicts(self):
        """Detect overlapping task windows using start-time + duration.

        Returns:
            List of warning messages for each pair of conflicting tasks
        """
        warnings = []
        tasks = self.get_all_pet_tasks()

        def time_to_minutes(t):
            h, m = map(int, t.split(':'))
            return h * 60 + m

        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                t1, t2 = tasks[i], tasks[j]
                start1 = time_to_minutes(t1.time)
                end1 = start1 + t1.duration
                start2 = time_to_minutes(t2.time)
                end2 = start2 + t2.duration
                if start1 < end2 and start2 < end1:
                    end1_str = f"{end1 // 60:02d}:{end1 % 60:02d}"
                    end2_str = f"{end2 // 60:02d}:{end2 % 60:02d}"
                    msg = (
                        f"⚠️  TIME CONFLICT: {t1.name} ({t1.pet_name}) "
                        f"{t1.time}–{end1_str} overlaps with "
                        f"{t2.name} ({t2.pet_name}) {t2.time}–{end2_str}"
                    )
                    warnings.append(msg)
                    logger.warning("Conflict detected — %s vs %s at %s/%s",
                                   t1.name, t2.name, t1.time, t2.time)

        if not warnings:
            logger.info("Conflict check passed — no overlapping tasks")
        return warnings

    def add_task(self, task: Task):
        """Add a task to the schedule if it exists in the owner's tasks."""
        if task in self.owner.tasks:
            self.tasks.append(task)
            self.calculate_total_time()

    def remove_task(self, task: Task):
        """Remove a task from the schedule if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)
            self.calculate_total_time()

    def calculate_total_time(self):
        """Calculate total time used and remaining time."""
        self.total_time_used = sum(task.duration for task in self.tasks)
        self.remaining_time = self.owner.available_time_per_day - self.total_time_used
        if self.remaining_time < 0:
            logger.warning(
                "Schedule overbooked by %d min (used %d / available %d)",
                abs(self.remaining_time), self.total_time_used, self.owner.available_time_per_day,
            )

    def generate_reliability_report(self) -> dict:
        """Score the schedule's reliability on a 0.0–1.0 scale.

        Deductions:
          - 0.15 per conflict pair (max 0.45 total from conflicts)
          - 0.20 if schedule is overbooked
          - 1.0 → 0.0 if no tasks are scheduled at all

        Returns a dict with keys: confidence, task_count, conflict_count,
        total_time, available_time, issues, summary.
        """
        tasks = self.get_all_pet_tasks()
        conflicts = self.detect_time_conflicts()
        total_time = sum(t.duration for t in tasks)
        issues = []
        score = 1.0

        if not tasks:
            score = 0.0
            issues.append("No tasks scheduled")
        else:
            if conflicts:
                deduction = min(0.45, len(conflicts) * 0.15)
                score -= deduction
                issues.append(f"{len(conflicts)} overlapping task pair(s) detected")
            if total_time > self.owner.available_time_per_day:
                score -= 0.20
                overage = total_time - self.owner.available_time_per_day
                issues.append(f"Overbooked by {overage} min")

        score = round(max(0.0, score), 2)
        status = "Schedule looks reliable" if not issues else "; ".join(issues)
        summary = f"Confidence {score:.0%} — {status}"

        logger.info("Reliability report: confidence=%.2f, conflicts=%d, overbooked=%s",
                    score, len(conflicts), total_time > self.owner.available_time_per_day)
        return {
            "confidence": score,
            "task_count": len(tasks),
            "conflict_count": len(conflicts),
            "total_time": total_time,
            "available_time": self.owner.available_time_per_day,
            "issues": issues,
            "summary": summary,
        }

    def display_schedule(self):
        """Print the daily schedule details."""
        print("Daily Schedule:")
        for task in self.tasks:
            print(f"- {task.get_task_details()}")
        print(f"Total time used: {self.total_time_used} min")
        print(f"Remaining time: {self.remaining_time} min")
