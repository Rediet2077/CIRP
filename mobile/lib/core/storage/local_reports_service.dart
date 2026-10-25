import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LocalReportsService {
  static const String _reportsKey = 'local_reports';
  static const String _reportIdCounterKey = 'report_id_counter';

  // Initialize with sample reports
  static Future<void> _initializeSampleData() async {
    final reports = await _getReports();
    
    if (reports.isEmpty) {
      final sampleReports = [
        {
          'id': '1',
          'user_id': '1',
          'category': 'Road Damage',
          'description': 'Large pothole on Main Street causing traffic issues',
          'location': 'Main Street, Addis Ababa',
          'latitude': 9.0320,
          'longitude': 38.7469,
          'status': 'in_progress',
          'created_at': DateTime.now().subtract(const Duration(days: 5)).toIso8601String(),
          'updated_at': DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
          'has_photo': true,
        },
        {
          'id': '2',
          'user_id': '1',
          'category': 'Water Leakage',
          'description': 'Water pipe burst near the market area',
          'location': 'Merkato, Addis Ababa',
          'latitude': 9.0141,
          'longitude': 38.7251,
          'status': 'submitted',
          'created_at': DateTime.now().subtract(const Duration(days: 3)).toIso8601String(),
          'updated_at': DateTime.now().subtract(const Duration(days: 3)).toIso8601String(),
          'has_photo': false,
        },
        {
          'id': '3',
          'user_id': '1',
          'category': 'Streetlight',
          'description': 'Street lights not working for a week',
          'location': 'Bole Road',
          'latitude': 8.9938,
          'longitude': 38.7861,
          'status': 'resolved',
          'created_at': DateTime.now().subtract(const Duration(days: 10)).toIso8601String(),
          'updated_at': DateTime.now().subtract(const Duration(days: 1)).toIso8601String(),
          'has_photo': true,
        },
      ];

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_reportsKey, jsonEncode(sampleReports));
      await prefs.setInt(_reportIdCounterKey, 4);
    }
  }

  static Future<List<Map<String, dynamic>>> _getReports() async {
    final prefs = await SharedPreferences.getInstance();
    final reportsJson = prefs.getString(_reportsKey);
    
    if (reportsJson == null) {
      return [];
    }
    
    return List<Map<String, dynamic>>.from(jsonDecode(reportsJson));
  }

  // Get all reports for current user
  static Future<List<Map<String, dynamic>>> getUserReports(String userId) async {
    await _initializeSampleData();
    
    final reports = await _getReports();
    return reports.where((r) => r['user_id'] == userId).toList()
      ..sort((a, b) => b['created_at'].compareTo(a['created_at']));
  }

  // Get reports by status
  static Future<List<Map<String, dynamic>>> getReportsByStatus(String userId, String status) async {
    final reports = await getUserReports(userId);
    return reports.where((r) => r['status'] == status).toList();
  }

  // Get single report
  static Future<Map<String, dynamic>?> getReport(String reportId) async {
    final reports = await _getReports();
    try {
      return reports.firstWhere((r) => r['id'] == reportId);
    } catch (e) {
      return null;
    }
  }

  // Create new report
  static Future<Map<String, dynamic>> createReport({
    required String userId,
    required String category,
    required String description,
    required String location,
    required double latitude,
    required double longitude,
    bool hasPhoto = false,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final reports = await _getReports();
    
    // Get next ID
    int counter = prefs.getInt(_reportIdCounterKey) ?? 1;
    
    final newReport = {
      'id': counter.toString(),
      'user_id': userId,
      'category': category,
      'description': description,
      'location': location,
      'latitude': latitude,
      'longitude': longitude,
      'status': 'submitted',
      'created_at': DateTime.now().toIso8601String(),
      'updated_at': DateTime.now().toIso8601String(),
      'has_photo': hasPhoto,
    };

    reports.add(newReport);
    await prefs.setString(_reportsKey, jsonEncode(reports));
    await prefs.setInt(_reportIdCounterKey, counter + 1);

    return newReport;
  }

  // Update report status
  static Future<Map<String, dynamic>> updateReportStatus(String reportId, String status) async {
    final reports = await _getReports();
    final index = reports.indexWhere((r) => r['id'] == reportId);
    
    if (index == -1) {
      throw Exception('Report not found');
    }

    reports[index]['status'] = status;
    reports[index]['updated_at'] = DateTime.now().toIso8601String();

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_reportsKey, jsonEncode(reports));

    return reports[index];
  }

  // Delete report
  static Future<void> deleteReport(String reportId) async {
    final reports = await _getReports();
    reports.removeWhere((r) => r['id'] == reportId);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_reportsKey, jsonEncode(reports));
  }

  // Get recent reports (last 5)
  static Future<List<Map<String, dynamic>>> getRecentReports(String userId) async {
    final reports = await getUserReports(userId);
    return reports.take(5).toList();
  }

  // Get statistics
  static Future<Map<String, int>> getStatistics(String userId) async {
    final reports = await getUserReports(userId);
    
    return {
      'total': reports.length,
      'submitted': reports.where((r) => r['status'] == 'submitted').length,
      'in_progress': reports.where((r) => r['status'] == 'in_progress').length,
      'resolved': reports.where((r) => r['status'] == 'resolved').length,
      'rejected': reports.where((r) => r['status'] == 'rejected').length,
    };
  }

  // Clear all reports (for testing)
  static Future<void> clearAllReports() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_reportsKey);
    await prefs.remove(_reportIdCounterKey);
  }
}
