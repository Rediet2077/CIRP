import 'package:cirp/core/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Amharic and Tigrinya text falls back to the bundled Ethiopic font',
      (tester) async {
    late TextStyle resolved;
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: Builder(builder: (context) {
            resolved = DefaultTextStyle.of(context).style;
            return const Text('አማርኛ ትግርኛ');
          }),
        ),
      ),
    );

    expect(resolved.fontFamilyFallback, contains('NotoSansEthiopic'));
    expect(AppTheme.lightTheme.textTheme.bodyMedium?.fontFamilyFallback,
        contains('NotoSansEthiopic'));
  });

  testWidgets('button text also falls back to the Ethiopic font', (tester) async {
    List<String>? buttonFallback;
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: ElevatedButton(
            onPressed: () {},
            child: Builder(builder: (context) {
              buttonFallback = DefaultTextStyle.of(context).style.fontFamilyFallback;
              return const Text('እቶ');
            }),
          ),
        ),
      ),
    );

    expect(buttonFallback, contains('NotoSansEthiopic'));
  });
}
