const emailService = require('./email.service');
const smsService = require('./sms.service');

/**
 * Tell the assignee of a task about it by email and/or SMS.
 * Never throws: each channel reports 'sent', 'failed' (with detail) or 'skipped'.
 */
async function notifyAssignee({ worker, task, report, notifyEmail = true, notifySms = true }) {
  const result = {
    email: { status: 'skipped', detail: 'Not requested' },
    sms: { status: 'skipped', detail: 'Not requested' },
  };
  if (!worker) {
    const detail = 'No assignee record found';
    return { email: { status: 'skipped', detail }, sms: { status: 'skipped', detail } };
  }

  const hasCoords = report.latitude != null && report.longitude != null;
  const location = report.address || report.location || (hasCoords ? `${report.latitude}, ${report.longitude}` : '');
  const mapUrl = hasCoords ? `https://www.google.com/maps?q=${report.latitude},${report.longitude}` : '';

  if (notifyEmail) {
    if (!worker.email) {
      result.email = { status: 'skipped', detail: 'Assignee has no email address' };
    } else {
      try {
        await emailService.sendTaskAssignmentEmail(worker.email, {
          assigneeName: worker.name,
          taskCode: task.taskCode,
          reportCode: task.reportCode,
          title: report.title,
          category: report.category_name,
          location,
          mapUrl,
          priority: task.priority,
          deadline: task.deadline,
          instructions: task.instructions,
          departmentName: report.department_name,
        });
        result.email = { status: 'sent', detail: worker.email };
      } catch (error) {
        console.error('❌ Assignment email failed:', error.message);
        result.email = { status: 'failed', detail: error.message };
      }
    }
  }

  if (notifySms) {
    if (!smsService.isEnabled()) {
      result.sms = { status: 'skipped', detail: 'SMS is not configured on the server' };
    } else if (!worker.phone_number) {
      result.sms = { status: 'skipped', detail: 'Assignee has no phone number' };
    } else {
      try {
        const text = `CIRP: new work order ${task.taskCode} (${task.priority}). `
          + `${report.title}${location ? ` at ${location}` : ''}. Deadline ${task.deadline}.`;
        await smsService.send(worker.phone_number, text.slice(0, 300));
        result.sms = { status: 'sent', detail: worker.phone_number };
      } catch (error) {
        console.error('❌ Assignment SMS failed:', error.message);
        result.sms = { status: 'failed', detail: error.message };
      }
    }
  }

  return result;
}

module.exports = { notifyAssignee };
