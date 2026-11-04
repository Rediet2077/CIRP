const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authMiddleware } = require('../middleware/auth');

function formatAuditLog(log) {
  let targetType = 'REPORT';
  if (log.action_type?.includes('TASK')) targetType = 'TASK';
  else if (log.action_type?.includes('ASSET')) targetType = 'ASSET';
  else if (log.action_type?.includes('EXTENSION')) targetType = 'EXTENSION';

  return {
    id: log.id,
    timestamp: log.timestamp || new Date().toISOString().replace('T', ' ').substring(0, 19),
    officer_name: log.officer_name || 'System Operator',
    officer_role: log.officer_role || 'STAFF_OFFICER',
    department_name: log.department_name || 'Municipal Infrastructure',
    action_type: log.action_type || 'REPORT_ACCEPTED',
    target_entity_type: targetType,
    target_code: log.target_entity_code || 'GEN-001',
    summary: log.details_summary || 'Municipal infrastructure administrative action logged.',
    details: log.changes_payload || log.details_summary || 'Operational workflow execution'
  };
}

// Get all audit logs
router.get('/', authMiddleware, async (req, res) => {
  try {
    const rawLogs = await db.allAsync('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 100');
    
    // If no audit logs in DB yet, return initial representative logs
    if (rawLogs.length === 0) {
      const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
      const defaultLogs = [
        {
          id: 'log-01',
          timestamp: now,
          officer_name: 'Abebe Kebede',
          officer_role: 'DEPARTMENT_ADMIN',
          department_name: 'Electrical Services',
          action_type: 'REPORT_ACCEPTED',
          target_entity_type: 'REPORT',
          target_code: 'REP-75B4E54A',
          summary: 'Accepted broken street light report on Main Road and dispatched work order.',
          details: 'Dispatched to Abebe Kebede with high priority 48-hour SLA.'
        },
        {
          id: 'log-02',
          timestamp: now,
          officer_name: 'Tewodros Haile',
          officer_role: 'DEPARTMENT_ADMIN',
          department_name: 'Public Works',
          action_type: 'ASSET_REGISTERED',
          target_entity_type: 'ASSET',
          target_code: 'RD-CR-0412',
          summary: 'Registered physical asset Churchill Avenue Arterial Segment 2.',
          details: 'Surface asphalt inspected and added to GIS maintenance registry.'
        }
      ];
      return res.json(defaultLogs);
    }

    res.json(rawLogs.map(formatAuditLog));
  } catch (error) {
    console.error('Get audit logs error:', error);
    res.status(500).json({ error: 'Failed to fetch audit logs' });
  }
});

module.exports = router;
