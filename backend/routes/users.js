const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');
const { authMiddleware, requireRole } = require('../middleware/auth');

function formatUser(u) {
  const role = u.role === 'admin' ? 'SYSTEM_ADMIN' : 'DEPARTMENT_ADMIN';
  const status = u.is_active ? 'ACTIVE' : 'INACTIVE';
  const firstName = u.full_name ? u.full_name.split(' ')[0] : 'User';
  const lastName = u.full_name && u.full_name.includes(' ') ? u.full_name.split(' ').slice(1).join(' ') : 'Officer';

  let department = null;
  if (u.department_id && u.department_name) {
    department = {
      id: u.department_id,
      name: u.department_name,
      code: u.department_name.substring(0, 4).toUpperCase()
    };
  }

  return {
    id: u.id,
    first_name: firstName,
    last_name: lastName,
    full_name: u.full_name,
    email: u.email,
    phone_number: u.phone_number || '',
    role,
    status,
    department
  };
}

// Get all administrative users
router.get('/', authMiddleware, async (req, res) => {
  try {
    const { department_id, search } = req.query;

    let whereConditions = ["u.role IN ('admin', 'department_head')"];
    let params = [];

    if (req.user.role === 'department_head' && req.user.department_id) {
      whereConditions.push('u.department_id = ?');
      params.push(req.user.department_id);
    } else if (department_id && department_id !== 'all') {
      whereConditions.push('u.department_id = ?');
      params.push(department_id);
    }

    if (search) {
      whereConditions.push('(u.full_name LIKE ? OR u.email LIKE ?)');
      params.push(`%${search}%`, `%${search}%`);
    }

    const whereClause = `WHERE ${whereConditions.join(' AND ')}`;

    const rawUsers = await db.allAsync(`
      SELECT 
        u.id, u.email, u.full_name, u.phone_number, u.role, u.is_active, u.department_id,
        d.name as department_name
      FROM users u
      LEFT JOIN departments d ON u.department_id = d.id
      ${whereClause}
      ORDER BY u.created_at DESC
    `, ...params);

    const users = rawUsers.map(formatUser);
    res.json(users);
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

// Get user by ID
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const rawUser = await db.getAsync(`
      SELECT 
        u.id, u.email, u.full_name, u.phone_number, u.role, u.is_active, u.department_id,
        d.name as department_name
      FROM users u
      LEFT JOIN departments d ON u.department_id = d.id
      WHERE u.id = ?
    `, [id]);

    if (!rawUser) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(formatUser(rawUser));
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
});

module.exports = router;
