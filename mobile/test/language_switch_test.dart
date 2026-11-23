import 'package:cirp/core/localization/fallback_material_localizations.dart';
import 'package:cirp/core/theme/app_theme.dart';
import 'package:cirp/features/auth/screens/login_screen.dart';
import 'package:cirp/features/auth/screens/register_screen.dart';
import 'package:cirp/features/language/language_provider.dart';
import 'package:cirp/generated/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<void> _pumpApp(WidgetTester tester, {Widget home = const RegisterScreen()}) async {
  SharedPreferences.setMockInitialValues({});
  tester.view.physicalSize = const Size(800, 2400);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(
    ChangeNotifierProvider(
      create: (_) => LanguageProvider(),
      child: Consumer<LanguageProvider>(
        builder: (context, lang, _) => MaterialApp(
          theme: AppTheme.lightTheme,
          locale: Locale(lang.languageCode),
          localizationsDelegates: const [
            AppLocalizations.delegate,
            FallbackMaterialLocalizationsDelegate(),
            FallbackCupertinoLocalizationsDelegate(),
            FallbackWidgetsLocalizationsDelegate(),
          ],
          supportedLocales: const [Locale('en'), Locale('am'), Locale('or'), Locale('ti')],
          home: home,
        ),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  const createAccount = {
    'am': 'መለያ ፍጠሩ',
    'or': 'Herreega Uumi',
    'ti': 'ሕሳብ ፍጠር',
  };
  for (final entry in {
    'አማርኛ': 'am',
    'Afaan Oromoo': 'or',
    'ትግርኛ': 'ti',
  }.entries) {
    testWidgets('tapping ${entry.value} switches the language', (tester) async {
      await _pumpApp(tester);
      expect(find.text('Create Account'), findsWidgets);

      await tester.tap(find.text(entry.key));
      await tester.pumpAndSettle();

      final ctx = tester.element(find.byType(RegisterScreen));
      expect(Provider.of<LanguageProvider>(ctx, listen: false).languageCode, entry.value);
      expect(tester.takeException(), isNull);
      // The screen's own text changed language
      expect(find.text('Create Account'), findsNothing);
      expect(find.text(createAccount[entry.value]!), findsWidgets);
    });
  }

  testWidgets('login screen follows the selected language', (tester) async {
    await _pumpApp(tester, home: const LoginScreen());
    expect(find.text('Log In'), findsWidgets);

    final ctx = tester.element(find.byType(LoginScreen));
    await Provider.of<LanguageProvider>(ctx, listen: false).setLanguage('ti');
    await tester.pumpAndSettle();

    expect(find.text('Log In'), findsNothing);
    expect(find.text('እቶ'), findsWidgets); // Tigrinya "logIn"
  });
}
