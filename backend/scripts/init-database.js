const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');

async function initializeDatabase() {
  try {
    console.log('🚀 Starting SQLite database initialization...\n');

    // Create tables
    console.log('📋 Creating tables...\n');

    // Wait for all tables to be created
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone_number TEXT,
        role TEXT DEFAULT 'citizen' CHECK(role IN ('citizen', 'admin', 'contractor', 'department_head')),
        is_active INTEGER DEFAULT 1,
        is_email_verified INTEGER DEFAULT 0,
        profile_image TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS departments (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        head_id TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (head_id) REFERENCES users(id)
      );

      CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        icon TEXT,
        color TEXT,
        department_id TEXT,
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments(id)
      );

      CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        category_id TEXT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        location TEXT,
        latitude REAL,
        longitude REAL,
        address TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'assigned', 'in_progress', 'resolved', 'rejected')),
        priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'critical')),
        assigned_to TEXT,
        department_id TEXT,
        is_anonymous INTEGER DEFAULT 0,
        upvotes INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id),
        FOREIGN KEY (assigned_to) REFERENCES users(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
      );

      CREATE TABLE IF NOT EXISTS report_images (
        id TEXT PRIMARY KEY,
        report_id TEXT NOT NULL,
        image_url TEXT NOT NULL,
        is_primary INTEGER DEFAULT 0,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        report_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        content TEXT NOT NULL,
        is_internal INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS report_activity (
        id TEXT PRIMARY KEY,
        report_id TEXT NOT NULL,
        user_id TEXT,
        action TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id)
      );

      CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT,
        reference_id TEXT,
        is_read INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS contractors (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        company_name TEXT NOT NULL,
        license_number TEXT,
        specializations TEXT,
        rating REAL DEFAULT 0.00,
        total_jobs INTEGER DEFAULT 0,
        is_verified INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
      );

      CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        officer_name TEXT,
        officer_role TEXT,
        department_name TEXT,
        action TEXT,
        action_type TEXT,
        target_entity_id TEXT,
        target_entity_code TEXT,
        details_summary TEXT,
        changes_payload TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_id TEXT,
        table_name TEXT,
        record_id TEXT,
        old_data TEXT,
        new_data TEXT,
        ip_address TEXT,
        user_agent TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
      );
    `);

    console.log('✅ All tables created\n');

    // Create indexes
    console.log('📊 Creating indexes...');
    
    await db.execAsync(`
      CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
      CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
      CREATE INDEX IF NOT EXISTS idx_reports_category_id ON reports(category_id);
      CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at);
      CREATE INDEX IF NOT EXISTS idx_comments_report_id ON comments(report_id);
      CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
      CREATE INDEX IF NOT EXISTS idx_report_activity_report_id ON report_activity(report_id);
    `);
    console.log('✅ Indexes created\n');

    // Insert default data
    console.log('🌱 Seeding default data...\n');

    // Hash password for default users
    const defaultPassword = await bcrypt.hash('Test@123', 10);

    // Insert default admin user
    const adminId = uuidv4();
    await db.runAsync(`
      INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role, is_email_verified)
      VALUES (?, ?, ?, ?, ?, ?)
    `, [adminId, 'admin@cirp.com', defaultPassword, 'System Administrator', 'admin', 1]);
    console.log('✅ Admin user created (admin@cirp.com / Test@123)');

    // Insert default citizen user
    const citizenId = uuidv4();
    await db.runAsync(`
      INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role, is_email_verified, phone_number)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `, [citizenId, 'citizen@test.com', defaultPassword, 'Test Citizen', 'citizen', 1, '+251911234567']);
    console.log('✅ Test citizen user created (citizen@test.com / Test@123)');

    // Insert departments
    const dept1Id = uuidv4();
    const dept2Id = uuidv4();
    const dept3Id = uuidv4();
    const dept4Id = uuidv4();

    await db.runAsync('INSERT OR IGNORE INTO departments (id, name, description, contact_email) VALUES (?, ?, ?, ?)',
      [dept1Id, 'Public Works', 'Responsible for roads, infrastructure, and public facilities', 'publicworks@cirp.gov']);
    await db.runAsync('INSERT OR IGNORE INTO departments (id, name, description, contact_email) VALUES (?, ?, ?, ?)',
      [dept2Id, 'Water & Sewage', 'Manages water supply and sewage systems', 'water@cirp.gov']);
    await db.runAsync('INSERT OR IGNORE INTO departments (id, name, description, contact_email) VALUES (?, ?, ?, ?)',
      [dept3Id, 'Sanitation', 'Handles garbage collection and waste management', 'sanitation@cirp.gov']);
    await db.runAsync('INSERT OR IGNORE INTO departments (id, name, description, contact_email) VALUES (?, ?, ?, ?)',
      [dept4Id, 'Electrical Services', 'Maintains streetlights and electrical infrastructure', 'electrical@cirp.gov']);
    
    console.log('✅ 4 departments created');

    // Insert categories
    const cat1Id = uuidv4();
    const cat2Id = uuidv4();
    const cat3Id = uuidv4();
    const cat4Id = uuidv4();
    const cat5Id = uuidv4();
    const cat6Id = uuidv4();

    await db.runAsync('INSERT OR IGNORE INTO categories (id, name, description, icon, color, department_id) VALUES (?, ?, ?, ?, ?, ?)',
      [cat1Id, 'Road Damage', 'Potholes, cracks, and road surface issues', '🛣️', '#F44336', dept1Id]);
    await db.runAsync('INSERT OR IGNORE INTO categories (id, name, description, icon, color, department_id) VALUES (?, ?, ?, ?, ?, ?)',
      [cat2Id, 'Water Leakage', 'Water pipe leaks and supply issues', '💧', '#2196F3', dept2Id]);
    await db.runAsync('INSERT OR IGNORE INTO categories (id, name, description, icon, color, department_id) VALUES (?, ?, ?, ?, ?, ?)',
      [cat3Id, 'Garbage', 'Uncollected waste and sanitation issues', '🗑️', '#FF9800', dept3Id]);
    await db.runAsync('INSERT OR IGNORE INTO categories (id, name, description, icon, color, department_id) VALUES (?, ?, ?, ?, ?, ?)',
      [cat4Id, 'Streetlight', 'Broken or malfunctioning street lights', '💡', '#FFC107', dept4Id]);
    await db.runAsync('INSERT OR IGNORE INTO categories (id, name, description, icon, color, department_id) VALUES (?, ?, ?, ?, ?, ?)',
      [cat5Id, 'Drainage', 'Blocked drains and flooding issues', '🌊', '#00BCD4', dept2Id]);
    await db.runAsync('INSERT OR IGNORE INTO categories (id, name, description, icon, color, department_id) VALUES (?, ?, ?, ?, ?, ?)',
      [cat6Id, 'Other', 'Other community issues', '⋯', '#9C27B0', dept1Id]);

    console.log('✅ 6 categories created');

    // Insert sample reports
    await db.runAsync(`
      INSERT OR IGNORE INTO reports (id, user_id, category_id, title, description, location, status, priority, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-2 hours'))
    `, [uuidv4(), citizenId, cat1Id, 'Large pothole on Main Street', 'There is a dangerous pothole causing traffic problems', 'Main Street, Addis Ababa', 'pending', 'high']);

    await db.runAsync(`
      INSERT OR IGNORE INTO reports (id, user_id, category_id, title, description, location, status, priority, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-5 hours'))
    `, [uuidv4(), citizenId, cat2Id, 'Water pipe burst', 'Major water leak flooding the street', 'Bole Road', 'assigned', 'critical']);

    await db.runAsync(`
      INSERT OR IGNORE INTO reports (id, user_id, category_id, title, description, location, status, priority, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-2 days'))
    `, [uuidv4(), citizenId, cat3Id, 'Overflowing garbage bins', 'Garbage bins have not been emptied for 3 days', 'Megenagna', 'resolved', 'medium']);

    console.log('✅ 3 sample reports created');

    console.log('\n✨ Database initialization completed successfully!\n');
    console.log('📝 Default credentials:');
    console.log('   Admin: admin@cirp.com / Test@123');
    console.log('   Citizen: citizen@test.com / Test@123\n');
    console.log('📊 Database location: ' + require('path').resolve(process.env.DB_PATH || './database/cirp.db') + '\n');

    process.exit(0);

  } catch (error) {
    console.error('❌ Error initializing database:', error);
    process.exit(1);
  }
}

initializeDatabase();
