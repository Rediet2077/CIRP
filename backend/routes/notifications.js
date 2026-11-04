const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authMiddleware } = require('../middleware/auth');

// Get user notifications
router.get('/', authMiddleware, async (req, res) => {
  try {
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
