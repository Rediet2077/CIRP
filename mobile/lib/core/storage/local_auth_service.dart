import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LocalAuthService {
  static const String _usersKey = 'local_users';
  static const String _currentUserKey = 'current_user';
  static const String _isLoggedInKey = 'is_logged_in';

  // User model for local storage
  static Future<void> _initializeDefaultUser() async {
    final prefs = await SharedPreferences.getInstance();
    final users = await _getUsers();
    
    if (users.isEmpty) {
      // Create default test user
      final defaultUser = {
        'id': '1',
        'email': 'citizen@test.com',
        'password': 'Test@123', // In real app, this should be hashed
        'full_name': 'Test Citizen',
        'phone_number': '+251912345678',
        'created_at': DateTime.now().toIso8601String(),
      };
      
      users.add(defaultUser);
      await prefs.setString(_usersKey, jsonEncode(users));
    }
  }

  static Future<List<Map<String, dynamic>>> _getUsers() async {
    final prefs = await SharedPreferences.getInstance();
    final usersJson = prefs.getString(_usersKey);
    
    if (usersJson == null) {
      return [];
    }
    
    return List<Map<String, dynamic>>.from(jsonDecode(usersJson));
  }

  // Login
  static Future<Map<String, dynamic>> login(String email, String password) async {
    await _initializeDefaultUser();
    
    final users = await _getUsers();
    final user = users.firstWhere(
      (u) => u['email'] == email && u['password'] == password,
      orElse: () => {},
    );

    if (user.isEmpty) {
      throw Exception('Invalid email or password');
    }

    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_isLoggedInKey, true);
    await prefs.setString(_currentUserKey, jsonEncode(user));

    return {
      'success': true,
      'user': user,
      'message': 'Login successful',
    };
  }

  // Signup
  static Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
    required String fullName,
    required String phoneNumber,
  }) async {
    final users = await _getUsers();
    
    // Check if email already exists
    final existingUser = users.firstWhere(
      (u) => u['email'] == email,
      orElse: () => {},
    );

    if (existingUser.isNotEmpty) {
      throw Exception('Email already exists');
    }

    // Create new user
    final newUser = {
      'id': DateTime.now().millisecondsSinceEpoch.toString(),
      'email': email,
      'password': password,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'created_at': DateTime.now().toIso8601String(),
    };

    users.add(newUser);
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_usersKey, jsonEncode(users));

    return {
      'success': true,
      'user': newUser,
      'message': 'Account created successfully',
    };
  }

  // Get current user
  static Future<Map<String, dynamic>?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_currentUserKey);
    
    if (userJson == null) {
      return null;
    }
    
    return Map<String, dynamic>.from(jsonDecode(userJson));
  }

  // Check if logged in
  static Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_isLoggedInKey) ?? false;
  }

  // Logout
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_isLoggedInKey);
    await prefs.remove(_currentUserKey);
  }

  // Update user profile
  static Future<Map<String, dynamic>> updateProfile({
    required String fullName,
    required String phoneNumber,
  }) async {
    final currentUser = await getCurrentUser();
    if (currentUser == null) {
      throw Exception('No user logged in');
    }

    currentUser['full_name'] = fullName;
    currentUser['phone_number'] = phoneNumber;
    currentUser['updated_at'] = DateTime.now().toIso8601String();

    // Update in users list
    final users = await _getUsers();
    final index = users.indexWhere((u) => u['id'] == currentUser['id']);
    if (index != -1) {
      users[index] = currentUser;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_usersKey, jsonEncode(users));
      await prefs.setString(_currentUserKey, jsonEncode(currentUser));
    }

    return currentUser;
  }

  // Verify email (mock - just mark as verified)
  static Future<bool> verifyEmail(String otp) async {
    // Mock verification - always success with any 6-digit code
    if (otp.length == 6) {
      final currentUser = await getCurrentUser();
      if (currentUser != null) {
        currentUser['email_verified'] = true;
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_currentUserKey, jsonEncode(currentUser));
      }
      return true;
    }
    return false;
  }

  // Resend OTP (mock)
  static Future<bool> resendOTP(String email) async {
    // Mock - always success
    return true;
  }
}
