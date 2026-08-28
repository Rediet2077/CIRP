/// API Configuration for CIRP Backend
class ApiConstants {
  // Base URLs
  static const String _localBaseUrl = 'http://localhost:8000';
  static const String _androidEmulatorBaseUrl = 'http://10.0.2.2:8000';
  static const String _physicalDeviceBaseUrl = 'http://10.102.4.204:8000'; // Your PC IP
  
  // Change this based on your device
  // Use _localBaseUrl for iOS Simulator, Chrome, Windows, macOS
  // Use _androidEmulatorBaseUrl for Android Emulator
  // Use _physicalDeviceBaseUrl for physical devices (phone)
  static const String baseUrl = _physicalDeviceBaseUrl; // Changed for physical device
  
  // API Version
  static const String apiVersion = '/api/v1';
  
  // Full API Base URL
  static String get apiBaseUrl => '$baseUrl$apiVersion';
  
  // Authentication Endpoints
  static String get loginUrl => '$apiBaseUrl/auth/login/';
  static String get registerUrl => '$apiBaseUrl/auth/register/';
  static String get logoutUrl => '$apiBaseUrl/auth/logout/';
  static String get refreshTokenUrl => '$apiBaseUrl/auth/token/refresh/';
  
  // Reports Endpoints
  static String get reportsUrl => '$apiBaseUrl/reports/';
  static String get myReportsUrl => '$apiBaseUrl/reports/my-reports/';
  static String reportDetailUrl(int id) => '$apiBaseUrl/reports/$id/';
  
  // Categories Endpoints
  static String get categoriesUrl => '$apiBaseUrl/categories/';
  
  // Departments Endpoints
  static String get departmentsUrl => '$apiBaseUrl/departments/';
  
  // User Profile Endpoints
  static String get profileUrl => '$apiBaseUrl/users/me/';
  static String get updateProfileUrl => '$apiBaseUrl/users/me/update/';
  
  // Notifications Endpoints
  static String get notificationsUrl => '$apiBaseUrl/notifications/';
  
  // Assets Endpoints
  static String get assetsUrl => '$apiBaseUrl/assets/';
  
  // AI Service
  static const String aiServiceBaseUrl = 'http://10.102.4.204:8001'; // Your PC IP
  static String get imageClassificationUrl => '$aiServiceBaseUrl/classify/';
  static String get duplicateDetectionUrl => '$aiServiceBaseUrl/detect-duplicate/';
  
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
