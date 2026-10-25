import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';

class AuthService {
  /// Register a new user
  static Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
    String? phoneNumber,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConstants.registerUrl),
        headers: ApiConstants.headers,
        body: jsonEncode({
          'email': email,
          'password': password,
          'full_name': fullName,
          'phone_number': phoneNumber ?? '',
        }),
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 201 || response.statusCode == 200) {
        return {
          'success': data['success'] ?? true,
          'message': data['message'] ?? 'Registration successful',
          'user': data['user'],
          'requiresVerification': data['requiresVerification'] ?? false,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? data['error'] ?? 'Registration failed',
          'errors': data['errors'],
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// Login user
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConstants.loginUrl),
        headers: ApiConstants.headers,
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      ).timeout(ApiConstants.connectTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        // Backend returns: {success, message, token, user: {id, email, full_name, role}}
        return {
          'success': data['success'] ?? true,
          'message': data['message'] ?? 'Login successful',
          'token': data['token'] ?? data['access'] ?? '',
          'user': data['user'],
        };
      } else if (response.statusCode == 403) {
        // Email not verified
        return {
          'success': false,
          'message': data['message'] ?? 'Email not verified',
          'requiresVerification': data['requiresVerification'] ?? false,
          'email': data['email'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? data['error'] ?? 'Login failed',
          'errors': data['errors'],
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }
}
