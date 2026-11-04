const sqlite3 = require('sqlite3').verbose();
const path = require('path');
require('dotenv').config();

const dbPath = path.resolve(process.env.DB_PATH || './database/cirp.db');

console.log('🔄 Adding department_id column to users table...\n');

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('❌ Database connection error:', err);
    process.exit(1);
  }
  console.log(`✅ Connected to database: ${dbPath}\n`);
});

db.serialize(() => {
  // Add department_id column to users table
  db.run(`
    ALTER TABLE users ADD COLUMN department_id TEXT
  `, (err) => {
    if (err && !err.message.includes('duplicate column')) {
      console.error('❌ Error adding department_id column:', err);
    } else if (err) {
      console.log('ℹ️  Column department_id already exists');
    } else {
      console.log('✅ Added department_id column to users table');
    }
  });

  // Add foreign key index
  db.run(`
    CREATE INDEX IF NOT EXISTS idx_users_department ON users(department_id)
  `, (err) => {
    if (err) {
      console.error('❌ Error creating index:', err);
    } else {
      console.log('✅ Created index on department_id');
    }
  });
});

setTimeout(() => {
  console.log('\n✅ Migration completed successfully!\n');
  db.close();
}, 500);
