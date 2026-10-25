/// API Configuration for CIRP Backend
class ApiConstants {
  // Base URLs
  static const String _localBaseUrl = 'http://localhost:3002';
  static const String _androidEmulatorBaseUrl = 'http://10.0.2.2:3002';
  static const String _physicalDeviceBaseUrl = 'http://localhost:3002'; // USB ADB reverse port forwarding
  
  // Change this based on your device
  // Use _localBaseUrl for USB debugging with 'adb reverse tcp:3002 tcp:3002'
  static const String baseUrl = _localBaseUrl;
  
  // API Version
  static const String apiVersion = '/api';
  
  // Full API Base URL
  static String get apiBaseUrl => '$baseUrl$apiVersion';
  
  // Authentication Endpoints
  static String get loginUrl => '$apiBaseUrl/auth/login';
  static String get registerUrl => '$apiBaseUrl/auth/register';
  static String get logoutUrl => '$apiBaseUrl/auth/logout';
  static String get refreshTokenUrl => '$apiBaseUrl/auth/refresh';
  static String get meUrl => '$apiBaseUrl/auth/me';
  static String get profileUrl => '$apiBaseUrl/auth/profile';
  static String get changePasswordUrl => '$apiBaseUrl/auth/change-password';
  
  // Reports Endpoints
  static String get reportsUrl => '$apiBaseUrl/reports';
  static String get myReportsUrl => '$apiBaseUrl/reports';
  static String reportDetailUrl(String id) => '$apiBaseUrl/reports/$id';
  static String reportStatusUrl(String id) => '$apiBaseUrl/reports/$id/status';
  static String reportCommentsUrl(String id) => '$apiBaseUrl/reports/$id/comments';
  static String get reportStatsUrl => '$apiBaseUrl/reports/stats/overview';
  
  // Categories Endpoints
  static String get categoriesUrl => '$apiBaseUrl/categories';
  static String categoryDetailUrl(String id) => '$apiBaseUrl/categories/$id';
  
  // Departments Endpoints (Future feature - return empty for now)
  static String get departmentsUrl => '$apiBaseUrl/departments';
  
  // OTP Endpoints
  static String get sendOTPUrl => '$apiBaseUrl/otp/send';
  static String get verifyOTPUrl => '$apiBaseUrl/otp/verify';
  static String get resendOTPUrl => '$apiBaseUrl/otp/resend';
  static String get checkOTPStatusUrl => '$apiBaseUrl/otp/check-status';
  
  // Users Endpoints
  static String get usersUrl => '$apiBaseUrl/users';
  static String userDetailUrl(String id) => '$apiBaseUrl/users/$id';
  
  // Notifications Endpoints
  static String get notificationsUrl => '$apiBaseUrl/notifications';
  
  // Request Headers
  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  static Map<String, String> authHeaders(String token) => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer $token',
  };
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}

