const nodemailer = require('nodemailer');
require('dotenv').config();

class EmailService {
  constructor() {
    this.transporter = nodemailer.createTransport({
      service: process.env.EMAIL_SERVICE || 'gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_APP_PASSWORD,
      },
    });
  }

  /**
   * Send OTP verification email
   * @param {string} to - Recipient email address
   * @param {string} otp - 6-digit OTP code
   * @param {string} userName - User's full name
   */
  async sendOTPEmail(to, otp, userName = 'User') {
    const mailOptions = {
      from: `"${process.env.EMAIL_FROM_NAME || 'CIRP'}" <${process.env.EMAIL_USER}>`,
      to,
      subject: 'Verify Your Email - CIRP Registration',
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }
            .otp-box { background: #f5f5f5; border: 2px dashed #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0; }
            .otp-code { font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #667eea; font-family: 'Courier New', monospace; }
            .footer { background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }
            .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 20px 0; }
            .btn { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1 style="margin: 0;">🏛️ CIRP</h1>
              <p style="margin: 10px 0 0 0; font-size: 16px;">Community Infrastructure Reporting Platform</p>
            </div>
            <div class="content">
              <h2>Hello ${userName}! 👋</h2>
              <p>Thank you for registering with CIRP. To complete your registration and verify your email address, please use the One-Time Password (OTP) below:</p>
              
              <div class="otp-box">
                <p style="margin: 0 0 10px 0; font-size: 14px; color: #666;">Your Verification Code</p>
                <div class="otp-code">${otp}</div>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">Valid for 5 minutes</p>
              </div>

              <p><strong>To verify your email:</strong></p>
              <ol>
                <li>Open the CIRP mobile app</li>
                <li>Enter the 6-digit code shown above</li>
                <li>Click "Verify" to complete registration</li>
              </ol>

              <div class="warning">
                <strong>⚠️ Security Notice:</strong> This OTP is valid for 5 minutes only. If you didn't request this code, please ignore this email.
              </div>

              <p>Need help? Contact our support team at <a href="mailto:${process.env.EMAIL_USER}">support@cirp.com</a></p>
            </div>
            <div class="footer">
              <p><strong>CIRP - Community Infrastructure Reporting Platform</strong></p>
              <p>This is an automated email. Please do not reply to this message.</p>
              <p>© ${new Date().getFullYear()} CIRP. All rights reserved.</p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
Hello ${userName}!

Thank you for registering with CIRP. Your verification code is: ${otp}

This code is valid for 5 minutes. Please enter it in the mobile app to complete your registration.

If you didn't request this code, please ignore this email.

---
CIRP - Community Infrastructure Reporting Platform
      `.trim(),
    };

    try {
      const info = await this.transporter.sendMail(mailOptions);
      console.log('✅ OTP email sent successfully:', info.messageId);
      return { success: true, messageId: info.messageId };
    } catch (error) {
      console.error('❌ Failed to send OTP email:', error);
      throw new Error(`Failed to send email: ${error.message}`);
    }
  }

  /**
   * Send welcome email after successful verification
   * @param {string} to - Recipient email address
   * @param {string} userName - User's full name
   */
  async sendWelcomeEmail(to, userName) {
    const mailOptions = {
      from: `"${process.env.EMAIL_FROM_NAME || 'CIRP'}" <${process.env.EMAIL_USER}>`,
      to,
      subject: 'Welcome to CIRP! 🎉',
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
            .footer { background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>🎉 Welcome to CIRP!</h1>
            </div>
            <div class="content">
              <h2>Hello ${userName}!</h2>
              <p>Your email has been successfully verified. Welcome to the Community Infrastructure Reporting Platform!</p>
              <p>You can now:</p>
              <ul>
                <li>🗺️ View infrastructure issues on the map</li>
                <li>📸 Report problems in your community</li>
                <li>📊 Track the status of your reports</li>
                <li>👥 Connect with other community members</li>
              </ul>
              <p>Thank you for joining us in making our community better! 🏛️</p>
            </div>
            <div class="footer">
              <p>© ${new Date().getFullYear()} CIRP. All rights reserved.</p>
            </div>
          </div>
        </body>
        </html>
      `,
    };

    try {
      await this.transporter.sendMail(mailOptions);
      console.log('✅ Welcome email sent successfully');
    } catch (error) {
      console.error('❌ Failed to send welcome email:', error);
      // Don't throw error for welcome email - it's not critical
    }
  }

  /**
   * Test email connection
   */
  async testConnection() {
    try {
      await this.transporter.verify();
      console.log('✅ Email service connection verified');
      return true;
    } catch (error) {
      console.error('❌ Email service connection failed:', error);
      return false;
    }
  }
}

module.exports = new EmailService();
