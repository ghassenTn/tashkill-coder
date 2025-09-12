const mongoose = require('mongoose');

const ProjectMemberSchema = new mongoose.Schema({
    project: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'project',
        required: true
    },
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'user',
        required: true
    },
    role: {
        type: String,
        enum: ['owner', 'admin', 'member', 'viewer'],
        default: 'member'
    },
    dateAdded: {
        type: Date,
        default: Date.now
    }
});

// Ensure a user can only be a member of a project once
ProjectMemberSchema.index({ project: 1, user: 1 }, { unique: true });

module.exports = mongoose.model('projectmember', ProjectMemberSchema);