const sqlite3 = require('sqlite3').verbose();
const path = require('path');
require('dotenv').config();

const dbPath = path.resolve(process.env.DB_PATH || './database/cirp.db');

console.log('🔄 Adding OTP verification table...\n');

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('❌ Database connection error:', err);
    process.exit(1);
  }
  console.log(`✅ Connected to database: ${dbPath}\n`);
});

db.serialize(() => {
  // Create otp_verifications table
  db.run(`
    CREATE TABLE IF NOT EXISTS otp_verifications (
      id TEXT PRIMARY KEY,
      email TEXT NOT NULL,
      otp_code TEXT NOT NULL,
      purpose TEXT DEFAULT 'registration' CHECK(purpose IN ('registration', 'password_reset', 'email_change')),
      attempts INTEGER DEFAULT 0,
      max_attempts INTEGER DEFAULT 3,
      is_verified INTEGER DEFAULT 0,
      expires_at DATETIME NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      verified_at DATETIME
    )
  `, (err) => {
    if (err) {
      console.error('❌ Error creating otp_verifications table:', err);
      process.exit(1);
    }
    console.log('✅ otp_verifications table created/verified');
  });

  // Create index on email for faster lookups
  db.run(`
    CREATE INDEX IF NOT EXISTS idx_otp_email ON otp_verifications(email)
  `, (err) => {
    if (err) {
      console.error('❌ Error creating index:', err);
    } else {
      console.log('✅ Index on email created');
    }
  });

  // Create index on expires_at for cleanup queries
  db.run(`
    CREATE INDEX IF NOT EXISTS idx_otp_expires ON otp_verifications(expires_at)
  `, (err) => {
    if (err) {
      console.error('❌ Error creating index:', err);
    } else {
      console.log('✅ Index on expires_at created');
    }
  });

  // Create otp_rate_limits table to prevent abuse
  db.run(`
    CREATE TABLE IF NOT EXISTS otp_rate_limits (
      id TEXT PRIMARY KEY,
      email TEXT NOT NULL,
      request_count INTEGER DEFAULT 1,
      first_request_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      last_request_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      blocked_until DATETIME
    )
  `, (err) => {
    if (err) {
      console.error('❌ Error creating otp_rate_limits table:', err);
    } else {
      console.log('✅ otp_rate_limits table created/verified');
    }
  });

  // Create index on email for rate limiting
  db.run(`
    CREATE INDEX IF NOT EXISTS idx_rate_limit_email ON otp_rate_limits(email)
  `, (err) => {
    if (err) {
      console.error('❌ Error creating rate limit index:', err);
    } else {
      console.log('✅ Index on rate limit email created');
    }
  });
});

db.close((err) => {
  if (err) {
    console.error('❌ Error closing database:', err);
    process.exit(1);
  }
  console.log('\n✅ Migration completed successfully!');
  console.log('📋 Tables added:');
  console.log('   - otp_verifications (stores OTP codes with expiration)');
  console.log('   - otp_rate_limits (prevents abuse with rate limiting)');
  console.log('\n✨ Database is ready for OTP verification!\n');
});
