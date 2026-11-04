class ApiConfig {
  // Use localhost with ADB reverse port forwarding
  // ADB command: adb reverse tcp:8000 tcp:8000
  static const String computerIp = 'localhost';
  
  // API URLs
  static const String baseUrl = 'http://$computerIp:8000';
  static const String aiServiceUrl = 'http://$computerIp:8001';
  
  // API Endpoints
  static const String apiVersion = '/api/v1';
  
  // Auth
  static const String loginEndpoint = '$apiVersion/auth/login/';
  static const String registerEndpoint = '$apiVersion/auth/register/';
  static const String refreshTokenEndpoint = '$apiVersion/auth/token/refresh/';
  static const String passwordResetRequestEndpoint = '$apiVersion/auth/password-reset/request/';
  static const String passwordResetVerifyEndpoint = '$apiVersion/auth/password-reset/verify/';
  static const String passwordResetConfirmEndpoint = '$apiVersion/auth/password-reset/confirm/';
  
  // Reports
  static const String reportsEndpoint = '$apiVersion/reports/';
  static const String submitReportEndpoint = '/submit-report/';
  
  // Categories
  static const String categoriesEndpoint = '$apiVersion/categories/';
  
  // Departments
  static const String departmentsEndpoint = '$apiVersion/departments/';
  
  // Notifications
  static const String notificationsEndpoint = '$apiVersion/notifications/';
  
  // AI Services
  static const String aiClassifyImageEndpoint = '/ai/classify-image/';
  static const String aiCheckQualityEndpoint = '/ai/check-quality/';
  static const String aiAutoFillEndpoint = '/ai/auto-fill/';
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
