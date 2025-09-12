const mongoose = require('mongoose');

const TaskSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'user',
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
  },
  dueDate: {
    type: Date,
  },
  priority: {
    type: String,
    enum: ['high', 'medium', 'low'],
    default: 'medium',
  },
  category: {
    type: String,
  },
  assignee: {
    type: String, // Can be user ID or just a name for now
  },
  status: {
    type: String,
    enum: ['to do', 'in progress', 'completed', 'blocked'],
    default: 'to do',
  },
  completed: {
    type: Boolean,
    default: false,
  },
  date: {
    type: Date,
    default: Date.now,
  },
  // For Subtasks
  parentTask: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'task',
    default: null,
  },
  // Potentially store subtasks as an array of IDs, though querying by parentTask is also viable.
  // subtasks: [{
  //   type: mongoose.Schema.Types.ObjectId,
  //   ref: 'task',
  // }],
  project: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'project',
    default: null
  }
});

module.exports = mongoose.model('task', TaskSchema);