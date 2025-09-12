const Task = require('../models/Task');

exports.getAllTasks = async (req, res) => {
    try {
        // Fetch only top-level tasks (no parentTask) for a user
        const tasks = await Task.find({ user: req.user.id, parentTask: null }).sort({ date: -1 });
        res.json(tasks);
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
};

exports.getSubtasks = async (req, res) => {
    try {
        const parentTaskId = req.params.id;
        const subtasks = await Task.find({ user: req.user.id, parentTask: parentTaskId }).sort({ date: -1 });

        // Optional: Check if the parent task itself exists and belongs to the user
        const parentTask = await Task.findById(parentTaskId);
        if (!parentTask || parentTask.user.toString() !== req.user.id) {
            return res.status(401).json({ msg: 'Not authorized to view subtasks for this parent' });
        }

        res.json(subtasks);
    } catch (err) {
        console.error(err.message);
        if (err.kind === 'ObjectId') {
            return res.status(404).json({ msg: 'Invalid parent task ID' });
        }
        res.status(500).send('Server Error');
    }
};

exports.getTaskById = async (req, res) => {
    try {
        const task = await Task.findById(req.params.id);

        if (!task) {
            return res.status(404).json({ msg: 'Task not found' });
        }

        // Ensure user owns the task
        if (task.user.toString() !== req.user.id) {
            return res.status(401).json({ msg: 'User not authorized' });
        }

        res.json(task);
    } catch (err) {
        console.error(err.message);
        if (err.kind === 'ObjectId') {
            return res.status(404).json({ msg: 'Task not found' });
        }
        res.status(500).send('Server Error');
    }
};

exports.createTask = async (req, res) => {
    const { title, description, dueDate, priority, category, assignee, status, projectId, parentTask } = req.body;

    try {
        // If parentTask is provided, ensure it exists and belongs to the user
        if (parentTask) {
            const existingParentTask = await Task.findById(parentTask);
            if (!existingParentTask || existingParentTask.user.toString() !== req.user.id) {
                return res.status(400).json({ msg: 'Invalid or unauthorized parent task' });
            }
        }

        const newTask = new Task({
            user: req.user.id,
            title,
            description,
            dueDate,
            priority,
            category,
            assignee,
            status,
            project: projectId || null, // Link to project if provided
            parentTask: parentTask || null // Link to parent task if provided
        });

        const task = await newTask.save();
        res.json(task);
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
};

exports.updateTask = async (req, res) => {
    const { title, description, dueDate, priority, category, assignee, status, completed, projectId, parentTask } = req.body;

    // Build task object
    const taskFields = {};
    if (title) taskFields.title = title;
    if (description) taskFields.description = description;
    if (dueDate) taskFields.dueDate = dueDate;
    if (priority) taskFields.priority = priority;
    if (category) taskFields.category = category;
    if (assignee) taskFields.assignee = assignee;
    if (status) taskFields.status = status;
    if (projectId) taskFields.project = projectId;
    if (typeof completed !== 'undefined') taskFields.completed = completed; // Allow setting completed to false
    // Allow nulling out parentTask, or setting a new one
    if (typeof parentTask !== 'undefined') taskFields.parentTask = parentTask;

    try {
        let task = await Task.findById(req.params.id);

        if (!task) return res.status(404).json({ msg: 'Task not found' });

        // Ensure user owns the task
        if (task.user.toString() !== req.user.id) {
            return res.status(401).json({ msg: 'User not authorized' });
        }

        // If parentTask is updated, ensure it exists and belongs to the user
        if (taskFields.parentTask) {
            const existingParentTask = await Task.findById(taskFields.parentTask);
            if (!existingParentTask || existingParentTask.user.toString() !== req.user.id) {
                return res.status(400).json({ msg: 'Invalid or unauthorized parent task for update' });
            }
        }

        task = await Task.findByIdAndUpdate(
            req.params.id,
            { $set: taskFields },
            { new: true }
        );

        res.json(task);
    } catch (err) {
        console.error(err.message);
        if (err.kind === 'ObjectId') {
            return res.status(404).json({ msg: 'Task not found' });
        }
        res.status(500).send('Server Error');
    }
};

exports.deleteTask = async (req, res) => {
    try {
        const task = await Task.findById(req.params.id);

        if (!task) {
            return res.status(404).json({ msg: 'Task not found' });
        }

        // Ensure user owns the task
        if (task.user.toString() !== req.user.id) {
            return res.status(401).json({ msg: 'User not authorized' });
        }

        // Optional: Also delete all subtasks if a parent task is deleted
        await Task.deleteMany({ parentTask: req.params.id });

        await Task.findByIdAndRemove(req.params.id);

        res.json({ msg: 'Task and its subtasks removed' });
    } catch (err) {
        console.error(err.message);
        if (err.kind === 'ObjectId') {
            return res.status(404).json({ msg: 'Task not found' });
        }
        res.status(500).send('Server Error');
    }
};

exports.markTaskComplete = async (req, res) => {
    try {
        let task = await Task.findById(req.params.id);

        if (!task) return res.status(404).json({ msg: 'Task not found' });

        // Ensure user owns the task
        if (task.user.toString() !== req.user.id) {
            return res.status(401).json({ msg: 'User not authorized' });
        }

        task.completed = true;
        await task.save();

        res.json(task);
    } catch (err) {
        console.error(err.message);
        if (err.kind === 'ObjectId') {
            return res.status(404).json({ msg: 'Task not found' });
        }
        res.status(500).send('Server Error');
    }
};

exports.searchTasks = async (req, res) => {
    try {
        const { keyword, priority, status, dueDate, category, projectId, completed, parentTask } = req.query;
        const query = { user: req.user.id };

        if (keyword) {
            query.$or = [
                { title: { $regex: keyword, $options: 'i' } },
                { description: { $regex: keyword, $options: 'i' } }
            ];
        }
        if (priority) {
            query.priority = priority;
        }
        if (status) {
            query.status = status;
        }
        if (dueDate) {
            // For exact date match or range, depending on how specific we want to be
            query.dueDate = new Date(dueDate);
        }
        if (category) {
            query.category = { $regex: category, $options: 'i' }; // Case-insensitive category search
        }
        if (projectId) {
            query.project = projectId;
        }
        if (typeof completed !== 'undefined') {
            query.completed = completed === 'true'; // Convert string to boolean
        }
        if (parentTask) {
            query.parentTask = parentTask;
        } else if (parentTask === 'null') {
            query.parentTask = null; // Search for top-level tasks
        }

        const tasks = await Task.find(query).sort({ date: -1 });
        res.json(tasks);

    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
};