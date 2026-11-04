import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'core/theme/app_theme.dart';
import 'core/routes/app_routes.dart';
import 'features/splash/splash_screen.dart';
import 'features/language/language_provider.dart';
import 'generated/app_localizations.dart';
import 'core/localization/fallback_material_localizations.dart';
import 'core/services/auth_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize global AuthService to keep token in memory
  await AuthService().initialize();
  
  runApp(const CirpApp());
}

class CirpApp extends StatelessWidget {
  const CirpApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => LanguageProvider(),
      child: Consumer<LanguageProvider>(
        builder: (context, langProvider, _) {
          return MaterialApp(
            title: 'CIRP - Community Issue Reporting Platform',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            locale: Locale(langProvider.languageCode),
            localizationsDelegates: const [
              AppLocalizations.delegate,
              FallbackMaterialLocalizationsDelegate(),
              FallbackCupertinoLocalizationsDelegate(),
              FallbackWidgetsLocalizationsDelegate(),
            ],
            supportedLocales: const [
              Locale('en'),
              Locale('am'),
              Locale('or'),
              Locale('ti'),
            ],
            routes: AppRoutes.routes,
            onGenerateRoute: AppRoutes.onGenerateRoute,
            home: const SplashScreen(),
          );
        },
      ),
    );
  }
}
