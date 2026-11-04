const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const dbPath = path.resolve(process.env.DB_PATH || './database/cirp.db');

console.log('🔄 Creating department head users...\n');

async function createDepartmentUsers() {
  const db = new sqlite3.Database(dbPath, async (err) => {
    if (err) {
      console.error('❌ Database connection error:', err);
      process.exit(1);
    }
    console.log(`✅ Connected to database: ${dbPath}\n`);

    try {
      // Hash password
      const password = await bcrypt.hash('Admin@123', 10);

      // Get departments
      db.all('SELECT id, name FROM departments', [], async (err, departments) => {
        if (err) {
          console.error('❌ Error getting departments:', err);
          db.close();
          return;
        }

        console.log(`Found ${departments.length} departments\n`);

        for (const dept of departments) {
          const userId = uuidv4();
          const email = `${dept.name.toLowerCase().replace(/\s+/g, '.')}@cirp.com`;
          const fullName = `${dept.name} Manager`;

          db.run(`
            INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role, is_email_verified, department_id)
            VALUES (?, ?, ?, ?, 'department_head', 1, ?)
          `, [userId, email, password, fullName, dept.id], function(err) {
            if (err) {
              console.error(`❌ Error creating user for ${dept.name}:`, err);
            } else if (this.changes > 0) {
              console.log(`✅ Created: ${email} (${fullName}) - Password: Admin@123`);
            } else {
              console.log(`ℹ️  User ${email} already exists`);
            }
          });
        }

        setTimeout(() => {
          console.log('\n✨ Department head users created successfully!\n');
          console.log('📋 Login credentials:');
          console.log('   - public.works@cirp.com / Admin@123 (Public Works)');
          console.log('   - water.&.sewage@cirp.com / Admin@123 (Water & Sewage)');
          console.log('   - sanitation@cirp.com / Admin@123 (Sanitation)');
          console.log('   - electrical.services@cirp.com / Admin@123 (Electrical Services)');
          console.log('\n');
          db.close();
        }, 1000);
      });
    } catch (err) {
      console.error('❌ Error:', err);
      db.close();
    }
  });
}

createDepartmentUsers();
