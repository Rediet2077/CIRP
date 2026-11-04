const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');
const { authMiddleware, requireRole } = require('../middleware/auth');

function formatExtension(ext) {
  return {
    id: ext.id,
    task_id: ext.task_id,
    task_code: ext.task_code || 'TSK-001',
    report_code: ext.report_code || 'REP-001',
    asset_code: ext.asset_code || 'N/A',
    department_id: ext.department_id || 'dept-elec',
    original_deadline: ext.original_deadline || '2026-11-01',
    requested_new_deadline: ext.requested_new_deadline || '2026-11-15',
    reason_category: ext.reason_category || 'Waiting for spare parts',
    detailed_explanation: ext.detailed_explanation || 'Pending procurement of replacement components.',
    supporting_evidence_note: ext.supporting_evidence_note || '',
    requested_by: ext.requested_by || 'Field Lead',
    requested_at: ext.requested_at || new Date().toISOString().replace('T', ' ').substring(0, 19),
    status: ext.status || 'PENDING',
    decision_date: ext.decision_date || undefined,
    decided_by: ext.decided_by || undefined,
    decision_comment: ext.decision_comment || undefined
  };
}

// Get all extensions
router.get('/', authMiddleware, async (req, res) => {
  try {
    const rawExtensions = await db.allAsync('SELECT * FROM extensions ORDER BY requested_at DESC');
    res.json(rawExtensions.map(formatExtension));
  } catch (error) {
    console.error('Get extensions error:', error);
    res.status(500).json({ error: 'Failed to fetch extensions' });
  }
});

// Request new deadline extension
router.post('/', authMiddleware, async (req, res) => {
  try {
    const {
      taskId,
      requestedNewDeadline,
      reasonCategory,
      detailedExplanation,
      supportingEvidenceNote,
      requestedBy
    } = req.body;

    const task = await db.getAsync('SELECT * FROM tasks WHERE id = ?', taskId);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const id = `ext-${Date.now()}`;
    const now = new Date().toISOString().replace('T', ' ').substring(0, 19);

    await db.runAsync(`
      INSERT INTO extensions (
        id, task_id, task_code, report_code, asset_code, department_id,
        original_deadline, requested_new_deadline, reason_category, detailed_explanation,
        supporting_evidence_note, requested_by, requested_at, status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
    `, [
      id, taskId, task.task_code, task.report_code, task.asset_code, task.department_id,
      task.deadline_date, requestedNewDeadline, reasonCategory, detailedExplanation,
      supportingEvidenceNote || '', requestedBy || req.user.full_name, now
    ]);

    // Record audit log
    await db.runAsync(`
      INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
      VALUES (?, ?, 'CONTRACTOR_LEAD', ?, 'EXTENSION_REQUESTED', ?, ?, ?)
    `, [
      uuidv4(),
      requestedBy || req.user.full_name,
      task.department_name,
      id,
      task.task_code,
      `Deadline extension requested to ${requestedNewDeadline}: ${reasonCategory}`
    ]);

    const created = await db.getAsync('SELECT * FROM extensions WHERE id = ?', id);
    res.status(201).json(formatExtension(created));
  } catch (error) {
    console.error('Request extension error:', error);
    res.status(500).json({ error: 'Failed to request extension' });
  }
});

// Decide extension (Approve / Reject)
router.post('/:id/decide', authMiddleware, requireRole('admin', 'department_head'), async (req, res) => {
  try {
    const { id } = req.params;
    const { approve, decidedBy, decisionComment } = req.body;

    const ext = await db.getAsync('SELECT * FROM extensions WHERE id = ?', id);
    if (!ext) {
      return res.status(404).json({ error: 'Extension not found' });
    }

    const status = approve ? 'APPROVED' : 'REJECTED';
    const now = new Date().toISOString().replace('T', ' ').substring(0, 19);

    await db.runAsync(`
      UPDATE extensions 
      SET status = ?, decision_date = ?, decided_by = ?, decision_comment = ?
      WHERE id = ?
    `, [status, now, decidedBy || req.user.full_name, decisionComment || '', id]);

    // If approved, update task deadline
    if (approve && ext.task_id) {
      await db.runAsync(`
        UPDATE tasks 
        SET deadline_date = ?
        WHERE id = ?
      `, [ext.requested_new_deadline, ext.task_id]);
    }

    // Record audit log
    await db.runAsync(`
      INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
      VALUES (?, ?, 'DEPARTMENT_ADMIN', 'Municipal Administration', ?, ?, ?, ?)
    `, [
      uuidv4(),
      decidedBy || req.user.full_name,
      approve ? 'EXTENSION_APPROVED' : 'EXTENSION_REJECTED',
      id,
      ext.task_code,
      `Extension ${status}: ${decisionComment || 'Decision processed'}`
    ]);

    const updated = await db.getAsync('SELECT * FROM extensions WHERE id = ?', id);
    res.json(formatExtension(updated));
  } catch (error) {
    console.error('Decide extension error:', error);
    res.status(500).json({ error: 'Failed to process extension decision' });
  }
});

module.exports = router;
