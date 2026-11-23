# AnePlan - Tasklist Manager

AnePlan has arisen from my overwhelming urge to micromanage all of the outstanding tasks I want to get done.

While this application remains far from its final form, it currently has all of the basic functions required to build and modify tasklists.

## Current Features
### Add Tasks
Provide a task name, weight, and parent task (if applicable) and AnePlan will handle the rest!

Note that inputs are limited by the following conditions:

- Names must be unique between tasks and not solely made up of digits. Technically, naming your tasks after floats (i.e. '1.23') is allowed, but is strongly discouraged.
- Weights must be non-negative integers. *Generally, zero weights are intended for tasks that you intend to add subtasks to.*
- The parent task must exist or be left empty.

### Remove Tasks
Provide a task name, and AnePlan will see it deleted!

If the task you attempt to erase has subtasks, they will automatically be moved up a level in the hierarchy (becoming subtasks of the deleted task's parent).

### Modify Tasks
Provide the name of the task to modify, and AnePlan will modify any fields you fill in as required!

Note that you may fill in multiple fields to modify in a single pass. AnePlan will modify every field with a valid input.

Beyond the name of the task to be modified being one of an existing task, all modifiable fields have conditions to be considered valid:

- A new task name must follow the same conditions as those for a newly added task (non-integer and not of a currently existing task)
- A new weight must be non-negative
- A new parent must name an existing task and cannot form a closed cycle of parent-children relationships

Completion is a bit special, in the sense that AnePlan permits it to be given in two forms:
1. A numerical value, which is interpreted as being the total number of completed weight units for the task
2. A fraction, consisting of two integers (i.e. 3/5), which is interpreted as being a proportion of the total weight

Say you had a task that you assigned a weight of 2, that you have completed 40% of. Under the two possible formats, you could log this completion as '0.8' or as '2/5' (or any equivalent fraction).

In addition to any inputted completion being recognizable as one of these two formats, total completion cannot exceed the weight of the task it's being assigned to.

### Viewing Modes
AnePlan currently has three implemented 'quick-views':

1. All Tasks (Hierarchy) - View all tasks in tree format
2. Leaf-Only Mode - View list of all lowest level tasks (tasks with no subtasks)
3. Root-Only Mode - View list of all highest level tasks (tasks with no parent task)

In addition to the quick view modes, AnePlan also allows for users to view all subtasks of a given task in hierarchical format. This proves helpful if/when your tasklist grows large enough to look overwhelming.

## Key (Eventually) Planned Features
### Prerequisite Trees
Independent to parent tasks, which allow you to break a larger task down into smaller steps, I hope to eventually implement prerequisites to help in determining which tasks are the most beneficial to finish first. Prerequisite tasks can be used to find:

1. Bottlenecks - tasks that themselves must be completed to eventually free/unlock high volumes of task weight
2. Buried tasks - tasks that have prerequisites with high volumes of incomplete weight

### Due Dates
Bringing due dates into tasks where applicable opens up another few key metrics that will be useful for prioritizing:

1. Urgent tasks - tasks with high weight to days-until-due ratios
2. Deadlined, buried tasks - tasks with both a set deadline and with incomplete prerequisites
