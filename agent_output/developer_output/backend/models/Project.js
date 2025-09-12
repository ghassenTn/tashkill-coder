const mongoose = require('mongoose');

const ProjectSchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'user',
        required: true
    },
    title: {
        type: String,
        required: true,
        trim: true
    },
    description: {
        type: String,
        trim: true
    },
    deadline: {
        type: Date
    },
    status: {
        type: String,
        enum: ['not started', 'in progress', 'completed', 'on hold', 'cancelled'],
        default: 'not started'
    },
    date: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('project', ProjectSchema);