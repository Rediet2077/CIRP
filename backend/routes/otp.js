const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const otpService = require('../services/otp.service');
const db = require('../config/database');

/**
 * POST /api/otp/send
 * Send OTP to email (for registration or password reset)
 */
router.post('/send',
  [
    body('email').isEmail().withMessage('Valid email is required'),
    body('purpose').optional().isIn(['registration', 'password_reset', 'email_change']).withMessage('Invalid purpose'),
    body('full_name').optional().trim(),
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

      const { email, purpose = 'registration', full_name = 'User' } = req.body;

      // Normalize email
      const normalizedEmail = email.toLowerCase().trim();

      // For registration, check if email is already registered and verified
      if (purpose === 'registration') {
        const existingUser = await db.getAsync(
          'SELECT id, is_email_verified FROM users WHERE email = ?',
          normalizedEmail
        );

        if (existingUser && existingUser.is_email_verified) {
          return res.status(400).json({
            success: false,
            message: 'This email is already registered. Please login instead.'
          });
        }
      }

      // Send OTP
      const result = await otpService.sendOTP(normalizedEmail, purpose, full_name);

      if (!result.success) {
        return res.status(429).json({
          success: false,
          message: result.message,
          retryAfter: result.retryAfter
        });
      }

      res.json({
        success: true,
        message: 'OTP sent successfully to your email',
        expiresAt: result.expiresAt,
        expiresIn: 300 // 5 minutes in seconds
      });

    } catch (error) {
      console.error('Send OTP error:', error);
      res.status(500).json({ 
        success: false,
        message: 'Failed to send OTP. Please try again.',
        error: error.message 
      });
    }
  }
);

/**
 * POST /api/otp/verify
 * Verify OTP code
 */
router.post('/verify',
  [
    body('email').isEmail().withMessage('Valid email is required'),
    body('otp_code').isLength({ min: 6, max: 6 }).withMessage('OTP must be 6 digits'),
    body('purpose').optional().isIn(['registration', 'password_reset', 'email_change']).withMessage('Invalid purpose'),
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

      const { email, otp_code, purpose = 'registration' } = req.body;

      // Normalize email
      const normalizedEmail = email.toLowerCase().trim();

      // Verify OTP
      const result = await otpService.verifyOTP(normalizedEmail, otp_code, purpose);

      if (!result.success) {
        return res.status(400).json({
          success: false,
          message: result.message,
          verified: false,
          attemptsLeft: result.attemptsLeft
        });
      }

      // If verification is for registration, mark user as verified
      if (purpose === 'registration') {
        await db.runAsync(
          `UPDATE users SET is_email_verified = 1, updated_at = CURRENT_TIMESTAMP 
           WHERE email = ?`,
          normalizedEmail
        );
      }

      res.json({
        success: true,
        message: 'Email verified successfully',
        verified: true
      });

    } catch (error) {
      console.error('Verify OTP error:', error);
      res.status(500).json({ 
        success: false,
        message: 'Verification failed. Please try again.',
        error: error.message 
      });
    }
  }
);

/**
 * POST /api/otp/resend
 * Resend OTP code
 */
router.post('/resend',
  [
    body('email').isEmail().withMessage('Valid email is required'),
    body('purpose').optional().isIn(['registration', 'password_reset', 'email_change']).withMessage('Invalid purpose'),
    body('full_name').optional().trim(),
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

      const { email, purpose = 'registration', full_name = 'User' } = req.body;

      // Normalize email
      const normalizedEmail = email.toLowerCase().trim();

      // Send new OTP (rate limiting will be checked inside)
      const result = await otpService.sendOTP(normalizedEmail, purpose, full_name);

      if (!result.success) {
        return res.status(429).json({
          success: false,
          message: result.message,
          retryAfter: result.retryAfter
        });
      }

      res.json({
        success: true,
        message: 'New OTP sent successfully to your email',
        expiresAt: result.expiresAt,
        expiresIn: 300 // 5 minutes in seconds
      });

    } catch (error) {
      console.error('Resend OTP error:', error);
      res.status(500).json({ 
        success: false,
        message: 'Failed to resend OTP. Please try again.',
        error: error.message 
      });
    }
  }
);

/**
 * POST /api/otp/check-status
 * Check if email is verified (for debugging/testing)
 */
router.post('/check-status',
  [
    body('email').isEmail().withMessage('Valid email is required'),
    body('purpose').optional().isIn(['registration', 'password_reset', 'email_change']).withMessage('Invalid purpose'),
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

      const { email, purpose = 'registration' } = req.body;
      const normalizedEmail = email.toLowerCase().trim();

      const isVerified = await otpService.isEmailVerified(normalizedEmail, purpose);

      res.json({
        success: true,
        email: normalizedEmail,
        purpose,
        verified: isVerified
      });

    } catch (error) {
      console.error('Check status error:', error);
      res.status(500).json({ 
        success: false,
        message: 'Failed to check status',
        error: error.message 
      });
    }
  }
);

module.exports = router;
