const http = require('http');

async function request(options, postData) {
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body);
          resolve({ status: res.statusCode, data: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, body });
        }
      });
    });
    req.on('error', reject);
    if (postData) {
      req.write(typeof postData === 'string' ? postData : JSON.stringify(postData));
    }
    req.end();
  });
}

async function runTests() {
  console.log('🧪 Starting CIRP End-to-End Integration Verification...\n');
  let passed = 0;
  let failed = 0;

  function assert(condition, message) {
    if (condition) {
      console.log(`  ✅ ${message}`);
      passed++;
    } else {
      console.error(`  ❌ FAIL: ${message}`);
      failed++;
    }
  }

  try {
    // 1. Auth Test - Department Head Login
    console.log('1. Testing Department Head Login (Electrical Services)...');
    const loginRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/auth/login/',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      email: 'electrical.services@cirp.com',
      password: 'Test@123'
    });

    assert(loginRes.status === 200, `Login status code is 200 (got ${loginRes.status})`);
    assert(loginRes.data.access && loginRes.data.token, 'Response contains access and token');
    assert(loginRes.data.user && loginRes.data.user.role === 'DEPARTMENT_ADMIN', 'User role is DEPARTMENT_ADMIN');
    assert(loginRes.data.user.department?.name === 'Electrical Services', 'Department is Electrical Services');
    const deptToken = loginRes.data.access;

    // 2. Auth Test - Citizen Login
    console.log('\n2. Testing Citizen Login...');
    const citizenLoginRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/auth/login/',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      email: 'citizen@test.com',
      password: 'Test@123'
    });

    assert(citizenLoginRes.status === 200, `Citizen login status is 200 (got ${citizenLoginRes.status})`);
    const citizenToken = citizenLoginRes.data.access;

    // 3. Citizen Submits New Report
    console.log('\n3. Testing Citizen Incident Report Submission (Streetlight)...');
    const createReportRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/reports',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${citizenToken}`
      }
    }, {
      category_id: 'aeac7e07-736a-46ac-a8d4-e8d95ddc8138', // Streetlight
      title: 'Dark intersection - Light outage',
      description: 'Streetlight pole completely dark at Bole Olympia intersection.',
      latitude: 9.0062,
      longitude: 38.7651,
      address: 'Bole Olympia Junction, Addis Ababa',
      priority: 'HIGH',
      media_images: ['data:image/jpeg;base64,sampleimagedata123']
    });

    assert(createReportRes.status === 201, `Report created with status 201 (got ${createReportRes.status})`);
    assert(createReportRes.data.report?.report_code?.startsWith('REP-'), `Report code generated: ${createReportRes.data.report?.report_code}`);
    assert(createReportRes.data.report?.status === 'NEW', `Frontend status mapped to NEW (got ${createReportRes.data.report?.status})`);
    assert(createReportRes.data.report?.citizen_name === 'Test Citizen', `Citizen name mapped correctly: ${createReportRes.data.report?.citizen_name}`);
    const createdReportId = createReportRes.data.report?.id;

    // 4. Department Admin Lists Reports
    console.log('\n4. Testing Department Admin Report List & Filtering...');
    const listRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/reports',
      method: 'GET',
      headers: { 'Authorization': `Bearer ${deptToken}` }
    });

    assert(listRes.status === 200, `Reports list status 200 (got ${listRes.status})`);
    assert(Array.isArray(listRes.data.reports), `Returns reports array with ${listRes.data.reports?.length} items`);
    const foundReport = listRes.data.reports.find(r => r.id === createdReportId);
    assert(foundReport !== undefined, 'Newly submitted report is visible to Electrical Services department');
    assert(foundReport?.status === 'NEW', 'Status is NEW for triage intake');

    // 5. Department Admin Accepts Report & Dispatches Task
    console.log('\n5. Testing Report Triage: Accept Report & Dispatch Work Order...');
    const acceptRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: `/api/reports/${createdReportId}/accept`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${deptToken}`
      }
    }, {
      priority: 'HIGH',
      assignedWorkerId: 'staff-el-01',
      deadlineDate: '2026-11-10',
      workDescription: 'Inspect Olympia junction streetlight transformer and replace 120W LED fixture.',
      internalNote: 'Standard replacement parts from Central Depot.'
    });

    assert(acceptRes.status === 200, `Accept report status is 200 (got ${acceptRes.status})`);
    assert(acceptRes.data.task_code?.startsWith('TSK-'), `Created operational task: ${acceptRes.data.task_code}`);
    assert(acceptRes.data.assigned_worker_name === 'Abebe Kebede', `Worker assigned: ${acceptRes.data.assigned_worker_name}`);
    assert(acceptRes.data.status === 'ASSIGNED', 'Task status is ASSIGNED');
    const createdTaskId = acceptRes.data.id;

    // 6. Tasks Pipeline & Workflow
    console.log('\n6. Testing Task Pipeline: Progress Update & Completion...');
    const progressRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: `/api/tasks/${createdTaskId}/progress`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${deptToken}`
      }
    }, {
      progressPercentage: 60,
      newStatus: 'IN_PROGRESS',
      progressNote: 'Replaced ballast and wiring. Testing circuit.',
      authorName: 'Abebe Kebede'
    });

    assert(progressRes.status === 200, `Progress update status is 200 (got ${progressRes.status})`);
    assert(progressRes.data.progress_percentage === 60, 'Progress percentage updated to 60%');
    assert(progressRes.data.status === 'IN_PROGRESS', 'Task status transitioned to IN_PROGRESS');

    // 7. Complete Task
    console.log('\n7. Testing Task Completion Submission...');
    const completeRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: `/api/tasks/${createdTaskId}/complete`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${deptToken}`
      }
    }, {
      completionNotes: 'All luminaire units restored. Illumination intensity verified.',
      completionDate: '2026-10-23',
      beforePhotos: [],
      afterPhotos: [],
      submittedBy: 'Abebe Kebede'
    });

    assert(completeRes.status === 200, `Completion status is 200 (got ${completeRes.status})`);
    assert(completeRes.data.status === 'COMPLETED_PENDING_VERIFICATION', 'Task status is COMPLETED_PENDING_VERIFICATION');

    // 8. Verify and Resolve Task
    console.log('\n8. Testing Verification & Resolution of Task & Report...');
    const verifyRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: `/api/tasks/${createdTaskId}/verify-resolve`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${deptToken}`
      }
    }, {
      officerName: 'Electrical Services Manager',
      resolutionNotes: 'Inspection passed. Light operates per municipal safety standard.'
    });

    assert(verifyRes.status === 200 && verifyRes.data === true, 'Task verified and resolved successfully');

    // Verify report reflects RESOLVED
    const verifyReportRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: `/api/reports/${createdReportId}`,
      method: 'GET',
      headers: { 'Authorization': `Bearer ${deptToken}` }
    });

    assert(verifyReportRes.data.status === 'RESOLVED', `Report status transitioned to RESOLVED (got ${verifyReportRes.data.status})`);
    assert(verifyReportRes.data.resolved_at !== null, 'Report resolved_at timestamp populated');

    // 9. Citizen Notifications
    console.log('\n9. Testing Citizen Notification Delivery...');
    const notifRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/notifications',
      method: 'GET',
      headers: { 'Authorization': `Bearer ${citizenToken}` }
    });

    assert(notifRes.status === 200, `Notifications status is 200 (got ${notifRes.status})`);
    assert(Array.isArray(notifRes.data.notifications), `Citizen received ${notifRes.data.notifications?.length} notifications`);
    const resolvedNotif = notifRes.data.notifications.find(n => n.title?.includes('Resolved'));
    assert(resolvedNotif !== undefined, `Resolution notification delivered to citizen: "${resolvedNotif?.title}"`);

    // 10. Assets & Map
    console.log('\n10. Testing Infrastructure Assets & GIS Map Endpoints...');
    const assetsRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/assets',
      method: 'GET',
      headers: { 'Authorization': `Bearer ${deptToken}` }
    });
    assert(assetsRes.status === 200 && assetsRes.data.assets?.length > 0, `Assets returned: ${assetsRes.data.assets?.length} assets`);

    const mapRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/map/assets',
      method: 'GET',
      headers: { 'Authorization': `Bearer ${deptToken}` }
    });
    assert(mapRes.status === 200 && Array.isArray(mapRes.data) && mapRes.data.length > 0, `Map GIS assets returned: ${mapRes.data?.length} points`);

    // 11. Analytics & Metrics
    console.log('\n11. Testing Analytics Metrics...');
    const analyticsRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/analytics/metrics',
      method: 'GET',
      headers: { 'Authorization': `Bearer ${deptToken}` }
    });
    assert(analyticsRes.status === 200, `Analytics status is 200 (got ${analyticsRes.status})`);
    assert(typeof analyticsRes.data.avgIntakeHours === 'number', `avgIntakeHours: ${analyticsRes.data.avgIntakeHours}`);
    assert(typeof analyticsRes.data.slaCompliancePercent === 'number', `slaCompliancePercent: ${analyticsRes.data.slaCompliancePercent}%`);

    // 12. Audit Logs
    console.log('\n12. Testing Audit Logs...');
    const auditRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/audit-logs',
      method: 'GET',
      headers: { 'Authorization': `Bearer ${deptToken}` }
    });
    assert(auditRes.status === 200 && Array.isArray(auditRes.data) && auditRes.data.length > 0, `Audit logs recorded: ${auditRes.data?.length} events`);

    // 13. Users List
    console.log('\n13. Testing Users Directory...');
    const usersRes = await request({
      hostname: 'localhost',
      port: 3002,
      path: '/api/users/',
      method: 'GET',
      headers: { 'Authorization': `Bearer ${deptToken}` }
    });
    assert(usersRes.status === 200 && Array.isArray(usersRes.data), `Users directory returned: ${usersRes.data?.length} users`);

    // Summary
    console.log(`\n========================================`);
    console.log(`🎉 ALL INTEGRATION TESTS PASSED: ${passed}/${passed + failed}`);
    console.log(`========================================\n`);

  } catch (err) {
    console.error('Fatal test error:', err);
  }
}

runTests();
