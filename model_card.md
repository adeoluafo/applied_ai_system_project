# PawPal+ Project Reflection

## 1. System Design
- A user should enter basic owner + pet info
- A user should be able add/edit tasks (duration + priority at minimum)
- Daily schedule/plan based on constraints and priorities


**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Answer:
1. PetOwner

Attributes:

name
available_time_per_day (in minutes or hours)
preferences (e.g., preferred walk times, task priorities)

Methods:

add_task(task)
remove_task(task)
get_tasks()

2. Pet

Attributes:

name
type (dog, cat, etc.)
age
special_needs (e.g., medication, diet)

Methods:

get_pet_info()

3. Task

(This is the most important object)

Attributes:

name (e.g., “Morning Walk”)
duration (in minutes)
priority (e.g., high, medium, low OR numeric)
category (feeding, walking, grooming, etc.)
frequency (daily, weekly)

Methods:

update_priority(new_priority)
update_duration(new_duration)
get_task_details()

4. Schedule

(Represents the daily plan)

Attributes:

tasks (list of Task objects)
total_time_used
remaining_time

Methods:

add_task(task)
remove_task(task)
calculate_total_time()
display_schedule()


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Answer:
- Added `self.pets = []` in `PetOwner.__init__()` to store a list of `Pet` objects.
- Added methods: `add_pet(pet: Pet)`, `remove_pet(pet: Pet)`, and `get_pets()` to manage pets.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Answer
 - Real time windows
 - total time availability
 - task importance
 - recurring cycle semantics
  - conflict/no-overlap warnings
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Answer:
 - speed over perfect optimization
 - The tradeoff is reasonable because it keeps the product usable now, while still being easy to extend later.
## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

Answer:
I used Ai to specify design logics and debugging
-specifying files using the '#' symbol was really helpful

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Answer:
 - There was a time when i made a mistake with a prompt. The AI generated a false suggestion in which I could not accept

 - I verfiying by comparing what I originally had and the suggested code given to see where the problem was
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Answer:
- Sorting by time, Conflict detection
 - It ensures schedule is chronologial, so owners day actually flows
  - To prevent impossible schedules (two tasks at same time)

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---
Answer:
-Due to all the tests cases passed, I am 100% confident
 - a test case would be 'No task at all' case

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
Answer:
I am most satisfied with the UML diagram which guided me 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Answer: 
I would improve the schedule optimezer by upgrading to a constrained selection algorithm (knapsack-like with priority-weighted scoring) to maximize coverage within

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Answer:
Ai is a great assistant when it is given the right prompt. 

## Reflection continued

### What this project taught me about AI

Working on PawPal+ changed how I think about the role of AI in software development. The most valuable use was not generating code — it was using AI as a design sounding board. Describing a scheduling problem in natural language and getting back a structured class diagram helped me identify responsibilities I had not thought to separate (for example, keeping `Task.create_recurring_task()` as a method on `Task` rather than inside `Schedule`, which made it independently testable).

The moment I learned the most from was when an AI suggestion introduced a subtle bug: it grouped conflict detection by start time, which looked correct for the test cases I had at the time but missed duration-overlap conflicts entirely. Catching this required understanding the real-world semantics of the problem (two tasks can't physically happen at the same time even if they start at different times) rather than just reading the code. That distinction — between code that passes tests and code that solves the actual problem — is something only human judgment can provide.

### What I would improve next

1. **Priority-weighted scheduler**: Implement a greedy or knapsack-style algorithm that, when the owner is overbooked, automatically selects the highest-value subset of tasks that fits within available time — surfacing what gets dropped and why.
2. **Persistent storage**: Replace in-memory session state with a lightweight database (SQLite via SQLModel) so schedules survive page refreshes and can be reviewed across days.
3. **Streamlit UI tests**: Use `streamlit.testing.v1` to write integration tests that simulate button clicks and verify that the rendered output matches the domain model's state.
4. **Natural language task entry**: Let owners type "walk Buddy for 30 minutes at 8am every day" and parse it into a structured `Task` — a practical use of an LLM as a parsing layer rather than a reasoning engine.

### Final takeaway

Reliability is not a feature you bolt on after the fact — it is a property you design for. Adding `Task.__post_init__` validation, duration-aware conflict detection, structured logging, a confidence-scoring engine, and a fixture-backed test suite did not change what PawPal+ does; it changed how confidently — and measurably — I can say it does it correctly.

### What are the limitations or biases in your system?

**Scheduling biases**

- `sort_by_time()` orders tasks chronologically, not by priority. A low-priority playtime at 07:00 always appears before a high-priority medication at 12:00 — the schedule never reorders to surface urgent tasks first.
- Tasks created without an explicit time default to `"00:00"`, so they silently sort first in the daily view even though they have no real scheduled time.
- Conflict detection flags overlaps but never suggests a resolution or alternative slot. The owner must figure out manually where to move a conflicting task.
- The system assumes zero multitasking. Two tasks that could realistically overlap (e.g., a 5-min medication while food is cooking) receive the same conflict warning as genuinely impossible simultaneous tasks.

**Confidence scoring biases**

- The −0.15/conflict and −0.20/overbooked deductions are arbitrary heuristics, not derived from data or user research.
- Penalties are priority-blind: a conflict between two "low" priority grooming tasks deducts the same amount as a conflict involving a "high" priority medication.
- An empty schedule scores 0.0, which conflates a legitimate rest day with a broken schedule.

### Could your AI be misused, and how would you prevent that?

**Yes —realistic misuse vectors exist in the current system.**

**1. Medical over-trust in the confidence score**

`generate_reliability_report()` scores 1.0 when there are no scheduling conflicts and the schedule fits within available time. A user could see "Confidence 100%" on a medication schedule and interpret that as veterinary assurance the timing is safe — when the system has no knowledge of dosing intervals, drug interactions, or species-specific care requirements. A task named "Insulin injection" at the wrong interval scores 1.0 if it has no time conflict.

*Prevention:* The confidence score description in the UI should explicitly state what it measures ("no overlapping time windows, within daily capacity") and carry a disclaimer: *"This schedule is a time-management tool only — consult a veterinarian for medical task timing."*

### What surprised you while testing your AI's reliability?

**1. Twenty passing tests hid a real bug.**

The original test suite had 20 tests and all of them passed. That felt like strong coverage — until writing `test_detect_duration_based_overlap`, which created a 60-minute walk at 08:00 and a feeding at 08:30. The original `detect_time_conflicts()` reported no conflict because it only grouped tasks by identical start time. The bug had existed since the first commit and no existing test caught it because every conflict test happened to use the same start time. Passing tests and correct behavior turned out to be two different things.

**2. Fixing the conflict detector broke a different test.**

After switching to pairwise window comparison, `test_detect_three_way_conflict` — a test that had passed before — suddenly failed. The old grouped-message format put all three conflicting task names in a single string; the new pairwise format produces one warning per pair, so `conflicts[0]` only contained two names. The test was accidentally testing the *format* of the output rather than the *behavior* it claimed to test. Rewriting it to check `" ".join(conflicts)` made it genuinely test what it said it was testing.

### AI Collaboration

AI was used throughout this project for three distinct purposes: initial class design, debugging logic errors, and generating test scaffolding. The most effective prompting technique was using the `#` symbol to reference specific files directly — asking the AI to look at `#pawpal_system.py` and suggest improvements produced far more precise responses than describing the code in prose.

**One instance where the AI gave a helpful suggestion**

During the Module 4 upgrade, I asked the AI how to eliminate the boilerplate setup code that appeared at the top of every test — each test was constructing a `PetOwner`, a `Pet`, and a `Task` from scratch before doing anything meaningful. The AI suggested creating a `tests/conftest.py` file with pytest fixtures scoped to the function level, so each test receives a guaranteed-fresh object as an argument rather than building it manually. This was the right call. It reduced the average test from ~10 lines to ~4, made each test's dependencies explicit in its signature, and meant that adding a new test scenario required almost no setup code. I accepted the suggestion and it improved the entire test suite.

**One instance where the AI suggestion was flawed or incorrect**

The original `detect_time_conflicts()` implementation — which the AI helped design — grouped all tasks by their start time string and flagged any group with more than one task. This looked correct and passed all the conflict tests at the time. The flaw was that it only caught tasks scheduled at the *identical* start time. A 60-minute walk at 08:00 and a feeding at 08:30 — tasks that physically cannot both be done simultaneously — produced no warning at all.

### What I learned

Writing tests before finding the blind spots forced me to think about what the code actually promises, not just what it does in the happy path. The duration-overlap bug had existed since the original implementation but was invisible because all early tests used identical start times. Writing a new scenario-driven test (`test_detect_duration_based_overlap`) was what revealed it — the production fix followed in two lines.

Confidence scoring turned out to be more useful than I expected. A score of 0.85 communicates more to an owner than a list of warning strings, and testing the score forced me to define what "reliable" means in numbers rather than words.

**Reflection**
What this project says about me as an AI engineer?:

-This project identifies my progressive thinking when it comes to designing systems. In this project, i had the option to choose between three Ai implementation features namely: RAG, Agentic workflow, Fine-tuned or specialized model and Reliability or Testing systems. I made sure my approach identified the prons and cons to on each feature and the time trade offs too. I finally was able to use Reliability or Testing systems. 

Decisions like this require a flexible way of thinking when it comes to approaching problems. As an AI engineer, I was able to utilize AI models to achieve most tasks, understand codes and reduce time cost. 