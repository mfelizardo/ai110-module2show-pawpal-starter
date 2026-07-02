# PawPal+ Project Reflection

## 1. System Design

3 Core Actions
1. User should be able to enter their own personal info (ex. name) and info relating to their pet (ex. pet name, breed)
2. User should be able to add or edit tasks for their pet. An example task could be "walking their pet". Each task should have at least a specified duration and priority 
3. User should be able to generate and see a daily schedule based on the tasks assigned to their pet (prioritizing tasks with higher priority)

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial UML design should have at least 4 objects, Pet Owner, Pet, Task, and Schedule.
- The Pet Owner (or Owner) class should contain 
  - attributes: name and a Pet object
  - methods: edit name, edit basic pet info (ex. pet name), add task, edit task, generate daily schedule
- The Pet class should contain
  - attributes: name, breed, and list of Tasks
  - methods: None
- The Task class should contain
  - attributes: task name, duration, priority
  - methods: None
- The Schedule class should contain
  - attributes: pet name, pet breed, and properly ordered list of Tasks sorted by Task priority (all provided by a Pet object)
  - methods: None


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I did make multiple design changes, thanks to the feedback from my AI Agent. One change that was made was changing the relationship of Owner --> Pet from one-to-one to one-to-many. As a result, the Owner class no longer has an attribute for only one Pet, but a list to support multiple Pets. This change makes sense because it is unreasonable to believe that all Owners who would like to use the app only have one pet. Another change was the addition of the ID fields for Task and Pet objects, in order to properly identify seperate objects, since for example it is unlikely but not impossible for an Owner to have more than 1 pet with the same name, breed, and task list so an ID field will help reference the correct one when needed.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers a fixed day window (08:00-20:00), each task's duration, whether a task has a fixed due_time (or a list of due_times for recurring tasks), each task's priority, and whether a task is marked concurrent_ok (allowed to overlap with other concurrent_ok tasks, e.g. things that can be multi-tasked like feeding multiple pets). Fixed due times are treated as hard constraints and are never moved, since they can represent real commitments like a vet appointment. Everything without a fixed time is "flexible" and gets auto-assigned a slot: those flexible tasks are sorted by descending priority first, so the more important tasks claim their preferred (earliest, or evenly-spread for recurring tasks) slot before lower-priority tasks are fit in around them. I decided fixed times mattered most because they're hard inputs given by the pet owners, with priority being next important. Fixed due_times that have schedule conflicts will be properly alerted to the app user so they can decide to make their own adjustments.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is that the scheduler assigns flexible tasks greedily, one at a time in priority order, rather than searching for a globally optimal arrangement of the whole day. Once a higher-priority task claims a slot, that slot is locked in and every lower-priority task has to schedule around it, even if some other combination would have fit everyone with less nudging. This is reasonable for this scenario because a pet owner's daily task list shouldn't be too large (a handful of tasks per pet), so there's rarely enough contention for the greedy choice to differ meaningfully from an optimal one, and the greedy approach is fast, simple to reason about, and produces a schedule where it's obvious to the user why a task landed at a given time (it either had a fixed due_time, or it took the best remaining slot after higher-priority tasks were placed).

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI tools in multiple steps of this project including: 
- design brainstorming and creating the UML diagram
- implementing the algorithms of the backend pawpal methods such as the `Scheduler.assign_schedule` method
- creating pytests to verify that the algorithms worked properly
- refactoring algorithms to improve readability and efficiency
- updating README documentation to clearly explain scheduling logic and walking through a demo of the app

Some important questions I asked my AI Agent that I found were helpful include:
- Asking to clarify how the Scheduler class should operate and identify schedule conflicts
- How can we expand our pytests in order to cover more app features and edge cases  

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment where I didn't accept an AI suggestion as-is was when we were initially building the class methods and attributes. There, it wanted to create a task attribute: `frequency` that would have been a type `string` with values such as "once". I felt that this was a very poor implementation that would lead to difficulties as we implemented the scheduling logic, so I asked the AI Agent to use an `int` type instead.

By consistently looking through the AI's suggested changes/additions, I was able to identify weird cases such as the one mentioned above. I also would always try to manually test the app after each change/addition, in order to make sure that everything is working as intended.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Some behaviors that I tested include:
- Basic model behavior: adding a task increases a pet's task count, and marking a task complete flips its `completed` flag. 
- Validation: a `Task` rejects a single `due_time` when `frequency > 1` (it should use `due_times` instead), and rejects a `due_times` list whose length doesn't match `frequency`. 
- Scheduling correctness: flexible (no fixed time) tasks are assigned the earliest free slot
  - recurring tasks with `frequency > 1` and no fixed times get evenly spread slots across the day
  - recurring tasks with matching `due_times` keep exactly those times
- Sorting: occurrences come back in chronological order, and same-start-time ties are broken by priority then duration. 
- Conflict detection: overlapping fixed due times across pets are flagged and `concurrent_ok` tasks at the same time are not flagged 
- Completed-task handling: completed tasks are excluded from a generated schedule by default

These were important because the scheduling logic is the most complex and highest-risk part of the app with interacting rules (fixed vs. flexible tasks, priority ordering, frequency spreading, concurrent_ok exemptions) where a change to one rule could silently break another. These tests helped me keep a sanity check as I continued to develop and refine more features.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident in the core logic since every branch of `assign_schedule` and `find_conflicts` (fixed times, flexible single-occurrence, flexible recurring, conflict vs. no-conflict, completed vs. not) has at least one passing test, and all 17 tests pass.

If I had more time, I'd add tests for: 
- a day so overbooked that even the fallback slot for a flexible task overlaps something else
- a `due_time` or `due_times` entry outside the 08:00-20:00 window
- frequency values of 0 or negative frequency being passed explicitly

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how this project help refresh and refine my knowledge of class diagrams and overall system design by making me produce and evaluate a UML Diagram before writing any code.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would want to improve the ui layout of the Streamlit app, making it utilize empty screen space more effectively and make the user scroll less in order to interact with the entire app.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing that I learned is that you will probably never get your system design or class diagram perfect on the first try. As I continued to develop the app, I realized there were many features that wouldn't work or be effective without adjusting the system design. The earliest example in this project was adjusting the Owner class to be able to have more than one Pet, in order to support more complex scheduling and potential time conflicts between two different pets.
