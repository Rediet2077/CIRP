import 'package:shared_preferences/shared_preferences.dart';

/// Global authentication service that persists token across app lifecycle
/// This singleton keeps token in memory even when camera activity opens
class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  // Keep token in memory (survives app pause)
  String? _cachedToken;
  String? _cachedRefreshToken;

  /// Initialize auth service and load token
  Future<void> initialize() async {
    await _loadTokenFromStorage();
  }

  /// Load token from SharedPreferences into memory cache
  Future<void> _loadTokenFromStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _cachedToken = prefs.getString('access_token');
      _cachedRefreshToken = prefs.getString('refresh_token');
      print('🔐 AuthService: Token loaded into memory cache');
    } catch (e) {
      print('❌ AuthService: Error loading token: $e');
    }
  }

  /// Save token to both memory cache and storage
  Future<void> saveToken(String accessToken, String refreshToken) async {
    try {
      // Save to memory cache first
      _cachedToken = accessToken;
      _cachedRefreshToken = refreshToken;
      
      // Then persist to storage
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', accessToken);
      await prefs.setString('refresh_token', refreshToken);
      
      print('✅ AuthService: Token saved to memory and storage');
    } catch (e) {
      print('❌ AuthService: Error saving token: $e');
    }
  }

  /// Get access token (from memory cache or storage)
  Future<String?> getAccessToken() async {
    // Try memory cache first (fastest and survives app pause)
    if (_cachedToken != null && _cachedToken!.isNotEmpty) {
      print('✅ AuthService: Token from memory cache');
      return _cachedToken;
    }

    // Fallback to storage
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('access_token');
      if (token != null && token.isNotEmpty) {
        _cachedToken = token; // Update cache
        print('✅ AuthService: Token from storage, cached');
        return token;
      }
    } catch (e) {
      print('❌ AuthService: Error reading token: $e');
    }

    print('❌ AuthService: No token available');
    return null;
  }

  /// Get refresh token
  Future<String?> getRefreshToken() async {
    if (_cachedRefreshToken != null && _cachedRefreshToken!.isNotEmpty) {
      return _cachedRefreshToken;
    }

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('refresh_token');
      if (token != null) {
        _cachedRefreshToken = token;
        return token;
      }
    } catch (e) {
      print('❌ AuthService: Error reading refresh token: $e');
    }

    return null;
  }

  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  /// Clear token from memory and storage
  Future<void> clearToken() async {
    _cachedToken = null;
    _cachedRefreshToken = null;

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('access_token');
      await prefs.remove('refresh_token');
      print('✅ AuthService: Token cleared');
    } catch (e) {
      print('❌ AuthService: Error clearing token: $e');
    }
  }

  /// Restore token after app lifecycle change (e.g., camera activity)
  Future<void> restoreToken() async {
    if (_cachedToken != null && _cachedToken!.isNotEmpty) {
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access_token', _cachedToken!);
        if (_cachedRefreshToken != null) {
          await prefs.setString('refresh_token', _cachedRefreshToken!);
        }
        print('✅ AuthService: Token restored to storage from memory');
      } catch (e) {
        print('❌ AuthService: Error restoring token: $e');
      }
    }
  }

  /// Get cached token directly (for quick checks)
  String? get cachedToken => _cachedToken;

  /// Check if token exists in memory cache
  bool get hasTokenInCache => _cachedToken != null && _cachedToken!.isNotEmpty;
}
