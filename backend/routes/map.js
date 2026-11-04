const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authMiddleware } = require('../middleware/auth');

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

// Get assets for GIS map
router.get('/assets', authMiddleware, async (req, res) => {
  try {
    const { department_id } = req.query;
    let whereConditions = [];
    let params = [];

    if (department_id && department_id !== 'all') {
      whereConditions.push('department_id = ?');
      params.push(department_id);
    }

    const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : '';
    const rawAssets = await db.allAsync(`SELECT * FROM assets ${whereClause}`, ...params);

    res.json(rawAssets.map(formatAsset));
  } catch (error) {
    console.error('Map assets error:', error);
    res.status(500).json({ error: 'Failed to fetch map assets' });
  }
});

module.exports = router;
