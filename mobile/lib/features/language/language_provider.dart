import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LanguageProvider extends ChangeNotifier {
  static const _prefKey = 'selected_language_code';

  String _languageCode = 'en';

  // Supported languages (Material Design has built-in support)
  static const List<String> _supportedLanguages = ['en', 'am'];

  LanguageProvider() {
    _loadSaved();
  }

  String get languageCode => _languageCode;

  Locale get locale => Locale(_languageCode);

  Future<void> setLanguage(String code) async {
    // Force to English if language not supported
    if (!_supportedLanguages.contains(code)) {
      code = 'en';
    }
    
    if (_languageCode == code) return;
    _languageCode = code;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefKey, code);
  }

  Future<void> _loadSaved() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_prefKey);
    
    // Force to English if saved language not supported
    if (saved != null && _supportedLanguages.contains(saved) && saved != _languageCode) {
      _languageCode = saved;
      notifyListeners();
    } else if (saved != null && !_supportedLanguages.contains(saved)) {
      // Reset to English if unsupported language was saved
      _languageCode = 'en';
      notifyListeners();
      await prefs.setString(_prefKey, 'en');
    }
  }

  String currentLanguageName() {
    switch (_languageCode) {
      case 'am':
        return 'Amharic';
      default:
        return 'English';
    }
  }

  List<Map<String, String>> get languageOptions => [
        {'code': 'en', 'name': 'English', 'icon': 'EN'},
        {'code': 'am', 'name': 'Amharic', 'icon': 'AM'},
        // Oromo and Tigrinya removed - Material Design doesn't support them yet
        // You can still process reports in these languages on backend
      ];
}
