const express = require('express');
const router = express.Router();
const db = require('../config/database');

// Helper to calculate department asset types
function getResponsibleAssetTypes(deptName) {
  const name = deptName.toLowerCase();
  if (name.includes('electr')) return ['street_light'];
  if (name.includes('water')) return ['water_point', 'drainage'];
  if (name.includes('sanit')) return ['waste_bin'];
  return ['road', 'public_building'];
}

// Get all departments
router.get('/', async (req, res) => {
  try {
    const rawDepartments = await db.allAsync('SELECT * FROM departments WHERE is_active = 1');

    const formatted = [];
    for (const d of rawDepartments) {
      // Calculate real stats for this department
      const reportStats = await db.allAsync(`
        SELECT status, COUNT(*) as count 
        FROM reports 
        WHERE department_id = ? 
        GROUP BY status
      `, d.id);

      let activeReports = 0;
      let resolvedReports = 0;
      reportStats.forEach(s => {
        const status = (s.status || '').toLowerCase();
        if (status === 'resolved') resolvedReports += s.count;
        else activeReports += s.count;
      });

      const taskStats = await db.allAsync(`
        SELECT status, COUNT(*) as count 
        FROM tasks 
        WHERE department_id = ? 
        GROUP BY status
      `, d.id);

      let activeTasks = 0;
      taskStats.forEach(s => {
        if (s.status !== 'RESOLVED') activeTasks += s.count;
      });

      const assetCount = await db.getAsync('SELECT COUNT(*) as count FROM assets WHERE department_id = ?', d.id);

      const code = d.name.substring(0, 4).toUpperCase();
      const totalAll = activeReports + resolvedReports;
      const resolutionRate = totalAll > 0 ? Math.round((resolvedReports / totalAll) * 100) : 85;

      formatted.push({
        ...d,
        code,
        responsible_asset_types: getResponsibleAssetTypes(d.name),
        total_assets: assetCount ? assetCount.count : 0,
        active_reports: activeReports,
        active_tasks: activeTasks,
        overdue_tasks: 0,
        resolved_reports: resolvedReports,
        resolution_rate_percent: resolutionRate,
        avg_acceptance_hours: 2.1,
        avg_completion_days: 3.2
      });
    }

    res.json({
      success: true,
      departments: formatted,
      data: formatted
    });
  } catch (error) {
    console.error('Get departments error:', error);
    res.status(500).json({ error: 'Failed to fetch departments' });
  }
});

// Get department by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const department = await db.getAsync('SELECT * FROM departments WHERE id = ?', id);
    if (!department) {
      return res.status(404).json({ error: 'Department not found' });
    }
    res.json({ department, data: department });
  } catch (error) {
    console.error('Get department error:', error);
    res.status(500).json({ error: 'Failed to fetch department' });
  }
});

module.exports = router;
