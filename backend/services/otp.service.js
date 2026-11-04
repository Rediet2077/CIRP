const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const db = require('../config/database');
const emailService = require('./email.service');

class OTPService {
  /**
   * Generate a 6-digit OTP code
   */
  generateOTP() {
    return crypto.randomInt(100000, 999999).toString();
  }

  /**
   * Check rate limiting for OTP requests
   * @param {string} email - User email
   * @returns {Promise<{allowed: boolean, retryAfter?: number}>}
   */
  async checkRateLimit(email) {
    const MAX_REQUESTS_PER_HOUR = 5;
    const BLOCK_DURATION_MINUTES = 60;

    const now = new Date().toISOString();

    // Check if email is currently blocked
    const blocked = await db.getAsync(
      `SELECT blocked_until FROM otp_rate_limits 
       WHERE email = ? AND blocked_until > datetime('now')`,
      email
    );

    if (blocked) {
      const retryAfter = Math.ceil((new Date(blocked.blocked_until) - new Date()) / 1000);
      return { allowed: false, retryAfter };
    }

    // Get rate limit record
    const rateLimit = await db.getAsync(
      `SELECT * FROM otp_rate_limits 
       WHERE email = ? AND first_request_at > datetime('now', '-1 hour')`,
      email
    );

    if (!rateLimit) {
      // First request in this hour - create new record
      await db.runAsync(
        `INSERT OR REPLACE INTO otp_rate_limits (id, email, request_count, first_request_at, last_request_at)
         VALUES (?, ?, 1, datetime('now'), datetime('now'))`,
        uuidv4(), email
      );
      return { allowed: true };
    }

    if (rateLimit.request_count >= MAX_REQUESTS_PER_HOUR) {
      // Block user for 1 hour
      await db.runAsync(
        `UPDATE otp_rate_limits 
         SET blocked_until = datetime('now', '+${BLOCK_DURATION_MINUTES} minutes')
         WHERE email = ?`,
        email
      );
      return { allowed: false, retryAfter: BLOCK_DURATION_MINUTES * 60 };
    }

    // Increment request count
    await db.runAsync(
      `UPDATE otp_rate_limits 
       SET request_count = request_count + 1, last_request_at = datetime('now')
       WHERE email = ?`,
      email
    );

    return { allowed: true };
  }

  /**
   * Create and send OTP
   * @param {string} email - User email
   * @param {string} purpose - OTP purpose ('registration', 'password_reset', 'email_change')
   * @param {string} userName - User's full name
   * @returns {Promise<{success: boolean, message: string}>}
   */
  async sendOTP(email, purpose = 'registration', userName = 'User') {
    try {
      // Check rate limiting
      const rateCheck = await this.checkRateLimit(email);
      if (!rateCheck.allowed) {
        return {
          success: false,
          message: `Too many requests. Please try again in ${Math.ceil(rateCheck.retryAfter / 60)} minutes.`,
          retryAfter: rateCheck.retryAfter
        };
      }

      // Generate OTP
      const otpCode = this.generateOTP();
      const expiresAt = new Date(Date.now() + 5 * 60 * 1000); // 5 minutes

      // Invalidate any existing unverified OTPs for this email
      await db.runAsync(
        `DELETE FROM otp_verifications 
         WHERE email = ? AND is_verified = 0`,
        email
      );

      // Store OTP in database
      const otpId = uuidv4();
      await db.runAsync(
        `INSERT INTO otp_verifications 
         (id, email, otp_code, purpose, expires_at, max_attempts)
         VALUES (?, ?, ?, ?, ?, 3)`,
        otpId, email, otpCode, purpose, expiresAt.toISOString()
      );

      // Send email
      await emailService.sendOTPEmail(email, otpCode, userName);

      console.log(`✅ OTP sent to ${email} for ${purpose}`);

      return {
        success: true,
        message: 'OTP sent successfully',
        otpId,
        expiresAt: expiresAt.toISOString()
      };
    } catch (error) {
      console.error('❌ Error sending OTP:', error);
      return {
        success: false,
        message: `Failed to send OTP: ${error.message}`
      };
    }
  }

  /**
   * Verify OTP code
   * @param {string} email - User email
   * @param {string} otpCode - OTP code to verify
   * @param {string} purpose - OTP purpose
   * @returns {Promise<{success: boolean, message: string, verified?: boolean}>}
   */
  async verifyOTP(email, otpCode, purpose = 'registration') {
    try {
      // Find valid OTP
      const otp = await db.getAsync(
        `SELECT * FROM otp_verifications 
         WHERE email = ? AND purpose = ? AND is_verified = 0 AND expires_at > datetime('now')
         ORDER BY created_at DESC
         LIMIT 1`,
        email, purpose
      );

      if (!otp) {
        return {
          success: false,
          message: 'OTP expired or not found. Please request a new code.',
          verified: false
        };
      }

      // Check max attempts
      if (otp.attempts >= otp.max_attempts) {
        await db.runAsync(
          `DELETE FROM otp_verifications WHERE id = ?`,
          otp.id
        );
        return {
          success: false,
          message: 'Maximum verification attempts exceeded. Please request a new code.',
          verified: false
        };
      }

      // Verify OTP code
      if (otp.otp_code !== otpCode) {
        // Increment attempts
        await db.runAsync(
          `UPDATE otp_verifications SET attempts = attempts + 1 WHERE id = ?`,
          otp.id
        );

        const attemptsLeft = otp.max_attempts - (otp.attempts + 1);
        return {
          success: false,
          message: `Invalid OTP code. ${attemptsLeft} attempt(s) remaining.`,
          verified: false,
          attemptsLeft
        };
      }

      // Mark as verified
      await db.runAsync(
        `UPDATE otp_verifications 
         SET is_verified = 1, verified_at = datetime('now')
         WHERE id = ?`,
        otp.id
      );

      console.log(`✅ OTP verified successfully for ${email}`);

      return {
        success: true,
        message: 'OTP verified successfully',
        verified: true
      };
    } catch (error) {
      console.error('❌ Error verifying OTP:', error);
      return {
        success: false,
        message: `Verification failed: ${error.message}`,
        verified: false
      };
    }
  }

  /**
   * Check if email has been verified
   * @param {string} email - User email
   * @param {string} purpose - OTP purpose
   * @returns {Promise<boolean>}
   */
  async isEmailVerified(email, purpose = 'registration') {
    const verified = await db.getAsync(
      `SELECT id FROM otp_verifications 
       WHERE email = ? AND purpose = ? AND is_verified = 1
       ORDER BY verified_at DESC
       LIMIT 1`,
      email, purpose
    );
    return !!verified;
  }

  /**
   * Clean up expired OTPs (run periodically)
   */
  async cleanupExpiredOTPs() {
    try {
      const result = await db.runAsync(
        `DELETE FROM otp_verifications 
         WHERE expires_at < datetime('now', '-1 hour')`
      );
      console.log(`🧹 Cleaned up ${result.changes || 0} expired OTPs`);
    } catch (error) {
      console.error('❌ Error cleaning up OTPs:', error);
    }
  }

  /**
   * Clean up old rate limit records
   */
  async cleanupRateLimits() {
    try {
      const result = await db.runAsync(
        `DELETE FROM otp_rate_limits 
         WHERE first_request_at < datetime('now', '-24 hours')
         AND (blocked_until IS NULL OR blocked_until < datetime('now'))`
      );
      console.log(`🧹 Cleaned up ${result.changes || 0} old rate limit records`);
    } catch (error) {
      console.error('❌ Error cleaning up rate limits:', error);
    }
  }
}

module.exports = new OTPService();
