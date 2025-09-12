const Project = require('../models/Project');
const ProjectMember = require('../models/ProjectMember');

exports.getAllProjects = async (req, res) => {
    try {
        // Get projects where the user is either the creator or a member
        const projectsAsOwner = await Project.find({ user: req.user.id }).sort({ date: -1 });
        const projectsAsMember = await ProjectMember.find({ user: req.user.id }).populate('project');

        // Combine and de-duplicate projects
        const combinedProjects = [...projectsAsOwner, ...projectsAsMember.map(pm => pm.project)];
        const uniqueProjects = Array.from(new Set(combinedProjects.map(p => p.id)))
                                .map(id => combinedProjects.find(p => p.id === id));

        res.json(uniqueProjects);
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
};

exports.getProjectById = async (req, res) => {
    try {
        const project = await Project.findById(req.params.id);

        if (!project) {
            return res.status(404).json({ msg: 'Project not found' });
        }

        // Check if user is the owner or a member
        const isMember = await ProjectMember.findOne({ project: req.params.id, user: req.user.id });
        if (project.user.toString() !== req.user.id && !isMember) {
            return res.status(401).json({ msg: 'User not authorized to view this project' });
        }

        res.json(project);
    } catch (err) {
        console.error(err.message);
        if (err.kind === 'ObjectId') {
            return res.status(404).json({ msg: 'Project not found' });
        }
        res.status(500).send('Server Error');
    }
};

exports.createProject = async (req, res) => {
    const { title, description, deadline, status } = req.body;

    try {
        const newProject = new Project({
            user: req.user.id,
            title,
            description,
            deadline,
            status
        });

        const project = await newProject.save();

        // Automatically add the creator as an owner in ProjectMember
        const newMember = new ProjectMember({
            project: project._id,
            user: req.user.id,
            role: 'owner'
        });
        await newMember.save();

        res.json(project);
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
};

exports.updateProject = async (req, res) => {
    const { title, description, deadline, status } = req.body;

    // Build project object
    const projectFields = {};
    if (title) projectFields.title = title;
    if (description) projectFields.description = description;
    if (deadline) projectFields.deadline = deadline;
    if (status) projectFields.status = status;

    try {
        let project = await Project.findById(req.params.id);

        if (!project) return res.status(404).json({ msg: 'Project not found' });

        // Only owner can update project details for now
        if (project.user.toString() !== req.user.id) {
            return res.status(401).json({ msg: 'User not authorized to update this project' });
        }

        project = await Project.findByIdAndUpdate(
            req.params.id,
            { $set: projectFields },
            { new: true }
        );

        res.json(project);
    } catch (err) {
        console.error(err.message);
        if (err.kind === 'ObjectId') {
            return res.status(404).json({ msg: 'Project not found' });
        }
        res.status(500).send('Server Error');
    }
};

exports.deleteProject = async (req, res) => {
    try {
        const project = await Project.findById(req.params.id);

        if (!project) {
            return res.status(404).json({ msg: 'Project not found' });
        }

        // Only owner can delete project
        if (project.user.toString() !== req.user.id) {
            return res.status(401).json({ msg: 'User not authorized to delete this project' });
        }

        await Project.findByIdAndRemove(req.params.id);

        // Also remove all associated tasks and project members
        await Task.deleteMany({ project: req.params.id });
        await ProjectMember.deleteMany({ project: req.params.id });

        res.json({ msg: 'Project, its tasks, and members removed' });
    } catch (err) {
        console.error(err.message);
        if (err.kind === 'ObjectId') {
            return res.status(404).json({ msg: 'Project not found' });
        }
        res.status(500).send('Server Error');
    }
};

exports.addProjectMember = async (req, res) => {
    const { userId, role } = req.body;
    const projectId = req.params.id;

    try {
        const project = await Project.findById(projectId);
        if (!project) return res.status(404).json({ msg: 'Project not found' });

        // Only owner can add members
        const projectOwner = await ProjectMember.findOne({ project: projectId, user: req.user.id, role: 'owner' });
        if (!projectOwner) {
            return res.status(401).json({ msg: 'Only project owners can add members' });
        }

        // Check if user is already a member
        const existingMember = await ProjectMember.findOne({ project: projectId, user: userId });
        if (existingMember) {
            return res.status(400).json({ msg: 'User is already a member of this project' });
        }

        const newMember = new ProjectMember({
            project: projectId,
            user: userId,
            role: role || 'member'
        });

        await newMember.save();
        res.json({ msg: 'Member added to project', member: newMember });

    } catch (err) {
        console.error(err.message);
        if (err.code === 11000) { // Duplicate key error
            return res.status(400).json({ msg: 'User is already a member of this project (duplicate)' });
        }
        res.status(500).send('Server Error');
    }
};

exports.removeProjectMember = async (req, res) => {
    const { memberId } = req.body; // memberId refers to the User's ID to be removed
    const projectId = req.params.id;

    try {
        const project = await Project.findById(projectId);
        if (!project) return res.status(404).json({ msg: 'Project not found' });

        // Only owner can remove members (or an admin removing a non-owner/non-admin)
        const projectOwner = await ProjectMember.findOne({ project: projectId, user: req.user.id, role: 'owner' });
        if (!projectOwner) {
            return res.status(401).json({ msg: 'Only project owners can remove members' });
        }

        // Prevent owner from removing themselves directly via this route (they should delete project)
        const memberToRemove = await ProjectMember.findOne({ project: projectId, user: memberId });
        if (!memberToRemove) {
            return res.status(404).json({ msg: 'Member not found in this project' });
        }

        if (memberToRemove.role === 'owner') {
            return res.status(400).json({ msg: 'Cannot remove project owner via this route. Delete the project instead.' });
        }

        await ProjectMember.deleteOne({ project: projectId, user: memberId });
        res.json({ msg: 'Member removed from project' });

    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
};

exports.getProjectMembers = async (req, res) => {
    const projectId = req.params.id;

    try {
        const project = await Project.findById(projectId);
        if (!project) return res.status(404).json({ msg: 'Project not found' });

        // Check if user is owner or member to view members
        const isMember = await ProjectMember.findOne({ project: projectId, user: req.user.id });
        if (project.user.toString() !== req.user.id && !isMember) {
            return res.status(401).json({ msg: 'User not authorized to view project members' });
        }

        const members = await ProjectMember.find({ project: projectId }).populate('user', 'name email'); // Populate user details
        res.json(members);

    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
};