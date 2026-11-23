const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');
const { authMiddleware, requireRole } = require('../middleware/auth');

function formatTask(task) {
  let progressNotes = [];
  try {
    progressNotes = task.progress_notes ? JSON.parse(task.progress_notes) : [];
  } catch (e) {
    progressNotes = [];
  }

  let completionSubmission = undefined;
  if (task.completion_submission) {
    try {
      completionSubmission = JSON.parse(task.completion_submission);
    } catch (e) {}
  }

  let rejectionHistory = [];
  if (task.rejection_history) {
    try {
      rejectionHistory = JSON.parse(task.rejection_history);
    } catch (e) {}
  }

  let extensions = [];
  if (task.extensions) {
    try {
      extensions = JSON.parse(task.extensions);
    } catch (e) {}
  }

  // Calculate overdue status
  let isOverdue = false;
  let daysOverdue = 0;
  if (task.deadline_date && task.status !== 'RESOLVED') {
    const deadline = new Date(task.deadline_date);
    const now = new Date();
    if (now > deadline) {
      isOverdue = true;
      daysOverdue = Math.ceil((now - deadline) / (1000 * 60 * 60 * 24));
    }
  }

  return {
    ...task,
    is_contractor: Boolean(task.is_contractor),
    is_overdue: isOverdue,
    days_overdue: daysOverdue,
    progress_percentage: Number(task.progress_percentage || 0),
    progress_notes: progressNotes,
    completion_submission: completionSubmission,
    rejection_history: rejectionHistory.length > 0 ? rejectionHistory : undefined,
    extensions: extensions
  };
}

// Tell the citizen who filed the report about a change in its work order
async function notifyCitizen(reportId, title, message) {
  if (!reportId) return;
  const report = await db.getAsync('SELECT user_id FROM reports WHERE id = ?', reportId);
  if (!report || !report.user_id) return;
  await db.runAsync(`
    INSERT INTO notifications (id, user_id, title, message, type, reference_id)
    VALUES (?, ?, ?, ?, 'status_update', ?)
  `, [uuidv4(), report.user_id, title, message, reportId]);
}

function appendNote(task, author, note, percentage) {
  let notes = [];
  try {
    notes = task.progress_notes ? JSON.parse(task.progress_notes) : [];
  } catch (e) {}
  notes.push({
    timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
    author,
    note,
    percentage: Number(percentage) || 0
  });
  return JSON.stringify(notes);
}

// Get all tasks
router.get('/', authMiddleware, async (req, res) => {
  try {
    const { department_id, search } = req.query;
    let whereConditions = [];
    let params = [];

    // Filter by department if department head
    if (req.user.role === 'department_head' && req.user.department_id) {
      whereConditions.push('department_id = ?');
      params.push(req.user.department_id);
    } else if (department_id && department_id !== 'all') {
      whereConditions.push('department_id = ?');
      params.push(department_id);
    }

    if (search) {
      whereConditions.push('(task_code LIKE ? OR work_description LIKE ? OR assigned_worker_name LIKE ?)');
      params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }

    const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : '';
    const rawTasks = await db.allAsync(`SELECT * FROM tasks ${whereClause} ORDER BY created_at DESC`, ...params);

    const tasks = rawTasks.map(formatTask);
    res.json({ tasks });
  } catch (error) {
    console.error('Get tasks error:', error);
    res.status(500).json({ error: 'Failed to fetch tasks' });
  }
});

// Get single task
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const rawTask = await db.getAsync('SELECT * FROM tasks WHERE id = ?', id);
    if (!rawTask) {
      return res.status(404).json({ error: 'Task not found' });
    }
    res.json(formatTask(rawTask));
  } catch (error) {
    console.error('Get task error:', error);
    res.status(500).json({ error: 'Failed to fetch task' });
  }
});

// Update task progress
router.post('/:id/progress', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { progressPercentage, newStatus, progressNote, authorName } = req.body;

    const task = await db.getAsync('SELECT * FROM tasks WHERE id = ?', id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }
    if (task.status === 'RESOLVED') {
      return res.status(409).json({ error: 'This work order is already resolved' });
    }
    const percentage = Number(progressPercentage);
    if (!Number.isFinite(percentage) || percentage < 0 || percentage > 100) {
      return res.status(400).json({ error: 'Progress must be a number between 0 and 100' });
    }

    let progressNotes = [];
    try {
      progressNotes = task.progress_notes ? JSON.parse(task.progress_notes) : [];
    } catch (e) {}

    const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
    progressNotes.push({
      timestamp: now,
      author: authorName || req.user.full_name || 'Worker',
      note: progressNote || `Progress updated to ${percentage}%`,
      percentage
    });

    const statusToSet = newStatus || (percentage > 0 ? 'IN_PROGRESS' : task.status);

    await db.runAsync(`
      UPDATE tasks 
      SET progress_percentage = ?, status = ?, progress_notes = ?
      WHERE id = ?
    `, [percentage, statusToSet, JSON.stringify(progressNotes), id]);

    await notifyCitizen(
      task.report_id,
      'Work update on your report',
      `Report #${task.report_code}: ${progressNote || 'Work is progressing'} (${percentage}% complete).`
    );

    // Also update report status if task transitioned to IN_PROGRESS
    if (task.report_id && statusToSet === 'IN_PROGRESS') {
      await db.runAsync("UPDATE reports SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP WHERE id = ?", task.report_id);
    }

    // Record audit log
    await db.runAsync(`
      INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
      VALUES (?, ?, 'STAFF_OFFICER', ?, 'TASK_PROGRESS_UPDATED', ?, ?, ?)
    `, [
      uuidv4(),
      authorName || req.user.full_name,
      task.department_name,
      id,
      task.task_code,
      `Progress updated to ${progressPercentage}%: ${progressNote}`
    ]);

    const updated = await db.getAsync('SELECT * FROM tasks WHERE id = ?', id);
    res.json(formatTask(updated));
  } catch (error) {
    console.error('Update progress error:', error);
    res.status(500).json({ error: 'Failed to update task progress' });
  }
});

// Submit task completion
router.post('/:id/complete', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { completionNotes, completionDate, beforePhotos = [], afterPhotos = [], submittedBy } = req.body;

    const task = await db.getAsync('SELECT * FROM tasks WHERE id = ?', id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const submission = {
      completion_date: completionDate || new Date().toISOString().split('T')[0],
      completion_notes: completionNotes || 'Work completed per engineering specifications.',
      before_photos: beforePhotos,
      after_photos: afterPhotos,
      submitted_by: submittedBy || req.user.full_name || 'Field Officer'
    };

    let progressNotes = [];
    try {
      progressNotes = task.progress_notes ? JSON.parse(task.progress_notes) : [];
    } catch (e) {}

    const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
    progressNotes.push({
      timestamp: now,
      author: submittedBy || req.user.full_name || 'Field Officer',
      note: `Completion dossier submitted: ${completionNotes}`,
      percentage: 100
    });

    await db.runAsync(`
      UPDATE tasks 
      SET status = 'COMPLETED_PENDING_VERIFICATION', progress_percentage = 100, completion_submission = ?, progress_notes = ?
      WHERE id = ?
    `, [JSON.stringify(submission), JSON.stringify(progressNotes), id]);

    await notifyCitizen(
      task.report_id,
      'Repair work finished',
      `Report #${task.report_code}: the repair work is finished and is waiting for final verification.`
    );

    // Record audit log
    await db.runAsync(`
      INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
      VALUES (?, ?, 'FIELD_TECHNICIAN', ?, 'TASK_COMPLETION_SUBMITTED', ?, ?, ?)
    `, [
      uuidv4(),
      submittedBy || req.user.full_name,
      task.department_name,
      id,
      task.task_code,
      `Task completion submitted for verification`
    ]);

    const updated = await db.getAsync('SELECT * FROM tasks WHERE id = ?', id);
    res.json(formatTask(updated));
  } catch (error) {
    console.error('Submit completion error:', error);
    res.status(500).json({ error: 'Failed to submit task completion' });
  }
});

// Verify and resolve task (and linked report)
router.post('/:id/verify-resolve', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { officerName, resolutionNotes } = req.body;

    const task = await db.getAsync('SELECT * FROM tasks WHERE id = ?', id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    // Update task to RESOLVED
    await db.runAsync(`
      UPDATE tasks 
      SET status = 'RESOLVED', progress_percentage = 100, progress_notes = ?
      WHERE id = ?
    `, [
      appendNote(task, officerName || req.user.full_name || 'Officer',
        `Resolved and verified. ${resolutionNotes || 'All checks passed.'}`, 100),
      id
    ]);

    // Update linked report to resolved
    if (task.report_id) {
      await db.runAsync(`
        UPDATE reports 
        SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `, [task.report_id]);

      // Fetch report for citizen notification
      const report = await db.getAsync('SELECT user_id, report_code FROM reports WHERE id = ?', task.report_id);
      if (report) {
        await db.runAsync(`
          INSERT INTO notifications (id, user_id, title, message, type, reference_id)
          VALUES (?, ?, 'Report Resolved!', ?, 'status_update', ?)
        `, [
          uuidv4(),
          report.user_id,
          `Great news! Report #${report.report_code || task.report_code} has been fully resolved and verified.`,
          task.report_id
        ]);
      }
    }

    // Record audit log
    await db.runAsync(`
      INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
      VALUES (?, ?, 'DEPARTMENT_ADMIN', ?, 'TASK_VERIFIED_RESOLVED', ?, ?, ?)
    `, [
      uuidv4(),
      officerName || req.user.full_name,
      task.department_name,
      id,
      task.task_code,
      `Task verified and marked resolved: ${resolutionNotes || 'All checks passed.'}`
    ]);

    console.log(`✅ Task ${task.task_code} and linked report ${task.report_id} verified and resolved.`);
    res.json(true);
  } catch (error) {
    console.error('Verify resolve error:', error);
    res.status(500).json({ error: 'Failed to verify and resolve task' });
  }
});

// Return / reject task
router.post('/:id/return-reject', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { officerName, reason, requiredCorrection, newExpectedDate } = req.body;

    const task = await db.getAsync('SELECT * FROM tasks WHERE id = ?', id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    let rejectionHistory = [];
    try {
      rejectionHistory = task.rejection_history ? JSON.parse(task.rejection_history) : [];
    } catch (e) {}

    const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
    rejectionHistory.push({
      timestamp: now,
      rejected_by: officerName || req.user.full_name,
      reason,
      required_correction: requiredCorrection,
      new_expected_date: newExpectedDate
    });

    await db.runAsync(`
      UPDATE tasks 
      SET status = 'RETURNED', deadline_date = ?, rejection_history = ?, progress_notes = ?,
          progress_percentage = MIN(progress_percentage, 90)
      WHERE id = ?
    `, [
      newExpectedDate || task.deadline_date,
      JSON.stringify(rejectionHistory),
      appendNote(task, officerName || req.user.full_name || 'Officer',
        `The finished work did not pass inspection and was sent back for correction.${newExpectedDate ? ` New expected date: ${newExpectedDate}.` : ''}`,
        Math.min(Number(task.progress_percentage) || 0, 90)),
      id
    ]);

    await notifyCitizen(
      task.report_id,
      'Work sent back for correction',
      `Report #${task.report_code}: the work did not pass inspection and is being corrected.`
    );

    // Record audit log
    await db.runAsync(`
      INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
      VALUES (?, ?, 'DEPARTMENT_ADMIN', ?, 'TASK_RETURNED_REJECTED', ?, ?, ?)
    `, [
      uuidv4(),
      officerName || req.user.full_name,
      task.department_name,
      id,
      task.task_code,
      `Task returned: ${reason}. Required correction: ${requiredCorrection}`
    ]);

    res.json(true);
  } catch (error) {
    console.error('Return reject error:', error);
    res.status(500).json({ error: 'Failed to return task' });
  }
});

module.exports = router;
