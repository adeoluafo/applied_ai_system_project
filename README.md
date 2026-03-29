# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Running Tests

Execute the test suite with:

```bash
python -m pytest tests/test_pawpal.py -v
```

### Test Coverage

The test suite includes **20 comprehensive tests** covering three critical areas:

1. **Sorting Correctness (5 tests)**
   - Chronological task ordering by time
   - Stable sorting for simultaneous tasks
   - Edge cases: midnight boundaries, empty schedules, single tasks

2. **Recurrence Logic (5 tests)**
   - Daily tasks create next-day instances
   - Weekly tasks create next-week instances
   - Properties preserved across recurring generations
   - Non-recurring tasks do not spawn duplicates
   - Multiple sequential completions handled correctly

3. **Conflict Detection (6 tests)**
   - Multiple tasks at same time flagged for same pet
   - Cross-pet conflicts detected
   - Three-way+ collisions identified
   - No false positives on staggered schedules
   - Edge cases: empty schedules, single tasks

4. **Core Functionality (4 tests)**
   - Pet task management
   - Task completion status updates
   - Multi-pet task retrieval
   - Task assignment to pets

### Confidence Level: ⭐⭐⭐⭐ (4/5 stars)

**Rationale:**
- ✅ All 20 tests pass consistently
- ✅ Key scheduling behaviors validated (sorting, recurrence, conflicts)
- ✅ Edge cases covered (midnight, empty schedules, multiple conflicts)
- ⚠️ Integration with Streamlit UI not yet tested
- ⚠️ Performance and scalability not yet benchmarked (100+ tasks)
- ⚠️ Invalid input edge cases (malformed times, invalid priorities) need additional coverage

