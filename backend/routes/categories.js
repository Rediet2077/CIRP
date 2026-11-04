const express = require('express');
const router = express.Router();
const db = require('../config/database');

// Get all categories
router.get('/', (req, res) => {
  try {
    const query = `
      SELECT c.*, d.name as department_name
      FROM categories c
      LEFT JOIN departments d ON c.department_id = d.id
      WHERE c.is_active = 1
      ORDER BY c.name
    `;
    
    db.all(query, [], (err, categories) => {
      if (err) {
        console.error('Get categories error:', err);
        return res.status(500).json({ error: 'Failed to fetch categories' });
      }
      
      res.json({
        success: true,
        categories,
        data: categories
      });
    });
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({ error: 'Failed to fetch categories' });
  }
});

// Get category by ID
router.get('/:id', (req, res) => {
  try {
    const { id } = req.params;

    const query = `
      SELECT c.*, d.name as department_name
      FROM categories c
      LEFT JOIN departments d ON c.department_id = d.id
      WHERE c.id = ?
    `;
    
    db.get(query, [id], (err, category) => {
      if (err) {
        console.error('Get category error:', err);
        return res.status(500).json({ error: 'Failed to fetch category' });
      }

      if (!category) {
        return res.status(404).json({ error: 'Category not found' });
      }

      res.json({ success: true, category, data: category });
    });
  } catch (error) {
    console.error('Get category error:', error);
    res.status(500).json({ error: 'Failed to fetch category' });
  }
});

module.exports = router;
