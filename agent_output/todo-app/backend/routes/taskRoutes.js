const express = require('express');
const router = express.Router();
const taskController = require('../controllers/taskController');
const authMiddleware = require('../middleware/authMiddleware'); // Import authentication middleware

// Apply authMiddleware to all task routes
router.use(authMiddleware);

// Get all top-level tasks for a user
router.get('/', taskController.getAllTasks);

// Search tasks based on query parameters
router.get('/search', taskController.searchTasks);

// Get subtasks for a given parent task ID
router.get('/:id/subtasks', taskController.getSubtasks);

// Get a single task by ID
router.get('/:id', taskController.getTaskById);

// Create a new task
router.post('/', taskController.createTask);

// Update a task by ID
router.put('/:id', taskController.updateTask);

// Delete a task by ID
router.delete('/:id', taskController.deleteTask);

// Mark a task as complete
router.patch('/:id/complete', taskController.markTaskComplete);

module.exports = router;