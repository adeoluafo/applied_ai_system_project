import unittest
from datetime import datetime, timedelta
from pawpal_system import PetOwner, Pet, Task, Schedule

class TestPawPal(unittest.TestCase):

    def test_pet_add_task(self):
        """Test that a task can be added to a pet."""
        pet = Pet("Buddy", "Dog", 3, "None")
        task = Task("Walk", 30, "high", "exercise", "daily")
        pet.add_task(task)
        self.assertIn(task, pet.get_tasks())
        self.assertEqual(len(pet.get_tasks()), 1)

    def test_schedule_get_all_pet_tasks(self):
        """Test that Schedule can retrieve all tasks from owner's pets."""
        owner = PetOwner("Alice", 480, "None")
        pet1 = Pet("Buddy", "Dog", 3, "None")
        pet2 = Pet("Whiskers", "Cat", 2, "None")
        task1 = Task("Walk", 30, "high", "exercise", "daily")
        task2 = Task("Feed", 15, "medium", "feeding", "daily")
        pet1.add_task(task1)
        pet2.add_task(task2)
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        schedule = Schedule(owner)
        all_tasks = schedule.get_all_pet_tasks()
        self.assertEqual(len(all_tasks), 2)
        self.assertIn(task1, all_tasks)

    def test_task_completion(self):
        """Verify that updating completion status changes the task's status."""
        task = Task("Walk", 30, "high", "exercise", "daily")
        self.assertEqual(task.completion_status, "pending")
        task.update_completion_status("completed")
        self.assertEqual(task.completion_status, "completed")

    def test_task_addition_to_pet(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        pet = Pet("Buddy", "Dog", 3, "None")
        initial_count = len(pet.get_tasks())
        task = Task("Walk", 30, "high", "exercise", "daily")
        pet.add_task(task)
        self.assertEqual(len(pet.get_tasks()), initial_count + 1)

    # ============ SORTING CORRECTNESS TESTS ============
    def test_sort_by_time_chronological_order(self):
        """Verify tasks are returned in chronological order by time."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        # Create tasks in random order
        task1 = Task("Lunch", 30, "medium", "feeding", "daily", "12:00", "pending", "Buddy", datetime.now())
        task2 = Task("Walk", 30, "high", "exercise", "daily", "08:00", "pending", "Buddy", datetime.now())
        task3 = Task("Playtime", 45, "low", "play", "daily", "18:00", "pending", "Buddy", datetime.now())
        task4 = Task("Breakfast", 20, "medium", "feeding", "daily", "07:00", "pending", "Buddy", datetime.now())
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        pet.add_task(task4)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        sorted_tasks = schedule.sort_by_time()
        
        # Verify order
        expected_order = ["07:00", "08:00", "12:00", "18:00"]
        actual_order = [task.time for task in sorted_tasks]
        self.assertEqual(actual_order, expected_order)

    def test_sort_by_time_same_time_stability(self):
        """Verify tasks with same time maintain consistent ordering."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        # Create multiple tasks at same time
        task1 = Task("Walk", 30, "high", "exercise", "daily", "08:00", "pending", "Buddy", datetime.now())
        task2 = Task("Brushing", 20, "medium", "grooming", "daily", "08:00", "pending", "Buddy", datetime.now())
        task3 = Task("Medication", 5, "high", "medication", "daily", "08:00", "pending", "Buddy", datetime.now())
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        sorted_tasks = schedule.sort_by_time()
        
        # All should have same time
        self.assertTrue(all(task.time == "08:00" for task in sorted_tasks))
        self.assertEqual(len(sorted_tasks), 3)

    def test_sort_by_time_empty_task_list(self):
        """Verify sorting empty task list returns empty list."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        sorted_tasks = schedule.sort_by_time()
        
        self.assertEqual(len(sorted_tasks), 0)

    def test_sort_by_time_midnight_boundary(self):
        """Verify sorting handles midnight and early morning tasks correctly."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        task1 = Task("Late night", 30, "low", "play", "daily", "23:59", "pending", "Buddy", datetime.now())
        task2 = Task("Midnight", 10, "low", "play", "daily", "00:00", "pending", "Buddy", datetime.now())
        task3 = Task("Early", 20, "low", "play", "daily", "00:30", "pending", "Buddy", datetime.now())
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        sorted_tasks = schedule.sort_by_time()
        
        expected_order = ["00:00", "00:30", "23:59"]
        actual_order = [task.time for task in sorted_tasks]
        self.assertEqual(actual_order, expected_order)

    def test_sort_by_time_single_task(self):
        """Verify sorting a single task returns that task."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        task = Task("Walk", 30, "high", "exercise", "daily", "10:00", "pending", "Buddy", datetime.now())
        
        pet.add_task(task)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        sorted_tasks = schedule.sort_by_time()
        
        self.assertEqual(len(sorted_tasks), 1)
        self.assertEqual(sorted_tasks[0].name, "Walk")

    # ============ RECURRENCE LOGIC TESTS ============
    def test_recurring_daily_task_creates_next_day(self):
        """Confirm that marking a daily task complete creates a new task for the following day."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        today = datetime.now()
        task = Task("Feeding", 15, "high", "feeding", "daily", "12:00", "pending", "Buddy", today)
        
        pet.add_task(task)
        owner.add_pet(pet)
        schedule = Schedule(owner)
        
        initial_count = len(schedule.get_all_pet_tasks())
        schedule.mark_task_complete(task)
        final_count = len(schedule.get_all_pet_tasks())
        
        # Should have one more task (the recurring one)
        self.assertEqual(final_count, initial_count + 1)
        
        # Verify the new task has next day's due date
        all_tasks = schedule.get_all_pet_tasks()
        new_task = None
        for t in all_tasks:
            if t.name == "Feeding" and t.completion_status == "pending":
                new_task = t
                break
        
        self.assertIsNotNone(new_task)
        expected_due_date = today + timedelta(days=1)
        self.assertEqual(new_task.due_date.date(), expected_due_date.date())

    def test_recurring_weekly_task_creates_next_week(self):
        """Confirm that marking a weekly task complete creates a new task for the following week."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        today = datetime.now()
        task = Task("Grooming", 60, "medium", "grooming", "weekly", "14:00", "pending", "Buddy", today)
        
        pet.add_task(task)
        owner.add_pet(pet)
        schedule = Schedule(owner)
        
        initial_count = len(schedule.get_all_pet_tasks())
        schedule.mark_task_complete(task)
        final_count = len(schedule.get_all_pet_tasks())
        
        # Should have one more task
        self.assertEqual(final_count, initial_count + 1)
        
        # Verify the new task has next week's due date
        all_tasks = schedule.get_all_pet_tasks()
        new_task = None
        for t in all_tasks:
            if t.name == "Grooming" and t.completion_status == "pending":
                new_task = t
                break
        
        self.assertIsNotNone(new_task)
        expected_due_date = today + timedelta(weeks=1)
        self.assertEqual(new_task.due_date.date(), expected_due_date.date())

    def test_recurring_task_preserves_properties(self):
        """Verify that recurring tasks preserve all properties from the original task."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        today = datetime.now()
        task = Task("Medication", 5, "high", "medication", "daily", "09:00", "pending", "Buddy", today)
        
        pet.add_task(task)
        owner.add_pet(pet)
        schedule = Schedule(owner)
        
        schedule.mark_task_complete(task)
        
        # Find the new recurring task
        all_tasks = schedule.get_all_pet_tasks()
        new_task = None
        for t in all_tasks:
            if t.name == "Medication" and t.completion_status == "pending":
                new_task = t
                break
        
        self.assertIsNotNone(new_task)
        # Verify properties match
        self.assertEqual(new_task.name, task.name)
        self.assertEqual(new_task.duration, task.duration)
        self.assertEqual(new_task.priority, task.priority)
        self.assertEqual(new_task.category, task.category)
        self.assertEqual(new_task.time, task.time)
        self.assertEqual(new_task.pet_name, task.pet_name)

    def test_non_recurring_task_does_not_create_new_task(self):
        """Verify that completing a non-recurring task does not create a new task."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        today = datetime.now()
        task = Task("Vet Appointment", 30, "high", "health", "once", "10:00", "pending", "Buddy", today)
        
        pet.add_task(task)
        owner.add_pet(pet)
        schedule = Schedule(owner)
        
        initial_count = len(schedule.get_all_pet_tasks())
        schedule.mark_task_complete(task)
        final_count = len(schedule.get_all_pet_tasks())
        
        # Should have same count (no new task created)
        self.assertEqual(final_count, initial_count)

    def test_multiple_recurring_completions(self):
        """Verify that marking a recurring task complete multiple times generates multiple instances."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        today = datetime.now()
        task = Task("Feeding", 15, "high", "feeding", "daily", "12:00", "pending", "Buddy", today)
        
        pet.add_task(task)
        owner.add_pet(pet)
        schedule = Schedule(owner)
        
        # Mark complete twice
        schedule.mark_task_complete(task)
        all_tasks = schedule.get_all_pet_tasks()
        next_task = None
        for t in all_tasks:
            if t.name == "Feeding" and t.completion_status == "pending":
                next_task = t
                break
        
        self.assertIsNotNone(next_task)
        schedule.mark_task_complete(next_task)
        
        # Should have 3 tasks now (original completed + 2 recurring)
        final_tasks = schedule.get_all_pet_tasks()
        self.assertEqual(len(final_tasks), 3)

    # ============ CONFLICT DETECTION TESTS ============
    def test_detect_time_conflicts_multiple_at_same_time(self):
        """Verify that the scheduler flags duplicate times."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        task1 = Task("Walk", 30, "high", "exercise", "daily", "08:00", "pending", "Buddy", datetime.now())
        task2 = Task("Brushing", 20, "medium", "grooming", "daily", "08:00", "pending", "Buddy", datetime.now())
        
        pet.add_task(task1)
        pet.add_task(task2)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        conflicts = schedule.detect_time_conflicts()
        
        # Should detect a conflict
        self.assertGreater(len(conflicts), 0)
        self.assertIn("08:00", conflicts[0])

    def test_detect_time_conflicts_multiple_pets_same_time(self):
        """Verify conflicts are detected across multiple pets at same time."""
        owner = PetOwner("Alice", 480, "None")
        pet1 = Pet("Buddy", "Dog", 3, "None")
        pet2 = Pet("Whiskers", "Cat", 2, "None")
        
        task1 = Task("Walk", 30, "high", "exercise", "daily", "09:00", "pending", "Buddy", datetime.now())
        task2 = Task("Playtime", 45, "low", "play", "daily", "09:00", "pending", "Whiskers", datetime.now())
        
        pet1.add_task(task1)
        pet2.add_task(task2)
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        schedule = Schedule(owner)
        conflicts = schedule.detect_time_conflicts()
        
        self.assertGreater(len(conflicts), 0)
        self.assertIn("Buddy", conflicts[0])
        self.assertIn("Whiskers", conflicts[0])

    def test_detect_time_conflicts_three_way_conflict(self):
        """Verify detection of three or more tasks at the same time."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        task1 = Task("Walk", 30, "high", "exercise", "daily", "10:00", "pending", "Buddy", datetime.now())
        task2 = Task("Feeding", 15, "medium", "feeding", "daily", "10:00", "pending", "Buddy", datetime.now())
        task3 = Task("Medication", 5, "high", "medication", "daily", "10:00", "pending", "Buddy", datetime.now())
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        conflicts = schedule.detect_time_conflicts()
        
        self.assertGreater(len(conflicts), 0)
        # Should mention all three tasks
        conflict_msg = conflicts[0]
        self.assertIn("Walk", conflict_msg)
        self.assertIn("Feeding", conflict_msg)
        self.assertIn("Medication", conflict_msg)

    def test_detect_time_conflicts_no_conflicts(self):
        """Verify no conflicts are flagged when tasks have different times."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        task1 = Task("Walk", 30, "high", "exercise", "daily", "08:00", "pending", "Buddy", datetime.now())
        task2 = Task("Feeding", 15, "medium", "feeding", "daily", "12:00", "pending", "Buddy", datetime.now())
        task3 = Task("Playtime", 45, "low", "play", "daily", "18:00", "pending", "Buddy", datetime.now())
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        conflicts = schedule.detect_time_conflicts()
        
        self.assertEqual(len(conflicts), 0)

    def test_detect_time_conflicts_empty_schedule(self):
        """Verify no conflicts on empty schedule."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        conflicts = schedule.detect_time_conflicts()
        
        self.assertEqual(len(conflicts), 0)

    def test_detect_time_conflicts_single_task(self):
        """Verify no conflicts with only one task."""
        owner = PetOwner("Alice", 480, "None")
        pet = Pet("Buddy", "Dog", 3, "None")
        
        task = Task("Walk", 30, "high", "exercise", "daily", "08:00", "pending", "Buddy", datetime.now())
        pet.add_task(task)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        conflicts = schedule.detect_time_conflicts()
        
        self.assertEqual(len(conflicts), 0)
