const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');
const { authMiddleware, requireRole } = require('../middleware/auth');

function formatContractor(c) {
  return {
    ...c,
    contractor_company_name: c.contractor_company_name || null,
    license_number: c.license_number || null,
    is_contractor: Boolean(c.is_contractor),
    is_available: Boolean(c.is_available),
    active_tasks_count: Number(c.active_tasks_count || 0),
    completed_tasks_count: Number(c.completed_tasks_count || 0),
    overdue_tasks_count: Number(c.overdue_tasks_count || 0),
    performance_score: Number(c.performance_score || 95)
  };
}

// Get all contractors & staff
router.get('/', async (req, res) => {
  try {
    const { department_id } = req.query;
    let whereConditions = [];
    let params = [];

    if (department_id) {
      whereConditions.push('department_id = ?');
      params.push(department_id);
    }

    const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : '';
    const rawRows = await db.allAsync(`SELECT * FROM staff_contractors ${whereClause} ORDER BY performance_score DESC`, ...params);

    const contractors = rawRows.map(formatContractor);
    res.json({ contractors });
  } catch (error) {
    console.error('Get contractors error:', error);
    res.status(500).json({ error: 'Failed to fetch contractors' });
  }
});

// Add new contractor or staff
router.post('/', authMiddleware, requireRole('admin', 'department_head'), async (req, res) => {
  try {
    const {
      name,
      phone_number,
      email,
      department_id,
      department_name,
      role_type,
      position_title,
      specialization,
      is_contractor = false,
      contractor_company_name,
      license_number,
      performance_score = 95,
      is_available = true
    } = req.body;

    const id = `staff-${Date.now()}`;

    await db.runAsync(`
      INSERT INTO staff_contractors (
        id, name, phone_number, email, department_id, department_name, role_type,
        position_title, specialization, is_contractor, contractor_company_name,
        license_number, performance_score, is_available
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      id, name, phone_number, email, department_id, department_name, role_type,
      position_title, specialization, is_contractor ? 1 : 0, contractor_company_name || null,
      license_number || null, performance_score, is_available ? 1 : 0
    ]);

    const created = await db.getAsync('SELECT * FROM staff_contractors WHERE id = ?', id);
    res.status(201).json(formatContractor(created));
  } catch (error) {
    console.error('Add contractor error:', error);
    res.status(500).json({ error: 'Failed to add contractor' });
  }
});

module.exports = router;
