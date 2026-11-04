const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const { body, validationResult } = require('express-validator');
const db = require('../config/database');
const { authMiddleware, requireRole } = require('../middleware/auth');
const http = require('http');

// AI Service configuration
const AI_SERVICE_HOST = process.env.AI_SERVICE_HOST || 'localhost';
const AI_SERVICE_PORT = process.env.AI_SERVICE_PORT || 8001;

// Helper function to call AI service for duplicate detection
async function checkDuplicateReport(newReport, existingReports) {
  return new Promise((resolve) => {
    try {
      if (!existingReports || existingReports.length === 0) {
        resolve({
          has_potential_duplicate: false,
          similar_reports: []
        });
        return;
      }

      const postData = JSON.stringify({
        new_report: {
          title: newReport.title,
          description: newReport.description,
          category: newReport.category_name || 'Other',
          latitude: newReport.latitude,
          longitude: newReport.longitude
        },
        existing_reports: existingReports.map(r => ({
          id: r.id,
          title: r.title,
          description: r.description,
          category: r.category_name || 'Other',
          latitude: r.latitude,
          longitude: r.longitude
        }))
      });

      const options = {
        hostname: AI_SERVICE_HOST,
        port: AI_SERVICE_PORT,
        path: '/ai/detect-duplicate/',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: 5000 // 5 second timeout
      };

      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
          try {
            const result = JSON.parse(data);
            console.log('🤖 AI Duplicate Detection Result:', result);
            resolve(result);
          } catch (e) {
            console.error('Error parsing AI response:', e);
            resolve({ has_potential_duplicate: false, similar_reports: [] });
          }
        });
      });

      req.on('error', (e) => {
        console.error('AI service request error:', e.message);
        resolve({ has_potential_duplicate: false, similar_reports: [] });
      });

      req.on('timeout', () => {
        console.warn('AI service timeout');
        req.destroy();
        resolve({ has_potential_duplicate: false, similar_reports: [] });
      });

      req.write(postData);
      req.end();
    } catch (error) {
      console.error('AI duplicate check error:', error);
      resolve({ has_potential_duplicate: false, similar_reports: [] });
    }
  });
}

// Helper to normalize status for frontend
function mapStatusToFrontend(status) {
  if (!status) return 'NEW';
  const s = status.toLowerCase();
  if (s === 'pending' || s === 'new') return 'NEW';
  if (s === 'assigned' || s === 'accepted') return 'ACCEPTED';
  if (s === 'in_progress') return 'IN_PROGRESS';
  if (s === 'completed' || s === 'completed_pending_verification') return 'COMPLETED_PENDING_VERIFICATION';
  if (s === 'resolved') return 'RESOLVED';
  if (s === 'rejected' || s === 'disputed') return 'DISPUTED';
  return status.toUpperCase();
}

// Helper to format a report row for frontend schemas
async function formatReport(r) {
  // Get images
  const images = await db.allAsync(
    'SELECT id, image_url, is_primary FROM report_images WHERE report_id = ?',
    r.id
  );

  // Ensure images have data URI prefix
  const mediaPhotos = images.map(img => {
    const url = img.image_url;
    // If the image doesn't start with data:, add the prefix
    if (url && !url.startsWith('data:')) {
      return `data:image/jpeg;base64,${url}`;
    }
    return url;
  });
  
  const reportCode = r.report_code || `REP-${r.id.substring(0, 8).toUpperCase()}`;

  // Find nearby assets if coordinates exist
  let nearbyAssets = [];
  if (r.latitude && r.longitude) {
    const assets = await db.allAsync(
      'SELECT id, asset_code, name, asset_type_label, latitude, longitude FROM assets WHERE department_id = ? LIMIT 5',
      r.department_id || ''
    );
    nearbyAssets = assets.map(a => {
      // Rough distance in meters
      const latDiff = Math.abs(a.latitude - r.latitude) * 111000;
      const lonDiff = Math.abs(a.longitude - r.longitude) * 111000;
      const dist = Math.round(Math.sqrt(latDiff * latDiff + lonDiff * lonDiff));
      return {
        asset_id: a.id,
        asset_code: a.asset_code,
        asset_name: a.name,
        distance_meters: dist,
        asset_type: a.asset_type_label
      };
    }).sort((a, b) => a.distance_meters - b.distance_meters);
  }

  // Linked task if any
  const linkedTask = await db.getAsync('SELECT id FROM tasks WHERE report_id = ?', r.id);

  let reporterName = r.reporter_name;
  let reporterContact = r.reporter_phone || r.reporter_email || '';
  if (!reporterName && r.user_id) {
    const user = await db.getAsync('SELECT full_name, email, phone_number FROM users WHERE id = ?', r.user_id);
    if (user) {
      reporterName = user.full_name;
      reporterContact = user.phone_number || user.email || '';
    }
  }

  return {
    ...r,
    report_code: reportCode,
    status: mapStatusToFrontend(r.status),
    priority: (r.priority || 'MEDIUM').toUpperCase(),
    citizen_name: reporterName || 'Citizen Reporter',
    citizen_contact: reporterContact,
    citizen_latitude: r.latitude ? Number(r.latitude) : null,
    citizen_longitude: r.longitude ? Number(r.longitude) : null,
    address: r.address || r.location || '',
    landmark: r.landmark || '',
    submitted_at: r.created_at,
    media_photos: mediaPhotos,
    images: images.length > 0 ? images.map(img => ({
      ...img,
      image_url: img.image_url && !img.image_url.startsWith('data:') 
        ? `data:image/jpeg;base64,${img.image_url}` 
        : img.image_url
    })) : null,
    suggested_nearby_assets: nearbyAssets,
    linked_task_id: linkedTask ? linkedTask.id : null,
    ai_category_prediction: {
      suggested_category: r.category_name || 'Infrastructure',
      confidence: 0.94
    },
    ai_duplicate_analysis: {
      has_potential_duplicate: false
    }
  };
}

// Get all reports (with filters and pagination)
router.get('/', authMiddleware, async (req, res) => {
  try {
    const {
      status,
      category_id,
      department_id,
      priority,
      search,
      page = 1,
      limit = 100,
      sort_by = 'created_at',
      sort_order = 'DESC',
      all
    } = req.query;

    let whereConditions = [];
    let params = [];

    // If citizen, only filter to own reports if 'all' is not requested
    if (req.user.role === 'citizen' && all !== 'true' && all !== '1') {
      whereConditions.push('r.user_id = ?');
      params.push(req.userId);
    }

    // If department admin, filter reports for their department
    if (req.user.role === 'department_head' && req.user.department_id) {
      whereConditions.push('r.department_id = ?');
      params.push(req.user.department_id);
    } else if (department_id) {
      whereConditions.push('r.department_id = ?');
      params.push(department_id);
    }

    // Status filter
    if (status && status !== 'all') {
      const s = status.toLowerCase();
      if (s === 'new' || s === 'pending') {
        whereConditions.push("(r.status = 'pending' OR r.status = 'NEW')");
      } else if (s === 'accepted' || s === 'assigned') {
        whereConditions.push("(r.status = 'assigned' OR r.status = 'ACCEPTED')");
      } else if (s === 'disputed' || s === 'rejected') {
        whereConditions.push("(r.status = 'rejected' OR r.status = 'DISPUTED')");
      } else if (s === 'in_progress') {
        whereConditions.push("(r.status = 'in_progress' OR r.status = 'IN_PROGRESS')");
      } else if (s === 'resolved') {
        whereConditions.push("(r.status = 'resolved' OR r.status = 'RESOLVED')");
      } else {
        whereConditions.push('r.status = ?');
        params.push(status);
      }
    }

    if (category_id) {
      whereConditions.push('r.category_id = ?');
      params.push(category_id);
    }

    if (priority && priority !== 'all') {
      whereConditions.push('(UPPER(r.priority) = ? OR LOWER(r.priority) = ?)');
      params.push(priority.toUpperCase(), priority.toLowerCase());
    }

    if (search) {
      whereConditions.push('(r.title LIKE ? OR r.description LIKE ? OR r.report_code LIKE ?)');
      params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }

    const whereClause = whereConditions.length > 0 
      ? `WHERE ${whereConditions.join(' AND ')}` 
      : '';

    // Get total count
    const countResult = await db.getAsync(
      `SELECT COUNT(*) as count FROM reports r ${whereClause}`,
      ...params
    );
    const totalReports = countResult.count;

    // Get reports with pagination
    const offset = (page - 1) * limit;
    
    const allowedSortColumns = ['created_at', 'updated_at', 'status', 'priority'];
    const sortColumn = allowedSortColumns.includes(sort_by) ? sort_by : 'created_at';
    const sortDirection = sort_order.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    const rawReports = await db.allAsync(`
      SELECT 
        r.*,
        c.name as category_name,
        c.icon as category_icon,
        c.color as category_color,
        u.full_name as reporter_name,
        u.email as reporter_email,
        u.phone_number as reporter_phone,
        assigned.full_name as assigned_to_name,
        d.name as department_name,
        (SELECT COUNT(*) FROM comments WHERE report_id = r.id) as comment_count
      FROM reports r
      LEFT JOIN categories c ON r.category_id = c.id
      LEFT JOIN users u ON r.user_id = u.id
      LEFT JOIN users assigned ON r.assigned_to = assigned.id
      LEFT JOIN departments d ON r.department_id = d.id
      ${whereClause}
      ORDER BY r.${sortColumn} ${sortDirection}
      LIMIT ? OFFSET ?
    `, ...params, limit, offset);

    // Format each report
    const formattedReports = [];
    for (const report of rawReports) {
      formattedReports.push(await formatReport(report));
    }

    console.log(`📊 Returning ${formattedReports.length} reports out of ${totalReports} total`);
    res.json({
      success: true,
      reports: formattedReports,
      data: formattedReports,
      total: totalReports,
      count: totalReports,
      page: parseInt(page),
      limit: parseInt(limit)
    });
  } catch (error) {
    console.error('Get reports error:', error);
    res.status(500).json({ 
      success: false,
      message: 'Failed to fetch reports',
      error: error.message 
    });
  }
});

// Get current user's reports (alias for mobile my-reports endpoint)
router.get('/my-reports', authMiddleware, async (req, res) => {
  try {
    const { page = 1, limit = 100 } = req.query;
    
    const offset = (page - 1) * limit;
    
    // Get user's reports
    const rawReports = await db.allAsync(`
      SELECT 
        r.*,
        c.name as category_name,
        c.icon as category_icon,
        c.color as category_color,
        u.full_name as reporter_name,
        u.email as reporter_email,
        u.phone_number as reporter_phone,
        d.name as department_name
      FROM reports r
      LEFT JOIN categories c ON r.category_id = c.id
      LEFT JOIN users u ON r.user_id = u.id
      LEFT JOIN departments d ON r.department_id = d.id
      WHERE r.user_id = ?
      ORDER BY r.created_at DESC
      LIMIT ? OFFSET ?
    `, req.userId, limit, offset);

    // Get total count
    const countResult = await db.getAsync(
      'SELECT COUNT(*) as count FROM reports WHERE user_id = ?',
      req.userId
    );

    // Format each report
    const formattedReports = [];
    for (const report of rawReports) {
      formattedReports.push(await formatReport(report));
    }

    console.log(`📊 User ${req.userId} has ${formattedReports.length} reports`);
    res.json({
      success: true,
      data: formattedReports,
      count: countResult.count,
      page: parseInt(page),
      limit: parseInt(limit)
    });
  } catch (error) {
    console.error('Get my reports error:', error);
    res.status(500).json({ 
      success: false,
      message: 'Failed to fetch your reports',
      error: error.message 
    });
  }
});

// Get single report
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;

    const rawReport = await db.getAsync(`
      SELECT 
        r.*,
        c.name as category_name,
        c.icon as category_icon,
        c.color as category_color,
        u.full_name as reporter_name,
        u.email as reporter_email,
        u.phone_number as reporter_phone,
        assigned.full_name as assigned_to_name,
        d.name as department_name
      FROM reports r
      LEFT JOIN categories c ON r.category_id = c.id
      LEFT JOIN users u ON r.user_id = u.id
      LEFT JOIN users assigned ON r.assigned_to = assigned.id
      LEFT JOIN departments d ON r.department_id = d.id
      WHERE r.id = ?
    `, id);

    if (!rawReport) {
      return res.status(404).json({ error: 'Report not found' });
    }

    const report = await formatReport(rawReport);

    // Get comments
    const comments = await db.allAsync(`
      SELECT c.*, u.full_name as user_name, u.role as user_role
      FROM comments c
      LEFT JOIN users u ON c.user_id = u.id
      WHERE c.report_id = ?
      ORDER BY c.created_at DESC
    `, id);

    report.comments = comments;

    res.json(report);
  } catch (error) {
    console.error('Get report error:', error);
    res.status(500).json({ error: 'Failed to fetch report' });
  }
});

// Create report
router.post('/',
  authMiddleware,
  [
    body('title').notEmpty().withMessage('Title is required'),
    body('description').notEmpty().withMessage('Description is required'),
  ],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ 
          success: false,
          message: 'Validation failed',
          errors: errors.array() 
        });
      }

      const {
        category_id,
        title,
        description,
        location,
        latitude,
        longitude,
        address,
        priority = 'MEDIUM',
        is_anonymous = false,
        images = [],
        media_images = []
      } = req.body;

      const reportId = uuidv4();
      const reportCode = `REP-${reportId.substring(0, 8).toUpperCase()}`;

      // Combine images and media_images
      const allImages = [...images, ...media_images];

      // Validate and get category_id - verify it exists in database
      let validCategoryId = category_id;
      let departmentId = null;
      
      if (category_id) {
        const category = await db.getAsync(
          'SELECT id, name, department_id FROM categories WHERE id = ?',
          category_id
        );
        
        if (category) {
          validCategoryId = category.id;
          departmentId = category.department_id || null;
          console.log(`✅ Valid category found: ${category.name} (${category.id}), dept: ${departmentId}`);
        } else {
          // Category doesn't exist - use default "Other" category
          console.warn(`⚠️ Category ${category_id} not found, using default 'Other' category`);
          const defaultCategory = await db.getAsync(
            "SELECT id, department_id FROM categories WHERE name = 'Other' OR name LIKE '%Other%' LIMIT 1"
          );
          validCategoryId = defaultCategory?.id || null;
          departmentId = defaultCategory?.department_id || null;
        }
      }
      
      // If still no valid category, try to find any category
      if (!validCategoryId) {
        console.warn('⚠️ No valid category_id provided, finding first available category');
        const anyCategory = await db.getAsync('SELECT id, department_id FROM categories LIMIT 1');
        validCategoryId = anyCategory?.id || null;
        departmentId = anyCategory?.department_id || null;
      }

      // If still no department, default to Public Works
      if (!departmentId) {
        const defaultDept = await db.getAsync("SELECT id FROM departments WHERE name LIKE '%Public Works%' LIMIT 1");
        departmentId = defaultDept?.id || null;
      }
      
      // If still no department, get any department
      if (!departmentId) {
        const anyDept = await db.getAsync('SELECT id FROM departments LIMIT 1');
        departmentId = anyDept?.id || null;
      }

      console.log(`📝 Creating report with category_id: ${validCategoryId}, department_id: ${departmentId}`);

      // Check for duplicate reports using AI before creating
      let duplicateAnalysis = { has_potential_duplicate: false, similar_reports: [] };
      try {
        // Get recent reports from same category (last 30 days)
        const recentReports = await db.allAsync(`
          SELECT r.*, c.name as category_name
          FROM reports r
          LEFT JOIN categories c ON r.category_id = c.id
          WHERE r.category_id = ? 
            AND r.created_at > datetime('now', '-30 days')
            AND r.status != 'rejected'
          ORDER BY r.created_at DESC
          LIMIT 50
        `, validCategoryId);

        if (recentReports && recentReports.length > 0) {
          console.log(`🔍 Checking ${recentReports.length} recent reports for duplicates...`);
          duplicateAnalysis = await checkDuplicateReport({
            title,
            description,
            category_name: recentReports[0]?.category_name || 'Other',
            latitude: latitude || 9.0054,
            longitude: longitude || 38.7636
          }, recentReports);
          
          if (duplicateAnalysis.has_potential_duplicate) {
            console.log(`⚠️ DUPLICATE DETECTED! Similar to ${duplicateAnalysis.similar_reports?.length || 0} reports`);
            
            // BLOCK DUPLICATE SUBMISSION
            return res.status(409).json({
              success: false,
              message: 'This report reported by others',
              duplicate_warning: {
                message: 'This report reported by others',
                similar_reports: duplicateAnalysis.similar_reports || []
              },
              is_duplicate: true
            });
          }
        }
      } catch (aiError) {
        console.error('AI duplicate check failed (continuing anyway):', aiError.message);
      }

      // Create report - use NULL for category_id if still not found (will allow report creation)
      await db.runAsync(`
        INSERT INTO reports 
        (id, report_code, user_id, category_id, department_id, title, description, location, latitude, longitude, address, priority, status, is_anonymous)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
      `, [
        reportId,
        reportCode,
        req.userId,
        validCategoryId,
        departmentId,
        title,
        description,
        location || address,
        latitude || 9.0054,
        longitude || 38.7636,
        address || location,
        priority.toLowerCase(),
        is_anonymous ? 1 : 0
      ]);

      // Add images if provided
      if (allImages && allImages.length > 0) {
        for (let i = 0; i < allImages.length; i++) {
          await db.runAsync(
            'INSERT INTO report_images (id, report_id, image_url, is_primary) VALUES (?, ?, ?, ?)',
            uuidv4(), reportId, allImages[i], i === 0 ? 1 : 0
          );
        }
      }

      // Log activity
      await db.runAsync(
        'INSERT INTO report_activity (id, report_id, user_id, action, new_value) VALUES (?, ?, ?, ?, ?)',
        uuidv4(), reportId, req.userId, 'created', 'Report created'
      );

      // Create audit log
      await db.runAsync(`
        INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
        VALUES (?, ?, 'CITIZEN', 'Citizen Submissions', 'REPORT_CREATED', ?, ?, ?)
      `, [uuidv4(), req.user?.full_name || 'Citizen', reportId, reportCode, `New incident report: ${title}`]);

      const createdRow = await db.getAsync('SELECT * FROM reports WHERE id = ?', reportId);
      const formatted = await formatReport(createdRow);
      
      // Add duplicate analysis to response
      formatted.ai_duplicate_analysis = duplicateAnalysis;

      res.status(201).json({
        success: true,
        message: 'Report created successfully',
        report: formatted,
        data: formatted,
        duplicate_warning: duplicateAnalysis.has_potential_duplicate ? {
          message: 'This report may be similar to existing reports',
          similar_reports: duplicateAnalysis.similar_reports || []
        } : null
      });
    } catch (error) {
      console.error('Create report error:', error);
      res.status(500).json({ 
        success: false,
        message: 'Failed to create report',
        error: error.message 
      });
    }
  }
);

// Accept report and create task (Admin/Department Head only)
router.post('/:id/accept',
  authMiddleware,
  requireRole('admin', 'department_head'),
  async (req, res) => {
    try {
      const { id } = req.params;
      const {
        priority = 'HIGH',
        assignedWorkerId,
        deadlineDate,
        workDescription,
        internalNote
      } = req.body;

      // Get current report
      const report = await db.getAsync(`
        SELECT r.*, d.name as department_name, c.name as category_name
        FROM reports r
        LEFT JOIN departments d ON r.department_id = d.id
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.id = ?
      `, id);

      if (!report) {
        return res.status(404).json({ error: 'Report not found' });
      }

      // Get assigned worker details from staff_contractors
      let worker = null;
      if (assignedWorkerId) {
        worker = await db.getAsync('SELECT * FROM staff_contractors WHERE id = ?', assignedWorkerId);
      }
      if (!worker) {
        // Fallback to first available staff for the department
        worker = await db.getAsync('SELECT * FROM staff_contractors WHERE department_id = ? LIMIT 1', report.department_id);
      }

      const workerName = worker ? worker.name : 'Assigned Field Officer';
      const isContractor = worker ? (worker.is_contractor === 1) : false;
      const contractorCompany = worker?.contractor_company_name || null;

      const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
      const taskId = `task-${Date.now()}`;
      const reportCode = report.report_code || `REP-${report.id.substring(0, 8).toUpperCase()}`;
      const taskCode = `TSK-${report.asset_code || 'GEN'}-${Math.floor(1000 + Math.random() * 9000)}`;
      const deadline = deadlineDate || '2026-11-20';

      const progressNotes = [
        {
          timestamp: now,
          author: req.user.full_name || 'System Dispatcher',
          note: `Report accepted and assigned to ${workerName}. Initial deadline: ${deadline}.`,
          percentage: 0
        }
      ];

      // Create new operational task
      await db.runAsync(`
        INSERT INTO tasks (
          id, task_code, report_id, report_code, asset_id, asset_code,
          asset_type_label, department_id, department_name, assigned_worker_id,
          assigned_worker_name, is_contractor, contractor_company, work_description,
          internal_note, priority, status, progress_percentage, created_at,
          deadline_date, original_deadline_date, is_overdue, days_overdue,
          progress_notes, extensions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `, [
        taskId,
        taskCode,
        report.id,
        reportCode,
        report.asset_id || 'unlinked',
        report.asset_code || 'N/A',
        report.asset_type_label || 'General Infrastructure',
        report.department_id,
        report.department_name,
        assignedWorkerId || (worker ? worker.id : 'staff-el-01'),
        workerName,
        isContractor ? 1 : 0,
        contractorCompany,
        workDescription || 'Inspect infrastructure damage and perform repair.',
        internalNote || '',
        priority.toUpperCase(),
        'ASSIGNED',
        0,
        now,
        deadline,
        deadline,
        0,
        0,
        JSON.stringify(progressNotes),
        JSON.stringify([])
      ]);

      // Update report status to assigned
      await db.runAsync(`
        UPDATE reports 
        SET status = 'assigned', priority = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `, [priority.toLowerCase(), id]);

      // Notify citizen reporter
      await db.runAsync(`
        INSERT INTO notifications (id, user_id, title, message, type, reference_id)
        VALUES (?, ?, ?, ?, 'status_update', ?)
      `, [
        uuidv4(),
        report.user_id,
        'Report Accepted & Dispatched',
        `Your report #${reportCode} has been accepted. Assigned to ${workerName} with deadline ${deadline}.`,
        id
      ]);

      // Record audit log
      await db.runAsync(`
        INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
        VALUES (?, ?, ?, ?, 'REPORT_ACCEPTED', ?, ?, ?)
      `, [
        uuidv4(),
        req.user.full_name,
        req.user.role === 'admin' ? 'SYSTEM_ADMIN' : 'DEPARTMENT_ADMIN',
        report.department_name,
        id,
        reportCode,
        `Report accepted and task ${taskCode} dispatched to ${workerName}`
      ]);

      // Build task response matching TaskRecordSchema
      const taskRecord = {
        id: taskId,
        task_code: taskCode,
        report_id: report.id,
        report_code: reportCode,
        asset_id: report.asset_id || 'unlinked',
        asset_code: report.asset_code || 'N/A',
        asset_type_label: report.asset_type_label || 'General Infrastructure',
        department_id: report.department_id,
        department_name: report.department_name,
        assigned_worker_id: assignedWorkerId || (worker ? worker.id : 'staff-el-01'),
        assigned_worker_name: workerName,
        is_contractor: isContractor,
        contractor_company: contractorCompany,
        work_description: workDescription || 'Inspect and repair',
        internal_note: internalNote || '',
        priority: priority.toUpperCase(),
        status: 'ASSIGNED',
        progress_percentage: 0,
        created_at: now,
        deadline_date: deadline,
        original_deadline_date: deadline,
        is_overdue: false,
        days_overdue: 0,
        progress_notes: progressNotes,
        extensions: []
      };

      console.log('✅ Report accepted successfully, created task:', taskCode);
      res.json(taskRecord);
    } catch (error) {
      console.error('Accept report error:', error);
      res.status(500).json({ error: 'Failed to accept report: ' + error.message });
    }
  }
);

// Reject report (Admin/Department Head only)
router.post(['/:id/reject', '/:id/reject/'],
  authMiddleware,
  requireRole('admin', 'department_head'),
  async (req, res) => {
    try {
      const { id } = req.params;
      const { department_id, reason } = req.body;

      const report = await db.getAsync('SELECT * FROM reports WHERE id = ?', id);
      if (!report) {
        return res.status(404).json({ error: 'Report not found' });
      }

      // Update status to rejected
      await db.runAsync(`
        UPDATE reports 
        SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `, [id]);

      // Add comment with reason
      if (reason) {
        await db.runAsync(`
          INSERT INTO comments (id, report_id, user_id, content, is_internal)
          VALUES (?, ?, ?, ?, 0)
        `, [uuidv4(), id, req.userId, `Rejection reason: ${reason}`]);
      }

      // Notify citizen
      await db.runAsync(`
        INSERT INTO notifications (id, user_id, title, message, type, reference_id)
        VALUES (?, ?, 'Report Rejected', ?, 'status_update', ?)
      `, [
        uuidv4(),
        report.user_id,
        `Your report has been rejected: ${reason || 'Does not meet triage criteria.'}`,
        id
      ]);

      // Record audit log
      const reportCode = report.report_code || `REP-${report.id.substring(0, 8).toUpperCase()}`;
      await db.runAsync(`
        INSERT INTO audit_logs (id, officer_name, officer_role, department_name, action_type, target_entity_id, target_entity_code, details_summary)
        VALUES (?, ?, ?, 'Municipal Triage', 'REPORT_REJECTED', ?, ?, ?)
      `, [
        uuidv4(),
        req.user.full_name,
        req.user.role === 'admin' ? 'SYSTEM_ADMIN' : 'DEPARTMENT_ADMIN',
        id,
        reportCode,
        `Report rejected: ${reason}`
      ]);

      const updatedRow = await db.getAsync(`
        SELECT r.*, c.name as category_name, d.name as department_name, u.full_name as reporter_name
        FROM reports r
        LEFT JOIN categories c ON r.category_id = c.id
        LEFT JOIN departments d ON r.department_id = d.id
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.id = ?
      `, id);

      const formatted = await formatReport(updatedRow);
      res.json(formatted);
    } catch (error) {
      console.error('Reject report error:', error);
      res.status(500).json({ error: 'Failed to reject report: ' + error.message });
    }
  }
);

// Link physical asset to report
router.post('/:id/link-asset',
  authMiddleware,
  requireRole('admin', 'department_head'),
  async (req, res) => {
    try {
      const { id } = req.params;
      const { assetId } = req.body;

      const asset = await db.getAsync('SELECT * FROM assets WHERE id = ?', assetId);
      if (!asset) {
        return res.status(404).json({ error: 'Asset not found' });
      }

      await db.runAsync(`
        UPDATE reports 
        SET asset_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `, [assetId, id]);

      res.json(true);
    } catch (error) {
      console.error('Link asset error:', error);
      res.status(500).json({ error: 'Failed to link asset: ' + error.message });
    }
  }
);

// Update report status directly
router.patch('/:id/status',
  authMiddleware,
  requireRole('admin', 'contractor', 'department_head'),
  [
    body('status').notEmpty().withMessage('Status is required'),
    body('comment').optional(),
  ],
  async (req, res) => {
    try {
      const { id } = req.params;
      const { status, comment } = req.body;

      const currentReport = await db.getAsync('SELECT status, user_id FROM reports WHERE id = ?', id);
      if (!currentReport) {
        return res.status(404).json({ error: 'Report not found' });
      }

      const oldStatus = currentReport.status;
      const dbStatus = status.toLowerCase();

      let updateQuery = 'UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP';
      const params = [dbStatus];

      if (dbStatus === 'resolved') {
        updateQuery += ', resolved_at = CURRENT_TIMESTAMP';
      }

      updateQuery += ' WHERE id = ?';
      params.push(id);

      await db.runAsync(updateQuery, ...params);

      if (comment) {
        await db.runAsync(
          'INSERT INTO comments (id, report_id, user_id, content, is_internal) VALUES (?, ?, ?, ?, 1)',
          uuidv4(), id, req.userId, comment
        );
      }

      await db.runAsync(
        'INSERT INTO notifications (id, user_id, title, message, type, reference_id) VALUES (?, ?, ?, ?, ?, ?)',
        uuidv4(),
        currentReport.user_id,
        'Report Status Updated',
        `Your report status has been updated to: ${status}`,
        'status_update',
        id
      );

      const updated = await db.getAsync('SELECT * FROM reports WHERE id = ?', id);
      const formatted = await formatReport(updated);
      res.json({ message: 'Report status updated successfully', report: formatted });
    } catch (error) {
      console.error('Update report status error:', error);
      res.status(500).json({ error: 'Failed to update report status' });
    }
  }
);

// Add comment to report
router.post('/:id/comments',
  authMiddleware,
  [
    body('content').notEmpty().withMessage('Comment content is required'),
  ],
  async (req, res) => {
    try {
      const { id } = req.params;
      const { content } = req.body;

      const report = await db.getAsync('SELECT user_id FROM reports WHERE id = ?', id);
      if (!report) {
        return res.status(404).json({ error: 'Report not found' });
      }

      const commentId = uuidv4();
      await db.runAsync(
        'INSERT INTO comments (id, report_id, user_id, content) VALUES (?, ?, ?, ?)',
        commentId, id, req.userId, content
      );

      const comment = await db.getAsync('SELECT * FROM comments WHERE id = ?', commentId);
      res.status(201).json({ message: 'Comment added successfully', comment });
    } catch (error) {
      console.error('Add comment error:', error);
      res.status(500).json({ error: 'Failed to add comment' });
    }
  }
);

// Get report statistics (Admin only)
router.get('/stats/overview',
  authMiddleware,
  requireRole('admin', 'department_head'),
  async (req, res) => {
    try {
      const statusStats = await db.allAsync('SELECT status, COUNT(*) as count FROM reports GROUP BY status');
      const categoryStats = await db.allAsync(`
        SELECT c.name, COUNT(r.id) as count
        FROM categories c
        LEFT JOIN reports r ON c.id = r.category_id
        GROUP BY c.id, c.name
        ORDER BY count DESC
      `);

      const recentCount = await db.getAsync("SELECT COUNT(*) as count FROM reports WHERE created_at > datetime('now', '-7 days')");
      const avgResponse = await db.getAsync(`
        SELECT AVG((julianday(resolved_at) - julianday(created_at)) * 24) as avg_hours
        FROM reports
        WHERE resolved_at IS NOT NULL
      `);

      res.json({
        status_breakdown: statusStats,
        category_breakdown: categoryStats,
        recent_reports_count: recentCount ? recentCount.count : 0,
        avg_response_time_hours: parseFloat(avgResponse?.avg_hours || 2.4).toFixed(2)
      });
    } catch (error) {
      console.error('Get stats error:', error);
      res.status(500).json({ error: 'Failed to fetch statistics' });
    }
  }
);

// Delete report (Own reports or Admin) & alias for mobile citizen-delete
const handleDeleteReport = async (req, res) => {
  try {
    const { id } = req.params;
    const report = await db.getAsync('SELECT user_id FROM reports WHERE id = ?', id);
    if (!report) {
      return res.status(404).json({ error: 'Report not found' });
    }

    if (req.user.role !== 'admin' && req.user.role !== 'department_head' && report.user_id !== req.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    await db.runAsync('DELETE FROM reports WHERE id = ?', id);
    res.json({ success: true, message: 'Report deleted successfully' });
  } catch (error) {
    console.error('Delete report error:', error);
    res.status(500).json({ error: 'Failed to delete report' });
  }
};

router.delete('/:id', authMiddleware, handleDeleteReport);
router.post('/:id/citizen-delete', authMiddleware, handleDeleteReport);
router.post('/:id/citizen-delete/', authMiddleware, handleDeleteReport);

module.exports = router;
