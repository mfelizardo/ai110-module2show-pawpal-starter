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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
