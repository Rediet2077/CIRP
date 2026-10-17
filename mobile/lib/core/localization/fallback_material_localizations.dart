import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

/// Fallback Material localizations delegate that uses English for unsupported locales
class FallbackMaterialLocalizationsDelegate extends LocalizationsDelegate<MaterialLocalizations> {
  const FallbackMaterialLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    // Support all locales by falling back to English for unsupported ones
    return true;
  }

  @override
  Future<MaterialLocalizations> load(Locale locale) async {
    // Tigrinya (ti) is not supported by GlobalMaterialLocalizations
    // For unsupported languages, fall back to English Material widgets
    if (locale.languageCode == 'ti') {
      return GlobalMaterialLocalizations.delegate.load(const Locale('en'));
    }
    
    // For all other languages (including or, am, en), use the built-in support
    return GlobalMaterialLocalizations.delegate.load(locale);
  }

  @override
  bool shouldReload(FallbackMaterialLocalizationsDelegate old) => false;
}

/// Fallback Cupertino localizations delegate
class FallbackCupertinoLocalizationsDelegate extends LocalizationsDelegate<CupertinoLocalizations> {
  const FallbackCupertinoLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => true;

  @override
  Future<CupertinoLocalizations> load(Locale locale) async {
    // Tigrinya (ti) is not supported
    if (locale.languageCode == 'ti') {
      return GlobalCupertinoLocalizations.delegate.load(const Locale('en'));
    }
    
    return GlobalCupertinoLocalizations.delegate.load(locale);
  }

  @override
  bool shouldReload(FallbackCupertinoLocalizationsDelegate old) => false;
}

/// Fallback Widgets localizations delegate
class FallbackWidgetsLocalizationsDelegate extends LocalizationsDelegate<WidgetsLocalizations> {
  const FallbackWidgetsLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => true;

  @override
  Future<WidgetsLocalizations> load(Locale locale) async {
    return GlobalWidgetsLocalizations.delegate.load(locale);
  }

  @override
  bool shouldReload(FallbackWidgetsLocalizationsDelegate old) => false;
}
