const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// User registration
router.post('/register', authController.register);

// User login
router.post('/login', authController.login);

// Password reset request
router.post('/forgot-password', authController.forgotPassword);

// Reset password with token
router.post('/reset-password/:token', authController.resetPassword);

module.exports = router;