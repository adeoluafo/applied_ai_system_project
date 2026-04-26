import streamlit as st
from pawpal_system import PetOwner, Pet, Task, Schedule
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Initialize PetOwner in session_state
if "owner" not in st.session_state:
    st.session_state.owner = PetOwner("Default Owner", 480, "No preferences set")

owner = st.session_state.owner

st.subheader("Owner Information")
col1, col2 = st.columns(2)
with col1:
    new_owner_name = st.text_input("Owner name", value=owner.name, key="owner_name_input")
    if new_owner_name != owner.name:
        owner.name = new_owner_name
with col2:
    new_available_time = st.number_input(
        "Available time (minutes/day)", 
        min_value=1, 
        max_value=1440, 
        value=owner.available_time_per_day,
        key="available_time_input"
    )
    if new_available_time != owner.available_time_per_day:
        owner.available_time_per_day = new_available_time

st.markdown("### Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"], key="species_select")
with col3:
    special_needs = st.text_input("Special needs", value="None", key="special_needs_input")

if st.button("Add Pet"):
    if pet_name:
        new_pet = Pet(pet_name, species, 1, special_needs)
        owner.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}!")
    else:
        st.error("Pet name cannot be empty.")

if owner.get_pets():
    st.write(f"**Owner's Pets ({len(owner.get_pets())}):**")
    for idx, pet in enumerate(owner.get_pets()):
        st.write(f"{idx + 1}. {pet.get_pet_info()}")
else:
    st.info("No pets added yet. Add one above.")

st.markdown("### Add Tasks to Pets")
if owner.get_pets():
    selected_pet = st.selectbox(
        "Select a pet",
        [pet.name for pet in owner.get_pets()],
        key="pet_select"
    )
    
    task_name = st.text_input("Task name", value="Morning walk", key="task_name_input")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30, key="duration_input")
    priority = st.selectbox("Priority", ["low", "medium", "high"], key="priority_select")
    category = st.selectbox("Category", ["feeding", "exercise", "grooming", "play", "medication"], key="category_select")
    
    if st.button("Add Task"):
        if task_name:
            new_task = Task(task_name, duration, priority, category, "daily")
            pet = next(p for p in owner.get_pets() if p.name == selected_pet)
            pet.add_task(new_task)
            st.success(f"Added '{task_name}' to {selected_pet}!")
        else:
            st.error("Task name cannot be empty.")
    
    st.markdown("#### Tasks by Pet")
    for pet in owner.get_pets():
        pet_tasks = pet.get_tasks()
        if pet_tasks:
            st.write(f"**{pet.name}:**")
            for task in pet_tasks:
                st.write(f"  - {task.get_task_details()}")
        else:
            st.write(f"**{pet.name}:** No tasks yet.")
else:
    st.info("Add a pet first to assign tasks.")



st.divider()

st.subheader("Generate Schedule")
st.caption("Build a daily schedule based on owner's available time and pet tasks.")

if st.button("📋 Generate Schedule", use_container_width=True):
    owner = st.session_state.owner
    schedule = Schedule(owner)
    
    # Get all tasks from pets
    all_pet_tasks = schedule.get_all_pet_tasks()
    
    if all_pet_tasks:
        st.success("✅ Schedule generated successfully!")
        
        # ============ RELIABILITY REPORT ============
        report = schedule.generate_reliability_report()
        confidence = report["confidence"]

        st.markdown("### 🔍 Schedule Reliability")
        col_score, col_summary = st.columns([1, 3])
        with col_score:
            st.metric("Confidence Score", f"{confidence:.0%}")
            st.progress(confidence)
        with col_summary:
            if confidence == 1.0:
                st.success(f"**{report['summary']}**")
            elif confidence >= 0.7:
                st.warning(f"**{report['summary']}**")
            else:
                st.error(f"**{report['summary']}**")
            if report["issues"]:
                for issue in report["issues"]:
                    st.markdown(f"- {issue}")

        # ============ CONFLICTS WARNING (PROMINENT) ============
        conflicts = report["conflict_count"]
        all_conflicts = schedule.detect_time_conflicts()
        if all_conflicts:
            with st.container(border=True):
                st.error("⚠️ **SCHEDULE CONFLICTS DETECTED**")
                for conflict in all_conflicts:
                    st.markdown(f"- {conflict}")
        else:
            with st.container(border=True):
                st.info("✅ **No time conflicts detected** — All tasks can run in parallel!")

        # ============ SUMMARY METRICS ============
        st.markdown("### 📊 Schedule Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        total_time = sum(t.duration for t in all_pet_tasks)
        pending = schedule.filter_tasks(completion_status="pending")
        completed = schedule.filter_tasks(completion_status="completed")
        
        with col1:
            st.metric("👤 Owner", owner.name)
        with col2:
            st.metric("📝 Total Tasks", len(all_pet_tasks))
        with col3:
            st.metric("⏱️ Total Duration", f"{total_time} min")
        with col4:
            st.metric("📅 Available Time", f"{owner.available_time_per_day} min")
        
        # ============ TIME CAPACITY INDICATOR ============
        st.markdown("### ⏲️ Time Capacity")
        capacity_percent = min(100, (total_time / owner.available_time_per_day) * 100)
        st.progress(capacity_percent / 100.0)
        
        if total_time > owner.available_time_per_day:
            st.error(
                f"🚨 **Overbooked by {total_time - owner.available_time_per_day} minutes!** "
                f"Tasks require {total_time} min but only {owner.available_time_per_day} available."
            )
        elif total_time == owner.available_time_per_day:
            st.success("✨ **Perfect fit!** All tasks fit exactly in available time.")
        else:
            remaining = owner.available_time_per_day - total_time
            st.success(f"✅ **{remaining} minutes of buffer time** available.")
        
        # ============ TABBED VIEWS ============
        tab1, tab2, tab3 = st.tabs(["📋 Sorted Schedule", "🐾 By Pet", "📊 Status Breakdown"])
        
        # TAB 1: SORTED SCHEDULE
        with tab1:
            st.markdown("#### Daily Schedule (Sorted by Time)")
            sorted_by_time = schedule.sort_by_time()
            
            if sorted_by_time:
                schedule_df_data = []
                for idx, task in enumerate(sorted_by_time, 1):
                    schedule_df_data.append({
                        "#": idx,
                        "🕐 Time": task.time,
                        "🐾 Pet": task.pet_name,
                        "📋 Task": task.name,
                        "⏱️ Duration": f"{task.duration} min",
                        "⭐ Priority": task.priority.upper(),
                        "🏷️ Category": task.category
                    })
                
                st.dataframe(
                    schedule_df_data, 
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "⭐ Priority": st.column_config.TextColumn(
                            help="Task priority level"
                        )
                    }
                )
        
        # TAB 2: BY PET
        with tab2:
            st.markdown("#### Tasks Grouped by Pet")
            
            for pet in owner.get_pets():
                pet_tasks = schedule.filter_tasks(pet_name=pet.name)
                
                if pet_tasks:
                    with st.expander(f"🐾 {pet.name} — {len(pet_tasks)} tasks", expanded=True):
                        pet_table_data = []
                        for task in sorted(pet_tasks, key=lambda t: t.time):
                            pet_table_data.append({
                                "🕐 Time": task.time,
                                "📋 Task": task.name,
                                "⏱️ Duration": f"{task.duration} min",
                                "⭐ Priority": task.priority,
                                "👁️ Status": task.completion_status
                            })
                        
                        st.table(pet_table_data)
                else:
                    st.info(f"No tasks assigned to {pet.name}")
        
        # TAB 3: STATUS BREAKDOWN
        with tab3:
            st.markdown("#### Task Status Overview")
            
            col1, col2, col3 = st.columns(3)
            in_progress = schedule.filter_tasks(completion_status="in_progress")
            
            with col1:
                st.metric(
                    "⏸️ Pending",
                    len(pending),
                    delta=f"{sum(t.duration for t in pending)} min"
                )
            with col2:
                st.metric(
                    "▶️ In Progress",
                    len(in_progress),
                    delta=f"{sum(t.duration for t in in_progress)} min"
                )
            with col3:
                st.metric(
                    "✅ Completed",
                    len(completed),
                    delta=f"{sum(t.duration for t in completed)} min"
                )
            
            # Status breakdown table
            if pending or in_progress or completed:
                st.markdown("---")
                st.markdown("##### Task Details by Status")
                
                status_data = []
                for task in all_pet_tasks:
                    status_emoji = {
                        "pending": "⏸️",
                        "in_progress": "▶️",
                        "completed": "✅"
                    }.get(task.completion_status, "❓")
                    
                    status_data.append({
                        "Status": f"{status_emoji} {task.completion_status}",
                        "📝 Task": task.name,
                        "🐾 Pet": task.pet_name,
                        "⏱️ Duration": f"{task.duration} min",
                        "⭐ Priority": task.priority
                    })
                
                st.dataframe(status_data, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ No tasks found. Add tasks to pets first.")
