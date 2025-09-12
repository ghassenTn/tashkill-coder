const express = require('express');
const router = express.Router();
const projectController = require('../controllers/projectController');
const authMiddleware = require('../middleware/authMiddleware'); // Import authentication middleware

// Apply authMiddleware to all project routes
router.use(authMiddleware);

// Get all projects for a user (owned or as a member)
router.get('/', projectController.getAllProjects);

// Get a single project by ID
router.get('/:id', projectController.getProjectById);

// Create a new project
router.post('/', projectController.createProject);

// Update a project by ID
router.put('/:id', projectController.updateProject);

// Delete a project by ID
router.delete('/:id', projectController.deleteProject);

// --- Project Member Management ---

// Add a member to a project
router.post('/:id/members', projectController.addProjectMember);

// Remove a member from a project
router.delete('/:id/members', projectController.removeProjectMember);

// Get all members of a project
router.get('/:id/members', projectController.getProjectMembers);

module.exports = router;