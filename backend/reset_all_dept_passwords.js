const bcrypt = require('bcryptjs');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'database', 'cirp.db');
const db = new sqlite3.Database(dbPath);

const newPassword = 'Test@123';

async function resetPasswords() {
  try {
    const hash = await bcrypt.hash(newPassword, 10);
    
    // Get all department heads
    db.all('SELECT id, email, full_name FROM users WHERE role = ?', ['department_head'], async (err, deptHeads) => {
      if (err) throw err;
      
      console.log(`\n🔄 Resetting passwords for ${deptHeads.length} department admins...\n`);
      
      for (const user of deptHeads) {
        db.run('UPDATE users SET password_hash = ? WHERE id = ?', [hash, user.id]);
        console.log(`✅ Reset: ${user.email} (${user.full_name})`);
      }
      
      console.log(`\n✅ All passwords reset to: ${newPassword}\n`);
      
      // Close database
      db.close();
    });
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    db.close();
  }
}

resetPasswords();
