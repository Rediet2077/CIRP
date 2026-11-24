const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authMiddleware } = require('../middleware/auth');

const STAFF_ROLES = ['admin', 'department_head'];

db.run(`CREATE TABLE IF NOT EXISTS staff_notification_reads (
  user_id TEXT NOT NULL,
  notif_key TEXT NOT NULL,
  PRIMARY KEY (user_id, notif_key)
)`);

const toIso = (v) => {
  if (!v) return new Date().toISOString();
  const str = String(v);
  return /[zZ]|[+-]\d\d:?\d\d$/.test(str) ? str : `${str.replace(' ', 'T')}Z`;
};

// Notifications for admins / department heads, built from live reports, tasks and extension requests
async function buildStaffNotifications(user, requestedDept) {
  const deptId = user.role === 'department_head'
    ? user.department_id
    : (requestedDept && requestedDept !== 'all' ? requestedDept : null);
  const scope = (col) => (deptId ? ` AND ${col} = ?` : '');
  const args = deptId ? [deptId] : [];
  const today = new Date().toISOString().substring(0, 10);
  const items = [];

  const reports = await db.allAsync(
    `SELECT r.id, r.report_code, r.title, r.address, r.priority, r.created_at, r.department_id, d.name AS dept
       FROM reports r LEFT JOIN departments d ON d.id = r.department_id
      WHERE LOWER(r.status) = 'pending'${deptId ? ' AND r.department_id IN (SELECT id FROM departments WHERE name = (SELECT name FROM departments WHERE id = ?))' : ''} ORDER BY r.created_at DESC LIMIT 30`, args);
  for (const r of reports) {
    const pr = String(r.priority || 'medium').toUpperCase();
    items.push({
      key: `new-report:${r.id}`, title: 'New citizen report awaiting review',
      message: `${r.title}${r.address ? ` at ${r.address}` : ''} was submitted and needs to be accepted or rejected.`,
      category: 'NEW_REPORT', priority: pr, created_at: toIso(r.created_at),
      target_url: '/dashboard/reports', department_id: r.department_id, department_name: r.dept, entity_code: r.report_code,
    });
  }

  const overdue = await db.allAsync(
    `SELECT * FROM tasks WHERE status NOT IN ('RESOLVED','CANCELLED')
        AND deadline_date IS NOT NULL AND deadline_date < ?${scope('department_id')} ORDER BY deadline_date LIMIT 30`, [today, ...args]);
  for (const t of overdue) {
    items.push({
      key: `overdue:${t.id}`, title: 'Work order is past its deadline',
      message: `${t.task_code} assigned to ${t.assigned_worker_name || 'the assignee'} was due on ${t.deadline_date} and is not finished.`,
      category: 'ESCALATION', priority: 'CRITICAL', created_at: toIso(`${t.deadline_date} 00:00:00`),
      target_url: '/dashboard/deadlines', department_id: t.department_id, department_name: t.department_name, entity_code: t.task_code,
    });
  }

  const verify = await db.allAsync(
    `SELECT * FROM tasks WHERE status = 'COMPLETED_PENDING_VERIFICATION'${scope('department_id')} ORDER BY created_at DESC LIMIT 30`, args);
  for (const t of verify) {
    items.push({
      key: `verify:${t.id}`, title: 'Work finished and ready for verification',
      message: `${t.assigned_worker_name || 'The assignee'} marked ${t.task_code} as complete. Verify it to resolve the report.`,
      category: 'TASK_COMPLETED', priority: 'MEDIUM', created_at: toIso(t.created_at),
      target_url: '/dashboard/reports', department_id: t.department_id, department_name: t.department_name, entity_code: t.task_code,
    });
  }

  const exts = await db.allAsync(
    `SELECT * FROM extensions WHERE status = 'PENDING'${scope('department_id')} ORDER BY requested_at DESC LIMIT 30`, args);
  for (const e of exts) {
    items.push({
      key: `ext:${e.id}`, title: 'Deadline extension requested',
      message: `${e.task_code || 'A work order'}: new deadline ${e.requested_new_deadline || 'requested'}. ${e.reason_category || ''}`.trim(),
      category: 'EXTENSION_REQUEST', priority: 'MEDIUM', created_at: toIso(e.requested_at),
      target_url: '/dashboard/extensions', department_id: e.department_id, entity_code: e.task_code,
    });
  }

  const reads = await db.allAsync('SELECT notif_key FROM staff_notification_reads WHERE user_id = ?', [user.id]);
  const readSet = new Set(reads.map((r) => r.notif_key));
  return items
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
    // the admin's schema allows missing fields but not null ones
    .map(({ key, ...n }) => Object.fromEntries(Object.entries({ id: key, is_read: readSet.has(key), ...n }).filter(([, v]) => v != null)));
}

// Mark staff notifications read / unread: { ids: [...], read: true|false }
router.post('/staff/read', authMiddleware, async (req, res) => {
  try {
    if (!STAFF_ROLES.includes(req.user.role)) return res.status(403).json({ error: 'Insufficient permissions' });
    const ids = Array.isArray(req.body.ids) ? req.body.ids.map(String).slice(0, 500) : [];
    const read = req.body.read !== false;
    for (const key of ids) {
      if (read) {
        await db.runAsync('INSERT OR IGNORE INTO staff_notification_reads (user_id, notif_key) VALUES (?, ?)', [req.user.id, key]);
      } else {
        await db.runAsync('DELETE FROM staff_notification_reads WHERE user_id = ? AND notif_key = ?', [req.user.id, key]);
      }
    }
    res.json({ success: true });
  } catch (error) {
    console.error('Staff read error:', error);
    res.status(500).json({ error: 'Failed to update notifications' });
  }
});

// Get user notifications
router.get('/', authMiddleware, async (req, res) => {
  try {
    if (STAFF_ROLES.includes(req.user.role)) {
      const notifications = await buildStaffNotifications(req.user, req.query.department_id);
      return res.json({
        success: true,
        notifications,
        count: notifications.length,
        unread_count: notifications.filter((n) => !n.is_read).length,
      });
    }
    const rawNotifications = await db.allAsync(
      'SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50',
      [req.userId]
    );

    const formatted = rawNotifications.map(n => ({
      ...n,
      is_read: Boolean(n.is_read)
    }));

    const unreadCount = formatted.filter(n => !n.is_read).length;

    res.json({
      success: true,
      notifications: formatted,
      data: formatted,
      count: formatted.length,
      unread_count: unreadCount
    });
  } catch (error) {
    console.error('Get notifications error:', error);
    res.status(500).json({ error: 'Failed to fetch notifications' });
  }
});

// Mark notification as read
router.patch('/:id/read', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    await db.runAsync('UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?', [id, req.userId]);
    res.json({ success: true, message: 'Notification marked as read' });
  } catch (error) {
    console.error('Mark read error:', error);
    res.status(500).json({ error: 'Failed to update notification' });
  }
});

// Delete notification
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    await db.runAsync('DELETE FROM notifications WHERE id = ? AND user_id = ?', [id, req.userId]);
    res.json({ success: true, message: 'Notification deleted' });
  } catch (error) {
    console.error('Delete notification error:', error);
    res.status(500).json({ error: 'Failed to delete notification' });
  }
});

module.exports = router;
