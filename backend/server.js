const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Enable strict routing to be false (allows trailing slashes)
app.set('strict routing', false);

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN?.split(',') || '*',
  credentials: true
}));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Static files (for uploads)
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/otp', require('./routes/otp'));
app.use('/api/reports', require('./routes/reports'));
app.use('/api/users', require('./routes/users'));
app.use('/api/categories', require('./routes/categories'));
app.use('/api/departments', require('./routes/departments'));
app.use('/api/contractors', require('./routes/contractors'));
app.use('/api/assets', require('./routes/assets'));
app.use('/api/asset-types', require('./routes/asset-types'));
app.use('/api/tasks', require('./routes/tasks'));
app.use('/api/notifications', require('./routes/notifications'));
app.use('/api/analytics', require('./routes/analytics'));
app.use('/api/map', require('./routes/map'));
app.use('/api/audit-logs', require('./routes/audit-logs'));
app.use('/api/extensions', require('./routes/extensions'));

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'CIRP Backend API',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/health',
      auth: '/api/auth',
      otp: '/api/otp',
      reports: '/api/reports',
      users: '/api/users',
      categories: '/api/categories'
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error'
  });
});

// Start server - listen on all interfaces (0.0.0.0) to allow mobile/network access
app.listen(PORT, '0.0.0.0', () => {
  console.log('\n🚀 CIRP Backend Server Started!');
  console.log(`📡 Server running on http://localhost:${PORT}`);
  console.log(`📡 Network access: http://192.168.8.60:${PORT}`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📊 Database: ${process.env.DB_NAME}`);
  console.log('\n📋 Available endpoints:');
  console.log(`   - Health: http://localhost:${PORT}/health`);
  console.log(`   - Auth: http://localhost:${PORT}/api/auth`);
  console.log(`   - OTP: http://localhost:${PORT}/api/otp`);
  console.log(`   - Reports: http://localhost:${PORT}/api/reports`);
  console.log(`   - Users: http://localhost:${PORT}/api/users`);
  console.log(`   - Categories: http://localhost:${PORT}/api/categories`);
  console.log('\n✨ Ready to accept requests!\n');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\nSIGINT received, shutting down gracefully...');
  process.exit(0);
});
