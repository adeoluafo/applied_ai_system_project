// PawPal+ System UML Class Diagram
// This diagram shows the class structure and relationships in the pet scheduling system

const pawpalUML = `classDiagram
    class Pet {
        - name: str
        - type: str
        - age: int
        - special_needs: str
        - tasks: List~Task~
        + __post_init__(): void
        + get_pet_info(): str
        + add_task(task: Task): void
        + remove_task(task: Task): void
        + get_tasks(): List~Task~
    }

    class Task {
        - name: str
        - duration: int
        - priority: str
        - category: str
        - frequency: str
        - time: str
        - completion_status: str
        - pet_name: str
        - due_date: datetime
        + update_priority(new_priority: str): void
        + update_duration(new_duration: int): void
        + update_completion_status(new_status: str): void
        + create_recurring_task(): Task
        + get_task_details(): str
    }

    class PetOwner {
        - name: str
        - available_time_per_day: int
        - preferences: str
        - tasks: List~Task~
        - pets: List~Pet~
        + add_task(task: Task): void
        + remove_task(task: Task): void
        + get_tasks(): List~Task~
        + add_pet(pet: Pet): void
        + remove_pet(pet: Pet): void
        + get_pets(): List~Pet~
    }

    class Schedule {
        - owner: PetOwner
        - tasks: List~Task~
        - total_time_used: int
        - remaining_time: int
        + get_all_pet_tasks(): List~Task~
        + sort_by_time(): List~Task~
        + filter_tasks(completion_status: str, pet_name: str): List~Task~
        + mark_task_complete(task: Task): void
        + detect_time_conflicts(): List~str~
        + add_task(task: Task): void
        + remove_task(task: Task): void
        + calculate_total_time(): void
        + display_schedule(): void
    }

    Pet "1" --> "*" Task : contains
    PetOwner "1" --> "*" Pet : owns
    PetOwner "1" --> "*" Task : manages
    Schedule "1" --> "1" PetOwner : schedules for
    Schedule "1" --> "*" Task : aggregates`;

export default pawpalUML;
