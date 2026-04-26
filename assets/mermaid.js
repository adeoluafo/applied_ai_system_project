// PawPal+ System Architecture Diagram
// Flowchart showing actual data flow: input → processing → output
// Matches implementation in app.py and pawpal_system.py

export const pawpalArchitecture = `flowchart TD

    subgraph UI["🖥️  UI Layer — app.py (Streamlit)"]
        A1[Owner Info\\nname · available_time_per_day]
        A2[Pet Info\\nname · type · age · special_needs]
        A3[Task Details\\nname · duration · priority · time · frequency]
        A4([Generate Schedule Button])
    end

    subgraph VAL["🛡️  Input Validator — Task.__post_init__"]
        V1{Valid?\\npriority ∈ high/medium/low\\nfrequency ∈ daily/weekly/once\\nduration > 0\\ntime HH:MM format}
    end

    subgraph STORE["💾  Session Store — st.session_state"]
        S1[(PetOwner object\\n+ pets list\\n+ tasks per pet)]
    end

    subgraph ENGINE["⚙️  Schedule Engine — Schedule class"]
        E1[Retrieval\\nget_all_pet_tasks]
        E2[Sort\\nsort_by_time]
        E3[Filter\\nfilter_tasks]
        E4[Capacity\\ncalculate_total_time]
        E5[Conflict Detector\\ndetect_time_conflicts\\npairwise window overlap]
        E6[Recurrence Engine\\nmark_task_complete\\ncreate_recurring_task]
    end

    subgraph EVAL["📊  Reliability Evaluator — generate_reliability_report"]
        R1[Confidence Score 0.0–1.0\\n−0.15 per conflict pair\\n−0.20 if overbooked]
        R2[Issue List\\nconflicts · overbooking]
        R3[Human-readable Summary]
    end

    subgraph LOG["📋  Logger — logging.getLogger pawpal"]
        L1[INFO\\ntask completed · recurring task queued\\nconflict check passed · report score]
        L2[WARNING\\nconflict detected · schedule overbooked]
    end

    subgraph OUT["📤  Output Display — Streamlit"]
        O1[Reliability Score + Progress Bar]
        O2[Conflict Warnings]
        O3[Sorted Schedule Table]
        O4[Capacity Indicator + Overbook Alert]
        O5[Per-pet Task Breakdown]
        O6[Status Breakdown Tab]
    end

    subgraph TEST["🧪  Test Suite — pytest  tests/"]
        T1[conftest.py\\nshared fixtures]
        T2[64 automated tests\\nsorting · recurrence · conflicts\\nvalidation · capacity · confidence]
    end

    %% --- INPUT FLOW ---
    A1 & A2 --> STORE
    A3 --> VAL
    VAL -->|valid| STORE
    VAL -->|invalid| ERR[ValueError raised\\nrejected at input boundary]

    %% --- SCHEDULE GENERATION TRIGGERED BY BUTTON ---
    A4 --> E1
    STORE --> E1

    %% --- SCHEDULE ENGINE INTERNAL FLOW ---
    E1 --> E2
    E1 --> E3
    E1 --> E4
    E1 --> E5
    E1 --> E6
    E6 -->|new recurring task appended| STORE

    %% --- EVALUATOR READS ENGINE OUTPUTS ---
    E1 --> EVAL
    E4 --> EVAL
    E5 --> EVAL
    R1 & R2 & R3 --> O1

    %% --- OUTPUTS ---
    E5 --> O2
    E2 --> O3
    E4 --> O4
    E3 --> O5
    E3 --> O6

    %% --- LOGGING ---
    E6 --> L1
    E5 --> L2
    E4 --> L2
    EVAL --> L1

    %% --- TEST SUITE VALIDATES ALL LAYERS ---
    T1 --> T2
    T2 -. validates .-> VAL
    T2 -. validates .-> ENGINE
    T2 -. validates .-> EVAL
`;


// PawPal+ UML Class Diagram
// Shows class structure and relationships as implemented in pawpal_system.py

export const pawpalClassDiagram = `classDiagram
    class Pet {
        - name: str
        - type: str
        - age: int
        - special_needs: str
        - tasks: List~Task~
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
        + __post_init__(): void
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
        + filter_tasks(completion_status, pet_name): List~Task~
        + mark_task_complete(task: Task): void
        + detect_time_conflicts(): List~str~
        + add_task(task: Task): void
        + remove_task(task: Task): void
        + calculate_total_time(): void
        + generate_reliability_report(): dict
        + display_schedule(): void
    }

    Pet "1" --> "*" Task : contains
    PetOwner "1" --> "*" Pet : owns
    PetOwner "1" --> "*" Task : manages
    Schedule "1" --> "1" PetOwner : schedules for
    Schedule "1" --> "*" Task : aggregates
`;
