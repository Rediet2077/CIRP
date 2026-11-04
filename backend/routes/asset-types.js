const express = require('express');
const router = express.Router();
const db = require('../config/database');

// Get all asset types
router.get('/', async (req, res) => {
  try {
    const depts = await db.allAsync('SELECT id, name FROM departments');
    const elecDept = depts.find(d => d.name.toLowerCase().includes('electr')) || depts[0];
    const roadDept = depts.find(d => d.name.toLowerCase().includes('public') || d.name.toLowerCase().includes('road')) || depts[1];
    const waterDept = depts.find(d => d.name.toLowerCase().includes('water')) || depts[2];
    const sanitDept = depts.find(d => d.name.toLowerCase().includes('sanit')) || depts[3];

    // Counts from database
    const assetCounts = await db.allAsync('SELECT asset_type_id, COUNT(*) as count FROM assets GROUP BY asset_type_id');
    const countsMap = {};
    assetCounts.forEach(c => { countsMap[c.asset_type_id] = c.count; });

    const assetTypes = [
      {
        id: 'street_light',
        name: 'Street Light & Lighting Pole',
        description: 'Illumination luminaires, sodium vapor, LED fixtures, and electrical poles.',
        category_id: 'aeac7e07-736a-46ac-a8d4-e8d95ddc8138',
        responsible_department_id: elecDept?.id || 'dept-elec',
        responsible_department_name: elecDept?.name || 'Electrical Services',
        requires_location: true,
        is_active: true,
        total_assets_count: countsMap['street_light'] || 2
      },
      {
        id: 'road',
        name: 'Road Network & Arterial Segment',
        description: 'Paved roadways, asphalt carriageways, cobblestone routes, and intersection segments.',
        category_id: '771ed052-e3f0-4709-bf8c-30cf532751d8',
        responsible_department_id: roadDept?.id || 'dept-roads',
        responsible_department_name: roadDept?.name || 'Public Works',
        requires_location: true,
        is_active: true,
        total_assets_count: countsMap['road'] || 1
      },
      {
        id: 'water_point',
        name: 'Water Distribution Point & Hydrant',
        description: 'Potable water pipelines, public taps, main valves, and municipal hydrants.',
        category_id: 'c0810993-eba1-4649-bab3-759c52b5b6b6',
        responsible_department_id: waterDept?.id || 'dept-water',
        responsible_department_name: waterDept?.name || 'Water & Sewage',
        requires_location: true,
        is_active: true,
        total_assets_count: countsMap['water_point'] || 1
      },
      {
        id: 'drainage',
        name: 'Stormwater Culvert & Flood Grid',
        description: 'Runoff channels, underground concrete conduits, stormwater grates, and flood dikes.',
        category_id: 'ca7060f8-52d7-478b-9a46-da95eb3ac224',
        responsible_department_id: waterDept?.id || 'dept-water',
        responsible_department_name: waterDept?.name || 'Water & Sewage',
        requires_location: true,
        is_active: true,
        total_assets_count: countsMap['drainage'] || 1
      },
      {
        id: 'waste_bin',
        name: 'Communal Waste Bin & Compactor Depot',
        description: 'High-capacity solid waste dumpsters, neighborhood trash stations, and recycling pods.',
        category_id: '01393c0f-6bff-44ac-9533-7cdbeae21a4e',
        responsible_department_id: sanitDept?.id || 'dept-waste',
        responsible_department_name: sanitDept?.name || 'Sanitation',
        requires_location: true,
        is_active: true,
        total_assets_count: countsMap['waste_bin'] || 1
      },
      {
        id: 'public_building',
        name: 'Municipal Building & Public Facility',
        description: 'Administrative centers, community halls, health posts, and civic offices.',
        category_id: '0964f75b-4375-4986-803a-1a2bfaf2dd7e',
        responsible_department_id: roadDept?.id || 'dept-roads',
        responsible_department_name: roadDept?.name || 'Public Works',
        requires_location: true,
        is_active: true,
        total_assets_count: countsMap['public_building'] || 0
      }
    ];

    res.json(assetTypes);
  } catch (error) {
    console.error('Get asset types error:', error);
    res.status(500).json({ error: 'Failed to fetch asset types' });
  }
});

module.exports = router;
