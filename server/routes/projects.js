const express = require('express');
const { body, validationResult } = require('express-validator');
const Project = require('../models/Project');
const User = require('../models/User');
const { auth, moderatorAuth } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/projects
// @desc    Get all projects for user
// @access  Private
router.get('/', auth, async (req, res) => {
  try {
    const { page = 1, limit = 10, status = '', search = '', sortBy = 'createdAt', sortOrder = 'desc' } = req.query;
    
    const query = {
      $or: [
        { createdBy: req.user._id },
        { 'teamMembers.user': req.user._id }
      ]
    };

    if (status) {
      query.status = status;
    }

    if (search) {
      query.$and = [
        query,
        {
          $or: [
            { title: { $regex: search, $options: 'i' } },
            { description: { $regex: search, $options: 'i' } },
            { tags: { $in: [new RegExp(search, 'i')] } }
          ]
        }
      ];
    }

    const sortOptions = {};
    sortOptions[sortBy] = sortOrder === 'desc' ? -1 : 1;

    const projects = await Project.find(query)
      .populate('createdBy', 'username firstName lastName email')
      .populate('teamMembers.user', 'username firstName lastName email')
      .sort(sortOptions)
      .limit(limit * 1)
      .skip((page - 1) * limit);

    const total = await Project.countDocuments(query);

    res.json({
      projects,
      totalPages: Math.ceil(total / limit),
      currentPage: parseInt(page),
      total
    });
  } catch (error) {
    console.error('Get projects error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   GET /api/projects/:id
// @desc    Get project by ID
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const project = await Project.findById(req.params.id)
      .populate('createdBy', 'username firstName lastName email')
      .populate('teamMembers.user', 'username firstName lastName email')
      .populate('tasks.assignedTo', 'username firstName lastName email');
    
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }

    // Check if user has access to this project
    const hasAccess = project.createdBy._id.toString() === req.user._id.toString() ||
                     project.teamMembers.some(member => member.user._id.toString() === req.user._id.toString());

    if (!hasAccess) {
      return res.status(403).json({ message: 'Access denied' });
    }

    res.json({ project });
  } catch (error) {
    console.error('Get project error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/projects
// @desc    Create a new project
// @access  Private
router.post('/', auth, [
  body('title').trim().isLength({ min: 1, max: 100 }).withMessage('Title is required and must be less than 100 characters'),
  body('description').trim().isLength({ min: 1, max: 1000 }).withMessage('Description is required and must be less than 1000 characters'),
  body('status').optional().isIn(['planning', 'in-progress', 'completed', 'on-hold', 'cancelled']).withMessage('Invalid status'),
  body('priority').optional().isIn(['low', 'medium', 'high', 'urgent']).withMessage('Invalid priority'),
  body('tags').optional().isArray().withMessage('Tags must be an array')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { title, description, status, priority, startDate, endDate, tags, teamMembers } = req.body;

    const project = new Project({
      title,
      description,
      status: status || 'planning',
      priority: priority || 'medium',
      startDate: startDate || new Date(),
      endDate,
      tags: tags || [],
      createdBy: req.user._id,
      teamMembers: teamMembers ? teamMembers.map(member => ({
        user: member.user,
        role: member.role || 'member'
      })) : []
    });

    // Add creator as owner
    project.teamMembers.push({
      user: req.user._id,
      role: 'owner'
    });

    await project.save();

    const populatedProject = await Project.findById(project._id)
      .populate('createdBy', 'username firstName lastName email')
      .populate('teamMembers.user', 'username firstName lastName email');

    res.status(201).json({
      message: 'Project created successfully',
      project: populatedProject
    });
  } catch (error) {
    console.error('Create project error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   PUT /api/projects/:id
// @desc    Update project
// @access  Private
router.put('/:id', auth, [
  body('title').optional().trim().isLength({ min: 1, max: 100 }).withMessage('Title must be less than 100 characters'),
  body('description').optional().trim().isLength({ min: 1, max: 1000 }).withMessage('Description must be less than 1000 characters'),
  body('status').optional().isIn(['planning', 'in-progress', 'completed', 'on-hold', 'cancelled']).withMessage('Invalid status'),
  body('priority').optional().isIn(['low', 'medium', 'high', 'urgent']).withMessage('Invalid priority')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const project = await Project.findById(req.params.id);
    
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }

    // Check if user has permission to update
    const isOwner = project.createdBy.toString() === req.user._id.toString();
    const isAdmin = project.teamMembers.find(member => 
      member.user.toString() === req.user._id.toString() && 
      ['owner', 'admin'].includes(member.role)
    );

    if (!isOwner && !isAdmin) {
      return res.status(403).json({ message: 'Access denied' });
    }

    const { title, description, status, priority, startDate, endDate, tags } = req.body;
    
    if (title) project.title = title;
    if (description) project.description = description;
    if (status) project.status = status;
    if (priority) project.priority = priority;
    if (startDate) project.startDate = startDate;
    if (endDate) project.endDate = endDate;
    if (tags) project.tags = tags;

    await project.save();

    const updatedProject = await Project.findById(project._id)
      .populate('createdBy', 'username firstName lastName email')
      .populate('teamMembers.user', 'username firstName lastName email');

    res.json({
      message: 'Project updated successfully',
      project: updatedProject
    });
  } catch (error) {
    console.error('Update project error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   DELETE /api/projects/:id
// @desc    Delete project
// @access  Private
router.delete('/:id', auth, async (req, res) => {
  try {
    const project = await Project.findById(req.params.id);
    
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }

    // Only owner can delete project
    if (project.createdBy.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Only project owner can delete project' });
    }

    await Project.findByIdAndDelete(req.params.id);

    res.json({ message: 'Project deleted successfully' });
  } catch (error) {
    console.error('Delete project error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   POST /api/projects/:id/tasks
// @desc    Add task to project
// @access  Private
router.post('/:id/tasks', auth, [
  body('title').trim().isLength({ min: 1, max: 200 }).withMessage('Task title is required and must be less than 200 characters'),
  body('description').optional().trim().isLength({ max: 500 }).withMessage('Description must be less than 500 characters'),
  body('priority').optional().isIn(['low', 'medium', 'high']).withMessage('Invalid priority'),
  body('assignedTo').optional().isMongoId().withMessage('Invalid assigned user ID')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const project = await Project.findById(req.params.id);
    
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }

    // Check if user has permission to add tasks
    const hasAccess = project.createdBy.toString() === req.user._id.toString() ||
                     project.teamMembers.some(member => 
                       member.user.toString() === req.user._id.toString() && 
                       ['owner', 'admin', 'member'].includes(member.role)
                     );

    if (!hasAccess) {
      return res.status(403).json({ message: 'Access denied' });
    }

    const { title, description, priority, assignedTo, dueDate } = req.body;

    const task = {
      title,
      description: description || '',
      priority: priority || 'medium',
      assignedTo: assignedTo || null,
      dueDate: dueDate || null
    };

    project.tasks.push(task);
    await project.save();

    const updatedProject = await Project.findById(project._id)
      .populate('createdBy', 'username firstName lastName email')
      .populate('teamMembers.user', 'username firstName lastName email')
      .populate('tasks.assignedTo', 'username firstName lastName email');

    res.status(201).json({
      message: 'Task added successfully',
      project: updatedProject
    });
  } catch (error) {
    console.error('Add task error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// @route   PUT /api/projects/:id/tasks/:taskId
// @desc    Update task
// @access  Private
router.put('/:id/tasks/:taskId', auth, [
  body('title').optional().trim().isLength({ min: 1, max: 200 }).withMessage('Title must be less than 200 characters'),
  body('description').optional().trim().isLength({ max: 500 }).withMessage('Description must be less than 500 characters'),
  body('status').optional().isIn(['todo', 'in-progress', 'completed']).withMessage('Invalid status'),
  body('priority').optional().isIn(['low', 'medium', 'high']).withMessage('Invalid priority')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const project = await Project.findById(req.params.id);
    
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }

    const task = project.tasks.id(req.params.taskId);
    if (!task) {
      return res.status(404).json({ message: 'Task not found' });
    }

    // Check if user has permission to update task
    const hasAccess = project.createdBy.toString() === req.user._id.toString() ||
                     project.teamMembers.some(member => 
                       member.user.toString() === req.user._id.toString() && 
                       ['owner', 'admin', 'member'].includes(member.role)
                     ) ||
                     task.assignedTo && task.assignedTo.toString() === req.user._id.toString();

    if (!hasAccess) {
      return res.status(403).json({ message: 'Access denied' });
    }

    const { title, description, status, priority, assignedTo, dueDate } = req.body;
    
    if (title) task.title = title;
    if (description !== undefined) task.description = description;
    if (status) task.status = status;
    if (priority) task.priority = priority;
    if (assignedTo !== undefined) task.assignedTo = assignedTo;
    if (dueDate !== undefined) task.dueDate = dueDate;
    
    task.updatedAt = new Date();

    await project.save();

    const updatedProject = await Project.findById(project._id)
      .populate('createdBy', 'username firstName lastName email')
      .populate('teamMembers.user', 'username firstName lastName email')
      .populate('tasks.assignedTo', 'username firstName lastName email');

    res.json({
      message: 'Task updated successfully',
      project: updatedProject
    });
  } catch (error) {
    console.error('Update task error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
