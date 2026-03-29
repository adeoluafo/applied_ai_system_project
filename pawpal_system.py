from dataclasses import dataclass

@dataclass
class Pet:
    name: str
    type: str
    age: int
    special_needs: str

    def get_pet_info(self) -> str:
        return f"{self.name} is a {self.age}-year-old {self.type} with special needs: {self.special_needs}"

@dataclass
class Task:
    name: str
    duration: int
    priority: str
    category: str
    frequency: str

    def update_priority(self, new_priority: str):
        self.priority = new_priority

    def update_duration(self, new_duration: int):
        self.duration = new_duration

    def get_task_details(self) -> str:
        return f"Task: {self.name}, Duration: {self.duration} min, Priority: {self.priority}, Category: {self.category}, Frequency: {self.frequency}"

class PetOwner:
    def __init__(self, name: str, available_time_per_day: int, preferences: str):
        self.name = name
        self.available_time_per_day = available_time_per_day
        self.preferences = preferences
        self.tasks = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task: Task):
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self):
        return self.tasks

class Schedule:
    def __init__(self):
        self.tasks = []
        self.total_time_used = 0
        self.remaining_time = 0

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.calculate_total_time()

    def remove_task(self, task: Task):
        if task in self.tasks:
            self.tasks.remove(task)
            self.calculate_total_time()

    def calculate_total_time(self):
        self.total_time_used = sum(task.duration for task in self.tasks)
        # Assuming remaining_time is based on some total, but not specified, so set to 0 or calculate differently
        self.remaining_time = 0  # Placeholder

    def display_schedule(self):
        print("Daily Schedule:")
        for task in self.tasks:
            print(f"- {task.get_task_details()}")
        print(f"Total time used: {self.total_time_used} min")
        print(f"Remaining time: {self.remaining_time} min")
