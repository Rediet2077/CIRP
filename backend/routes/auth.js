const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const { body, validationResult } = require('express-validator');
const db = require('../config/database');
const { authMiddleware } = require('../middleware/auth');
const otpService = require('../services/otp.service');

// Helper function to generate JWT
const generateToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRES_IN || '7d'
  });
};

// Register
router.post('/register',
  [
    body('email').isEmail().withMessage('Valid email is required'),
    body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
    body('full_name').notEmpty().withMessage('Full name is required'),
  ],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ 
          success: false,
          message: 'Validation failed',
          errors: errors.array() 
        });
      }

      const { email, password, full_name, phone_number } = req.body;

      // Normalize email
      const normalizedEmail = email.toLowerCase().trim();

      // Check if user exists
      const existingUser = await db.getAsync('SELECT id, is_email_verified FROM users WHERE email = ?', [normalizedEmail]);

      if (existingUser) {
        if (existingUser.is_email_verified) {
          return res.status(400).json({ 
            success: false,
            message: 'Email already registered. Please login instead.' 
          });
        } else {
          // User exists but not verified - allow re-registration (update existing record)
          const password_hash = await bcrypt.hash(password, 10);
          await db.runAsync(`
            UPDATE users 
            SET password_hash = ?, full_name = ?, phone_number = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
          `, [password_hash, full_name, phone_number, existingUser.id]);

          return res.status(200).json({
            success: true,
            message: 'Registration updated. Please verify your email with the OTP sent.',
            user: {
              id: existingUser.id,
              email: normalizedEmail,
              full_name,
              is_email_verified: false
            },
            requiresVerification: true
          });
        }
      }

      // Hash password
      const password_hash = await bcrypt.hash(password, 10);

      // Create user with is_email_verified = 0 (requires OTP verification)
      const userId = uuidv4();
      await db.runAsync(`
        INSERT INTO users (id, email, password_hash, full_name, phone_number, role, is_email_verified, is_active)
        VALUES (?, ?, ?, ?, ?, 'citizen', 0, 1)
      `, [userId, normalizedEmail, password_hash, full_name, phone_number]);

      const user = await db.getAsync('SELECT id, email, full_name, role, is_email_verified FROM users WHERE id = ?', [userId]);

      // Send OTP automatically
      try {
        await otpService.sendOTP(normalizedEmail, 'registration', full_name);
        console.log('✅ OTP sent to:', normalizedEmail);
      } catch (otpError) {
        console.error('❌ Failed to send OTP:', otpError);
        // Continue even if OTP fails - user can resend later
      }

      res.status(201).json({
        success: true,
        message: 'Registration successful. Please check your email for OTP verification code.',
        user: {
          id: user.id,
          email: user.email,
          full_name: user.full_name,
          role: user.role,
          is_email_verified: false
        },
        requiresVerification: true
      });
    } catch (error) {
      console.error('Registration error:', error);
      res.status(500).json({ 
        success: false,
        message: 'Registration failed',
        error: error.message 
      });
    }
  }
);

// Login (handles both /login and /login/)
router.post(['/login', '/login/'],
  [
    body('email').isEmail().withMessage('Valid email is required'),
    body('password').notEmpty().withMessage('Password is required'),
  ],
  async (req, res) => {
    console.log('🔐 Login request received:', { email: req.body?.email, hasPassword: !!req.body?.password });
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        console.log('❌ Validation errors:', errors.array());
        return res.status(400).json({ errors: errors.array() });
      }

      const { email, password } = req.body;
      console.log('📧 Looking up user:', email);

      // Get user
      const user = await db.getAsync(`
        SELECT id, email, password_hash, full_name, role, is_active, is_email_verified, phone_number, profile_image
        FROM users WHERE email = ?
      `, [email]);

      console.log('👤 User found:', user ? { id: user.id, email: user.email, role: user.role } : 'NOT FOUND');

      if (!user) {
        console.log('❌ User not found');
        return res.status(401).json({ 
          success: false,
          message: 'Invalid credentials' 
        });
      }

      // Check if email is verified
      if (!user.is_email_verified) {
        console.log('❌ Email not verified');
        return res.status(403).json({ 
          success: false,
          message: 'Email not verified. Please verify your email with OTP first.',
          requiresVerification: true,
          email: user.email
        });
      }

      // Check if account is active
      if (!user.is_active) {
        console.log('❌ Account inactive');
        return res.status(401).json({ 
          success: false,
          message: 'Account is inactive. Please contact support.' 
        });
      }

      console.log('🔑 Verifying password...');
      // Verify password
      const isValidPassword = await bcrypt.compare(password, user.password_hash);
      console.log('🔑 Password valid:', isValidPassword);

      if (!isValidPassword) {
        console.log('❌ Invalid password');
        return res.status(401).json({ 
          success: false,
          message: 'Invalid credentials' 
        });
      }

      console.log('🎫 Generating token...');
      // Generate token
      const token = generateToken(user.id);

      console.log('🏢 Getting department info...');
      // Get department info if user is department_head
      let department = null;
      if (user.role === 'department_head') {
        const dept = await db.getAsync(`
          SELECT d.id, d.name
          FROM departments d
          JOIN users u ON u.department_id = d.id
          WHERE u.id = ?
        `, [user.id]);
        console.log('🏢 Department:', dept ? dept.name : 'NOT FOUND');
        if (dept) {
          // Generate code from name (first 4 letters uppercase)
          const code = dept.name.substring(0, 4).toUpperCase();
          department = {
            id: dept.id,
            name: dept.name,
            code: code
          };
        }
      }

      console.log('✅ Login successful, sending response...');
      // Format response to match admin page and mobile app expectations
      const response = {
        success: true,
        access: token,
        refresh: token,
        token: token,
        user: {
          id: user.id,
          email: user.email,
          full_name: user.full_name,
          first_name: user.full_name.split(' ')[0] || user.full_name,
          last_name: user.full_name.split(' ').slice(1).join(' ') || '',
          role: user.role === 'admin' ? 'SYSTEM_ADMIN' : user.role === 'department_head' ? 'DEPARTMENT_ADMIN' : 'CITIZEN',
          status: user.is_active ? 'ACTIVE' : 'INACTIVE',
          department: department
        }
      };
      console.log('📤 Sending response:', JSON.stringify(response, null, 2));
      res.json(response);
    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({ error: 'Login failed' });
    }
  }
);

// Get current user
router.get('/me', authMiddleware, async (req, res) => {
  try {
    const user = await db.getAsync(`
      SELECT id, email, full_name, role, phone_number, profile_image, created_at
      FROM users WHERE id = ?
    `, [req.userId]);

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ error: 'Failed to get user' });
  }
});

// Update profile
router.put('/profile', authMiddleware,
  [
    body('full_name').optional().notEmpty(),
    body('phone_number').optional(),
  ],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const { full_name, phone_number } = req.body;
      const updates = [];
      const values = [];

      if (full_name) {
        updates.push('full_name = ?');
        values.push(full_name);
      }

      if (phone_number) {
        updates.push('phone_number = ?');
        values.push(phone_number);
      }

      if (updates.length === 0) {
        return res.status(400).json({ error: 'No fields to update' });
      }

      updates.push('updated_at = CURRENT_TIMESTAMP');
      values.push(req.userId);

      await db.runAsync(`
        UPDATE users SET ${updates.join(', ')}
        WHERE id = ?
      `, values);

      const user = await db.getAsync('SELECT id, email, full_name, phone_number, role FROM users WHERE id = ?', [req.userId]);

      res.json({
        message: 'Profile updated successfully',
        user
      });
    } catch (error) {
      console.error('Update profile error:', error);
      res.status(500).json({ error: 'Failed to update profile' });
    }
  }
);

// Change password
router.post('/change-password', authMiddleware,
  [
    body('current_password').notEmpty().withMessage('Current password is required'),
    body('new_password').isLength({ min: 6 }).withMessage('New password must be at least 6 characters'),
  ],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const { current_password, new_password } = req.body;

      // Get current password hash
      const user = await db.getAsync('SELECT password_hash FROM users WHERE id = ?', [req.userId]);

      // Verify current password
      const isValidPassword = await bcrypt.compare(current_password, user.password_hash);

      if (!isValidPassword) {
        return res.status(401).json({ error: 'Current password is incorrect' });
      }

      // Hash new password
      const new_password_hash = await bcrypt.hash(new_password, 10);

      // Update password
      await db.runAsync('UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
        [new_password_hash, req.userId]);

      res.json({ message: 'Password changed successfully' });
    } catch (error) {
      console.error('Change password error:', error);
      res.status(500).json({ error: 'Failed to change password' });
    }
  }
);

module.exports = router;
