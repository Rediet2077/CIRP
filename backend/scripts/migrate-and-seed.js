const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');

async function migrateAndSeed() {
  try {
    console.log('🔄 Running CIRP Database Migration & Seeding...');

    // 1. Ensure report_code column in reports table
    const reportColumns = await db.allAsync('PRAGMA table_info(reports)');
    const hasReportCode = reportColumns.some(col => col.name === 'report_code');
    if (!hasReportCode) {
      console.log('➕ Adding report_code column to reports table...');
      await db.runAsync('ALTER TABLE reports ADD COLUMN report_code TEXT');
    }

    // Populate report_code for existing reports if null
    const existingReports = await db.allAsync('SELECT id, report_code FROM reports');
    for (const report of existingReports) {
      if (!report.report_code) {
        const code = `REP-${report.id.substring(0, 8).toUpperCase()}`;
        await db.runAsync('UPDATE reports SET report_code = ? WHERE id = ?', [code, report.id]);
      }
    }

    // 2. Create tasks table
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        task_code TEXT UNIQUE NOT NULL,
        report_id TEXT NOT NULL,
        report_code TEXT,
        asset_id TEXT DEFAULT 'unlinked',
        asset_code TEXT DEFAULT 'N/A',
        asset_type_label TEXT DEFAULT 'General Infrastructure',
        department_id TEXT NOT NULL,
        department_name TEXT,
        assigned_worker_id TEXT NOT NULL,
        assigned_worker_name TEXT,
        is_contractor INTEGER DEFAULT 0,
        contractor_company TEXT,
        work_description TEXT NOT NULL,
        internal_note TEXT,
        priority TEXT DEFAULT 'HIGH',
        status TEXT DEFAULT 'ASSIGNED',
        progress_percentage INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        deadline_date TEXT,
        original_deadline_date TEXT,
        is_overdue INTEGER DEFAULT 0,
        days_overdue INTEGER DEFAULT 0,
        progress_notes TEXT,
        completion_submission TEXT,
        rejection_history TEXT,
        extensions TEXT,
        FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
        FOREIGN KEY (department_id) REFERENCES departments(id)
      );
    `);
    console.log('✅ Tasks table verified');

    // 3. Create assets table
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        asset_code TEXT UNIQUE NOT NULL,
        asset_type_id TEXT NOT NULL,
        asset_type_label TEXT NOT NULL,
        department_id TEXT NOT NULL,
        department_name TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'ACTIVE',
        condition TEXT DEFAULT 'GOOD',
        installation_date TEXT,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        address TEXT,
        landmark TEXT,
        registered_by TEXT,
        registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_inspection_date TEXT,
        active_reports_count INTEGER DEFAULT 0,
        specific_data TEXT,
        FOREIGN KEY (department_id) REFERENCES departments(id)
      );
    `);
    console.log('✅ Assets table verified');

    // 4. Create staff_contractors table
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS staff_contractors (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        email TEXT NOT NULL,
        department_id TEXT NOT NULL,
        department_name TEXT NOT NULL,
        role_type TEXT NOT NULL,
        position_title TEXT NOT NULL,
        specialization TEXT NOT NULL,
        is_contractor INTEGER DEFAULT 0,
        contractor_company_name TEXT,
        license_number TEXT,
        active_tasks_count INTEGER DEFAULT 0,
        completed_tasks_count INTEGER DEFAULT 0,
        overdue_tasks_count INTEGER DEFAULT 0,
        performance_score REAL DEFAULT 95.0,
        is_available INTEGER DEFAULT 1
      );
    `);
    console.log('✅ Staff & Contractors table verified');

    // 5. Create extensions table
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS extensions (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        task_code TEXT,
        report_code TEXT,
        asset_code TEXT,
        department_id TEXT,
        original_deadline TEXT,
        requested_new_deadline TEXT,
        reason_category TEXT,
        detailed_explanation TEXT,
        supporting_evidence_note TEXT,
        requested_by TEXT,
        requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'PENDING',
        decision_date TEXT,
        decided_by TEXT,
        decision_comment TEXT,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
      );
    `);
    console.log('✅ Extensions table verified');

    // 6. Ensure audit_logs has all needed columns without restrictive old constraints
    const auditInfo = await db.allAsync("SELECT sql FROM sqlite_master WHERE type='table' AND name='audit_logs'");
    if (auditInfo.length > 0 && auditInfo[0].sql.includes('action TEXT NOT NULL')) {
      await db.execAsync('DROP TABLE IF EXISTS audit_logs');
    }
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        officer_name TEXT,
        officer_role TEXT,
        department_name TEXT,
        action TEXT,
        action_type TEXT,
        target_entity_id TEXT,
        target_entity_code TEXT,
        details_summary TEXT,
        changes_payload TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Audit logs table verified');

    // Fetch existing departments for foreign keys
    const depts = await db.allAsync('SELECT id, name FROM departments');
    const elecDept = depts.find(d => d.name.toLowerCase().includes('electr')) || depts[0];
    const waterDept = depts.find(d => d.name.toLowerCase().includes('water')) || depts[1];
    const roadDept = depts.find(d => d.name.toLowerCase().includes('public') || d.name.toLowerCase().includes('road')) || depts[2];
    const sanitDept = depts.find(d => d.name.toLowerCase().includes('sanit')) || depts[3];

    // 7. Seed Staff Contractors if empty
    const contractorCount = await db.getAsync('SELECT COUNT(*) as count FROM staff_contractors');
    if (contractorCount.count === 0) {
      console.log('🌱 Seeding staff and contractors...');
      const initialStaff = [
        {
          id: 'staff-el-01',
          name: 'Abebe Kebede',
          phone_number: '+251 91 123 4567',
          email: 'abebe.k@cirp.gov.et',
          department_id: elecDept.id,
          department_name: elecDept.name,
          role_type: 'STAFF_OFFICER',
          position_title: 'Senior Electrical Engineer',
          specialization: 'High-voltage Grid & Street Lighting',
          is_contractor: 0,
          contractor_company_name: null,
          license_number: 'LIC-EE-4890',
          active_tasks_count: 2,
          completed_tasks_count: 34,
          overdue_tasks_count: 0,
          performance_score: 97,
          is_available: 1
        },
        {
          id: 'contractor-el-02',
          name: 'Ethio-Power Infrastructure Ltd',
          phone_number: '+251 92 345 6789',
          email: 'ops@ethiopower.com',
          department_id: elecDept.id,
          department_name: elecDept.name,
          role_type: 'CONTRACTOR_LEAD',
          position_title: 'Chief Technical Supervisor',
          specialization: 'LED Lamp Replacements & Cable Trenching',
          is_contractor: 1,
          contractor_company_name: 'Ethio-Power Infrastructure Ltd',
          license_number: 'LIC-CON-8832',
          active_tasks_count: 3,
          completed_tasks_count: 85,
          overdue_tasks_count: 1,
          performance_score: 92,
          is_available: 1
        },
        {
          id: 'staff-rd-01',
          name: 'Tewodros Haile',
          phone_number: '+251 93 456 7890',
          email: 'tewodros.h@cirp.gov.et',
          department_id: roadDept.id,
          department_name: roadDept.name,
          role_type: 'STAFF_OFFICER',
          position_title: 'Road Maintenance Supervisor',
          specialization: 'Asphalt Patching & Pavement Assessment',
          is_contractor: 0,
          contractor_company_name: null,
          license_number: 'LIC-CE-1123',
          active_tasks_count: 1,
          completed_tasks_count: 42,
          overdue_tasks_count: 0,
          performance_score: 95,
          is_available: 1
        },
        {
          id: 'contractor-rd-02',
          name: 'Blue Nile Civil Works',
          phone_number: '+251 94 567 8901',
          email: 'support@bluenilecivil.et',
          department_id: roadDept.id,
          department_name: roadDept.name,
          role_type: 'CONTRACTOR_LEAD',
          position_title: 'Project Lead',
          specialization: 'Heavy Road Rehabilitation & Resurfacing',
          is_contractor: 1,
          contractor_company_name: 'Blue Nile Civil Works',
          license_number: 'LIC-CON-9011',
          active_tasks_count: 2,
          completed_tasks_count: 61,
          overdue_tasks_count: 0,
          performance_score: 94,
          is_available: 1
        },
        {
          id: 'staff-wt-01',
          name: 'Marta Hailu',
          phone_number: '+251 95 678 9012',
          email: 'marta.h@cirp.gov.et',
          department_id: waterDept.id,
          department_name: waterDept.name,
          role_type: 'STAFF_OFFICER',
          position_title: 'Hydraulic Inspector',
          specialization: 'Mainline Pipeline Repair & Valve Maintenance',
          is_contractor: 0,
          contractor_company_name: null,
          license_number: 'LIC-HE-5512',
          active_tasks_count: 2,
          completed_tasks_count: 53,
          overdue_tasks_count: 0,
          performance_score: 98,
          is_available: 1
        },
        {
          id: 'staff-sn-01',
          name: 'Solomon Bekele',
          phone_number: '+251 96 789 0123',
          email: 'solomon.b@cirp.gov.et',
          department_id: sanitDept.id,
          department_name: sanitDept.name,
          role_type: 'STAFF_OFFICER',
          position_title: 'Sanitation Logistics Lead',
          specialization: 'Waste Bin Depots & Route Management',
          is_contractor: 0,
          contractor_company_name: null,
          license_number: 'LIC-SAN-3341',
          active_tasks_count: 1,
          completed_tasks_count: 77,
          overdue_tasks_count: 0,
          performance_score: 96,
          is_available: 1
        }
      ];

      for (const staff of initialStaff) {
        await db.runAsync(`
          INSERT INTO staff_contractors (
            id, name, phone_number, email, department_id, department_name, role_type,
            position_title, specialization, is_contractor, contractor_company_name,
            license_number, active_tasks_count, completed_tasks_count, overdue_tasks_count,
            performance_score, is_available
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `, [
          staff.id, staff.name, staff.phone_number, staff.email, staff.department_id,
          staff.department_name, staff.role_type, staff.position_title, staff.specialization,
          staff.is_contractor, staff.contractor_company_name, staff.license_number,
          staff.active_tasks_count, staff.completed_tasks_count, staff.overdue_tasks_count,
          staff.performance_score, staff.is_available
        ]);
      }
      console.log(`✅ Seeded ${initialStaff.length} staff and contractors`);
    }

    // 8. Seed Assets if empty
    const assetCount = await db.getAsync('SELECT COUNT(*) as count FROM assets');
    if (assetCount.count === 0) {
      console.log('🌱 Seeding initial infrastructure assets...');
      const initialAssets = [
        {
          id: 'ast-stl-001',
          asset_code: 'STL-BOL-1042',
          asset_type_id: 'street_light',
          asset_type_label: 'Street Light',
          department_id: elecDept.id,
          department_name: elecDept.name,
          name: 'Bole Road Solar LED Pole #1042',
          description: 'High-efficiency 120W Solar LED fixture on 8m steel pole outside Atlas Hotel.',
          status: 'ACTIVE',
          condition: 'GOOD',
          installation_date: '2023-04-12',
          latitude: 9.0054,
          longitude: 38.7636,
          address: 'Bole Road, near Atlas, Addis Ababa',
          landmark: 'Opposite Atlas Hotel',
          registered_by: 'Abebe Kebede',
          registered_at: '2023-04-12 10:00:00',
          updated_at: '2026-10-20 14:00:00',
          last_inspection_date: '2026-09-15',
          active_reports_count: 2,
          specific_data: JSON.stringify({
            type: 'street_light',
            specs: {
              pole_type: 'Steel',
              light_type: 'Solar LED',
              power_source: 'Solar',
              height_meters: 8,
              wattage_watts: 120
            }
          })
        },
        {
          id: 'ast-stl-002',
          asset_code: 'STL-MES-2104',
          asset_type_id: 'street_light',
          asset_type_label: 'Street Light',
          department_id: elecDept.id,
          department_name: elecDept.name,
          name: 'Meskel Square Grid LED Mast #2104',
          description: 'High-mast 250W LED illumination grid luminaire.',
          status: 'ACTIVE',
          condition: 'EXCELLENT',
          installation_date: '2022-09-20',
          latitude: 9.0104,
          longitude: 38.7612,
          address: 'Meskel Square, Addis Ababa',
          landmark: 'Exhibition Center Gate',
          registered_by: 'Abebe Kebede',
          registered_at: '2022-09-20 11:30:00',
          updated_at: '2026-10-18 09:15:00',
          last_inspection_date: '2026-10-01',
          active_reports_count: 0,
          specific_data: JSON.stringify({
            type: 'street_light',
            specs: {
              pole_type: 'Steel',
              light_type: 'LED',
              power_source: 'Grid',
              height_meters: 12,
              wattage_watts: 250
            }
          })
        },
        {
          id: 'ast-rd-001',
          asset_code: 'RD-CR-0412',
          asset_type_id: 'road',
          asset_type_label: 'Road Section',
          department_id: roadDept.id,
          department_name: roadDept.name,
          name: 'Churchill Avenue Arterial Segment 2',
          description: 'Four-lane asphalt dual carriageway from Tewodros Square to Piassa.',
          status: 'ACTIVE',
          condition: 'FAIR',
          installation_date: '2021-02-15',
          latitude: 9.0289,
          longitude: 38.7516,
          address: 'Churchill Ave, Arada, Addis Ababa',
          landmark: 'Near Tewodros Square',
          registered_by: 'Tewodros Haile',
          registered_at: '2021-02-15 08:00:00',
          updated_at: '2026-10-12 16:30:00',
          last_inspection_date: '2026-08-20',
          active_reports_count: 1,
          specific_data: JSON.stringify({
            type: 'road',
            specs: {
              road_name: 'Churchill Avenue Segment 2',
              road_type: 'Arterial Highway',
              surface_type: 'Asphalt',
              length_km: 1.4,
              width_meters: 18.0,
              lanes_count: 4
            }
          })
        },
        {
          id: 'ast-wt-001',
          asset_code: 'WTR-MEG-019',
          asset_type_id: 'water_point',
          asset_type_label: 'Water Point',
          department_id: waterDept.id,
          department_name: waterDept.name,
          name: 'Megenagna Distribution Main Valve V-19',
          description: '250mm ductile iron valve junction feeding neighborhood zones 4 and 5.',
          status: 'ACTIVE',
          condition: 'GOOD',
          installation_date: '2020-06-10',
          latitude: 9.0205,
          longitude: 38.7901,
          address: 'Megenagna Roundabout, Yeka, Addis Ababa',
          landmark: 'Zefmesh Grand Mall Corner',
          registered_by: 'Marta Hailu',
          registered_at: '2020-06-10 09:00:00',
          updated_at: '2026-10-05 11:20:00',
          last_inspection_date: '2026-09-10',
          active_reports_count: 1,
          specific_data: JSON.stringify({
            type: 'water_point',
            specs: {
              pipe_type: 'Distribution Main',
              pipe_diameter_mm: 250,
              material: 'Ductile Iron',
              flow_capacity_lps: 45,
              supply_source: 'Municipal Reservoir'
            }
          })
        },
        {
          id: 'ast-dr-001',
          asset_code: 'DRN-GOT-008',
          asset_type_id: 'drainage',
          asset_type_label: 'Drainage Channel',
          department_id: waterDept.id,
          department_name: waterDept.name,
          name: 'Gotera Stormwater Culvert C-8',
          description: 'Reinforced underground concrete drainage culvert directing highway runoff.',
          status: 'ACTIVE',
          condition: 'FAIR',
          installation_date: '2019-11-04',
          latitude: 8.9892,
          longitude: 38.7548,
          address: 'Gotera Interchange, Nifas Silk, Addis Ababa',
          landmark: 'Under Gotera Flyover East Ramp',
          registered_by: 'Marta Hailu',
          registered_at: '2019-11-04 14:00:00',
          updated_at: '2026-09-28 10:15:00',
          last_inspection_date: '2026-07-22',
          active_reports_count: 0,
          specific_data: JSON.stringify({
            type: 'drainage',
            specs: {
              drain_type: 'Underground Culvert',
              width_meters: 2.5,
              depth_meters: 1.8,
              flow_direction: 'Towards River Basin',
              has_safety_grate: true
            }
          })
        },
        {
          id: 'ast-wst-001',
          asset_code: 'WST-PIAS-014',
          asset_type_id: 'waste_bin',
          asset_type_label: 'Waste Station',
          department_id: sanitDept.id,
          department_name: sanitDept.name,
          name: 'Piassa Municipal Public Dumpster #14',
          description: 'Standard steel high-capacity communal waste container with tilt mechanism.',
          status: 'ACTIVE',
          condition: 'GOOD',
          installation_date: '2024-01-18',
          latitude: 9.0351,
          longitude: 38.7523,
          address: 'Piassa, Arada, Addis Ababa',
          landmark: 'Near St. George Cathedral Square',
          registered_by: 'Solomon Bekele',
          registered_at: '2024-01-18 13:00:00',
          updated_at: '2026-10-14 08:30:00',
          last_inspection_date: '2026-10-10',
          active_reports_count: 0,
          specific_data: JSON.stringify({
            type: 'waste_bin',
            specs: {
              bin_type: 'Large Dumpster',
              capacity_liters: 1100,
              collection_frequency: 'Daily'
            }
          })
        }
      ];

      for (const asset of initialAssets) {
        await db.runAsync(`
          INSERT INTO assets (
            id, asset_code, asset_type_id, asset_type_label, department_id, department_name,
            name, description, status, condition, installation_date, latitude, longitude,
            address, landmark, registered_by, registered_at, updated_at, last_inspection_date,
            active_reports_count, specific_data
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `, [
          asset.id, asset.asset_code, asset.asset_type_id, asset.asset_type_label,
          asset.department_id, asset.department_name, asset.name, asset.description,
          asset.status, asset.condition, asset.installation_date, asset.latitude,
          asset.longitude, asset.address, asset.landmark, asset.registered_by,
          asset.registered_at, asset.updated_at, asset.last_inspection_date,
          asset.active_reports_count, asset.specific_data
        ]);
      }
      console.log(`✅ Seeded ${initialAssets.length} physical assets`);
    }

    // 9. Seed 1-2 active tasks for realistic initial dashboard pipeline
    const taskCount = await db.getAsync('SELECT COUNT(*) as count FROM tasks');
    if (taskCount.count === 0) {
      console.log('🌱 Seeding initial active operational tasks...');
      const sampleReport = await db.getAsync('SELECT * FROM reports WHERE department_id = ? LIMIT 1', [elecDept.id]);
      if (sampleReport) {
        const taskId = `task-${Date.now()}`;
        const taskCode = `TSK-STL-1042-4910`;
        const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
        const deadline = '2026-11-05';
        
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
          sampleReport.id,
          sampleReport.report_code || 'REP-INIT',
          'ast-stl-001',
          'STL-BOL-1042',
          'Street Light',
          elecDept.id,
          elecDept.name,
          'staff-el-01',
          'Abebe Kebede',
          0,
          null,
          'Replace damaged luminaire fuse and inspect battery controller for voltage fluctuation.',
          'Parts issued from depot. Priority response for street corridor visibility.',
          'HIGH',
          'IN_PROGRESS',
          40,
          now,
          deadline,
          deadline,
          0,
          0,
          JSON.stringify([
            {
              timestamp: now,
              author: 'Abebe Kebede',
              note: 'Dispatched to location. Confirmed blown driver unit. Installing spare module.',
              percentage: 40
            }
          ]),
          JSON.stringify([])
        ]);

        // Update report status
        await db.runAsync('UPDATE reports SET status = ? WHERE id = ?', ['assigned', sampleReport.id]);
        console.log('✅ Seeded initial task linked to report ' + sampleReport.id);
      }
    }

    console.log('\n🎉 CIRP Migration and Seeding Completed Successfully!\n');
    process.exit(0);
  } catch (error) {
    console.error('❌ Migration error:', error);
    process.exit(1);
  }
}

migrateAndSeed();
