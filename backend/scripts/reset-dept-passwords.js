const bcrypt = require('bcryptjs');
const db = require('../config/database');

async function resetDepartmentPasswords() {
  try {
    console.log('🔐 Resetting department admin passwords...\n');

    // Hash the password
    const newPassword = await bcrypt.hash('Test@123', 10);

    // Get all department head users
    const deptHeads = await db.allAsync(
      `SELECT id, email, full_name FROM users WHERE role = 'department_head'`
    );

    console.log(`Found ${deptHeads.length} department admin(s)\n`);

    // Update each one
    for (const user of deptHeads) {
      await db.runAsync(
        `UPDATE users SET password_hash = ? WHERE id = ?`,
        [newPassword, user.id]
      );
      console.log(`✅ Reset password for: ${user.email} (${user.full_name})`);
    }

    console.log('\n✨ All department admin passwords reset to: Test@123\n');
    console.log('📝 Department Admin Credentials:');
    for (const user of deptHeads) {
      console.log(`   ${user.email} / Test@123`);
    }
    console.log();

    db.close();
  } catch (error) {
    console.error('❌ Error resetting passwords:', error);
    process.exit(1);
  }
}

resetDepartmentPasswords();
