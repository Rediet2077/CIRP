const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');
const { authMiddleware, requireRole } = require('../middleware/auth');

function formatAsset(a) {
  let specificData = { type: a.asset_type_id, specs: {} };
  if (a.specific_data) {
    try {
      specificData = typeof a.specific_data === 'string' ? JSON.parse(a.specific_data) : a.specific_data;
    } catch (e) {}
  }

  return {
    ...a,
    latitude: Number(a.latitude),
    longitude: Number(a.longitude),
    active_reports_count: Number(a.active_reports_count || 0),
    specific_data: specificData
  };
}

// Get all assets
router.get('/', async (req, res) => {
  try {
    const { department_id, search } = req.query;
    let whereConditions = [];
    let params = [];

    if (department_id) {
      whereConditions.push('department_id = ?');
      params.push(department_id);
    }

    if (search) {
      whereConditions.push('(asset_code LIKE ? OR name LIKE ? OR address LIKE ?)');
      params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }

    const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : '';
    const rawAssets = await db.allAsync(`SELECT * FROM assets ${whereClause} ORDER BY registered_at DESC`, ...params);

    const assets = rawAssets.map(formatAsset);
    res.json({ assets });
  } catch (error) {
    console.error('Get assets error:', error);
    res.status(500).json({ error: 'Failed to fetch assets' });
  }
});

// Get single asset
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const rawAsset = await db.getAsync('SELECT * FROM assets WHERE id = ?', id);
    if (!rawAsset) {
      return res.status(404).json({ error: 'Asset not found' });
    }
    res.json(formatAsset(rawAsset));
  } catch (error) {
    console.error('Get asset error:', error);
    res.status(500).json({ error: 'Failed to fetch asset' });
  }
});

// Register new asset
router.post('/', authMiddleware, requireRole('admin', 'department_head'), async (req, res) => {
  try {
    const {
      asset_type_id,
      asset_type_label,
      department_id,
      department_name,
      name,
      description,
      status = 'ACTIVE',
      condition = 'GOOD',
      installation_date,
      latitude,
      longitude,
      address,
      landmark,
      specific_data
    } = req.body;

    const id = `ast-${Date.now()}`;
    const codePrefix = (asset_type_id || 'AST').substring(0, 3).toUpperCase();
    const asset_code = `${codePrefix}-${Math.floor(1000 + Math.random() * 9000)}`;
    const now = new Date().toISOString().replace('T', ' ').substring(0, 19);

    await db.runAsync(`
      INSERT INTO assets (
        id, asset_code, asset_type_id, asset_type_label, department_id, department_name,
        name, description, status, condition, installation_date, latitude, longitude,
        address, landmark, registered_by, registered_at, updated_at, last_inspection_date,
        active_reports_count, specific_data
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      id, asset_code, asset_type_id, asset_type_label || name, department_id, department_name,
      name, description, status, condition, installation_date || now.split(' ')[0],
      latitude || 9.0054, longitude || 38.7636, address || '', landmark || '',
      req.user.full_name || 'Inspector', now, now, now.split(' ')[0], 0,
      JSON.stringify(specific_data || { type: asset_type_id, specs: {} })
    ]);

    const created = await db.getAsync('SELECT * FROM assets WHERE id = ?', id);
    res.status(201).json(formatAsset(created));
  } catch (error) {
    console.error('Register asset error:', error);
    res.status(500).json({ error: 'Failed to register asset' });
  }
});

module.exports = router;
