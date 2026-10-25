import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/api_constants.dart';

class ApiService {
  /// Get authorization headers with token
  static Future<Map<String, String>> _getAuthHeaders() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token') ?? '';
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  /// Get current user profile
  static Future<Map<String, dynamic>> getUserProfile() async {
    try {
      final headers = await _getAuthHeaders();
      final response = await http.get(
        Uri.parse(ApiConstants.profileUrl),
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to fetch profile',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Get all reports (paginated)
  static Future<Map<String, dynamic>> getReports({
    int page = 1,
    int pageSize = 20,
    String? status,
    String? category,
  }) async {
    try {
      final headers = await _getAuthHeaders();
      
      // Build query parameters
      final queryParams = {
        'page': page.toString(),
        'page_size': pageSize.toString(),
      };
      if (status != null) queryParams['status'] = status;
      if (category != null) queryParams['category'] = category;
      
      final uri = Uri.parse(ApiConstants.reportsUrl).replace(
        queryParameters: queryParams,
      );

      final response = await http.get(
        uri,
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final reports = data['reports'] ?? data['data'] ?? [];
        return {
          'success': true,
          'data': reports,
          'count': data['total'] ?? data['count'] ?? (reports is List ? reports.length : 0),
          'next': data['next'],
          'previous': data['previous'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to fetch reports',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Get user's own reports
  static Future<Map<String, dynamic>> getMyReports({int page = 1}) async {
    try {
      final headers = await _getAuthHeaders();
      
      final uri = Uri.parse(ApiConstants.myReportsUrl).replace(
        queryParameters: {
          'page': page.toString(),
        },
      );

      final response = await http.get(
        uri,
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        // Backend returns {reports: [...], total, page, limit}
        final reports = data['reports'] ?? data['data'] ?? [];
        return {
          'success': true,
          'data': reports,
          'count': data['total'] ?? data['count'] ?? reports.length,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to fetch your reports',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Get report by ID
  static Future<Map<String, dynamic>> getReportById(dynamic id) async {
    try {
      final headers = await _getAuthHeaders();
      final response = await http.get(
        Uri.parse(ApiConstants.reportDetailUrl(id.toString())),
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final report = data is Map<String, dynamic> ? (data['report'] ?? data['data'] ?? data) : data;
        return {
          'success': true,
          'data': report,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to fetch report',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Get report details (alias for getReportById)
  static Future<Map<String, dynamic>> getReportDetails(dynamic id) async {
    return getReportById(id);
  }

  /// Create new report
  static Future<Map<String, dynamic>> createReport({
    required String title,
    required String description,
    required dynamic categoryId,
    required double latitude,
    required double longitude,
    String? address,
    String priority = 'MEDIUM',
    List<String>? images,
  }) async {
    try {
      final headers = await _getAuthHeaders();
      
      final body = <String, dynamic>{
        'title': title,
        'description': description,
        'category_id': categoryId.toString(),
        'latitude': latitude,
        'longitude': longitude,
        'priority': priority.toUpperCase(),
      };
      
      if (address != null) body['address'] = address;
      if (images != null && images.isNotEmpty) {
        body['images'] = images;
        body['media_images'] = images;
      }

      final response = await http.post(
        Uri.parse(ApiConstants.reportsUrl),
        headers: headers,
        body: jsonEncode(body),
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 201) {
        return {
          'success': true,
          'message': data['message'] ?? 'Report created successfully',
          'data': data['report'] ?? data['data'] ?? data,
        };
      } else {
        String errMsg = data['message'] ?? data['detail'] ?? '';
        if (errMsg.isEmpty && data is Map) {
          errMsg = data.entries.map((e) => '${e.key}: ${e.value}').join(', ');
        }
        if (errMsg.isEmpty) {
          errMsg = 'Failed to create report (${response.statusCode})';
        }
        return {
          'success': false,
          'message': errMsg,
          'errors': data,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Get all categories
  static Future<Map<String, dynamic>> getCategories() async {
    try {
      final headers = await _getAuthHeaders();
      final response = await http.get(
        Uri.parse(ApiConstants.categoriesUrl),
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final categories = data['categories'] ?? data['data'] ?? [];
        return {
          'success': true,
          'data': categories,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to fetch categories',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Get all departments
  static Future<Map<String, dynamic>> getDepartments() async {
    try {
      final headers = await _getAuthHeaders();
      final response = await http.get(
        Uri.parse(ApiConstants.departmentsUrl),
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final departments = data['departments'] ?? data['data'] ?? [];
        return {
          'success': true,
          'data': departments,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to fetch departments',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Get notifications
  static Future<Map<String, dynamic>> getNotifications({int page = 1}) async {
    try {
      final headers = await _getAuthHeaders();
      final uri = Uri.parse(ApiConstants.notificationsUrl).replace(
        queryParameters: {'page': page.toString()},
      );

      final response = await http.get(
        uri,
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final notifications = data['notifications'] ?? data['data'] ?? [];
        return {
          'success': true,
          'data': notifications,
          'count': data['count'] ?? (notifications is List ? notifications.length : 0),
          'unread_count': data['unread_count'] ?? 0,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to fetch notifications',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Get dashboard statistics
  static Future<Map<String, dynamic>> getDashboardStats() async {
    try {
      // Fetch user's reports to get statistics
      final myReportsResult = await getMyReports();
      final allReportsResult = await getReports(pageSize: 1);
      
      int myReportsCount = 0;
      int pendingCount = 0;
      int inProgressCount = 0;
      int resolvedCount = 0;
      
      if (myReportsResult['success'] == true) {
        myReportsCount = myReportsResult['count'] ?? 0;
        final reports = myReportsResult['data'] as List? ?? [];
        
        for (var report in reports) {
          final status = (report['status'] ?? '').toString().toLowerCase();
          if (status == 'pending' || status == 'new') {
            pendingCount++;
          } else if (status == 'in_progress' || status == 'assigned') {
            inProgressCount++;
          } else if (status == 'resolved') {
            resolvedCount++;
          }
        }
      }
      
      final totalReports = allReportsResult['count'] ?? 0;
      
      return {
        'success': true,
        'data': {
          'my_reports': myReportsCount,
          'pending': pendingCount,
          'in_progress': inProgressCount,
          'resolved': resolvedCount,
          'total_reports': totalReports,
        },
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Delete or remove report from citizen history
  static Future<Map<String, dynamic>> deleteReport(String reportId) async {
    try {
      final headers = await _getAuthHeaders();
      var response = await http.delete(
        Uri.parse('${ApiConstants.reportsUrl}/$reportId'),
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      if (response.statusCode != 200 && response.statusCode != 204) {
        response = await http.post(
          Uri.parse('${ApiConstants.apiBaseUrl}/reports/$reportId/citizen-delete/'),
          headers: headers,
        ).timeout(ApiConstants.connectTimeout);
      }

      if (response.statusCode == 200 || response.statusCode == 204) {
        return {'success': true, 'message': 'Report removed successfully'};
      }
      return {'success': false, 'message': 'Failed to delete report'};
    } catch (e) {
      return {'success': false, 'message': 'Network error: $e'};
    }
  }

  /// Delete notification
  static Future<Map<String, dynamic>> deleteNotification(String notificationId) async {
    try {
      final headers = await _getAuthHeaders();
      final response = await http.delete(
        Uri.parse('${ApiConstants.apiBaseUrl}/notifications/$notificationId/'),
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      if (response.statusCode == 200 || response.statusCode == 204) {
        return {'success': true, 'message': 'Notification deleted successfully'};
      }
      
      final data = response.body.isNotEmpty ? jsonDecode(response.body) : {};
      return {
        'success': false,
        'message': data['error'] ?? data['message'] ?? 'Failed to delete notification',
      };
    } catch (e) {
      return {'success': false, 'message': 'Network error: $e'};
    }
  }

  /// Clear all notifications
  static Future<Map<String, dynamic>> clearAllNotifications() async {
    try {
      final headers = await _getAuthHeaders();
      final response = await http.post(
        Uri.parse('${ApiConstants.apiBaseUrl}/notifications/clear-all/'),
        headers: headers,
      ).timeout(ApiConstants.connectTimeout);

      if (response.statusCode == 200 || response.statusCode == 204) {
        final data = response.body.isNotEmpty ? jsonDecode(response.body) : {};
        return {
          'success': true,
          'message': data['message'] ?? 'All notifications cleared',
          'deleted_count': data['deleted_count'] ?? 0,
        };
      }
      
      final data = response.body.isNotEmpty ? jsonDecode(response.body) : {};
      return {
        'success': false,
        'message': data['error'] ?? data['message'] ?? 'Failed to clear notifications',
      };
    } catch (e) {
      return {'success': false, 'message': 'Network error: $e'};
    }
  }

  /// Send OTP to email
  static Future<Map<String, dynamic>> sendOTP({
    required String email,
    required String fullName,
    String purpose = 'registration',
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConstants.sendOTPUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'full_name': fullName,
          'purpose': purpose,
        }),
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      return {
        'success': data['success'] ?? false,
        'message': data['message'] ?? '',
        'expiresAt': data['expiresAt'],
        'expiresIn': data['expiresIn'],
        'retryAfter': data['retryAfter'],
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Verify OTP code
  static Future<Map<String, dynamic>> verifyOTP({
    required String email,
    required String otpCode,
    String purpose = 'registration',
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConstants.verifyOTPUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'otp_code': otpCode,
          'purpose': purpose,
        }),
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      return {
        'success': data['success'] ?? false,
        'message': data['message'] ?? '',
        'verified': data['verified'] ?? false,
        'attemptsLeft': data['attemptsLeft'],
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
        'verified': false,
      };
    }
  }

  /// Resend OTP code
  static Future<Map<String, dynamic>> resendOTP({
    required String email,
    required String fullName,
    String purpose = 'registration',
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConstants.resendOTPUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'full_name': fullName,
          'purpose': purpose,
        }),
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      return {
        'success': data['success'] ?? false,
        'message': data['message'] ?? '',
        'expiresAt': data['expiresAt'],
        'expiresIn': data['expiresIn'],
        'retryAfter': data['retryAfter'],
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }
}
