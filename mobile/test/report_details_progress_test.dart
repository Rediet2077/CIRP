import 'package:cirp/features/reports/screens/report_details_screen.dart';
import 'package:cirp/generated/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Map<String, dynamic> _report({
  required String status,
  Map<String, dynamic>? progress,
}) =>
    {
      'title': 'Road Damage: Pothole',
      'description': 'Deep pothole near the junction',
      'address': 'Bole Road',
      'priority': 'MEDIUM',
      'created_at': '2026-11-23 19:38:00',
      'updated_at': '2026-11-23 20:10:00',
      'status': status,
      'progress': progress,
    };

Future<void> _show(WidgetTester tester, Map<String, dynamic> report) async {
  tester.view.physicalSize = const Size(800, 2400);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(
    MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: ReportDetailsScreen(report: report),
    ),
  );
  await tester.pump();
}

void main() {
  testWidgets('new report: only submitted, no progress card', (tester) async {
    await _show(tester, _report(status: 'NEW'));

    expect(find.text('Submitted'), findsOneWidget); // status badge
    expect(find.text('Report Submitted'), findsOneWidget);
    expect(find.text('Under Review / Triage'), findsOneWidget);
    expect(find.text('Repair progress'), findsNothing);
  });

  testWidgets('accepted: shows who it was assigned to and the deadline', (tester) async {
    await _show(
      tester,
      _report(status: 'ACCEPTED', progress: {
        'task_status': 'ASSIGNED',
        'percentage': 0,
        'assigned_to': 'Blue Nile Civil Works',
        'accepted_at': '2026-11-23T20:00:00Z',
        'deadline_date': '2026-11-25',
        'updates': [],
      }),
    );

    expect(find.text('Under Review'), findsOneWidget); // status badge
    expect(find.text('Accepted & Assigned'), findsOneWidget);
    expect(
      find.text('Assigned to Blue Nile Civil Works · Expected by 2026-11-25'),
      findsOneWidget,
    );
    expect(find.text('Repair progress'), findsOneWidget);
    expect(find.text('0%'), findsOneWidget);
  });

  testWidgets('in progress: shows percentage and the admin update', (tester) async {
    await _show(
      tester,
      _report(status: 'IN_PROGRESS', progress: {
        'task_status': 'IN_PROGRESS',
        'percentage': 40,
        'assigned_to': 'Blue Nile Civil Works',
        'accepted_at': '2026-11-23T20:00:00Z',
        'deadline_date': '2026-11-25',
        'updates': [
          {
            'timestamp': '2026-11-23T21:00:00Z',
            'note': 'Crew on site, removing damaged asphalt.',
            'percentage': 40,
          },
        ],
      }),
    );

    expect(find.text('In Progress'), findsOneWidget);
    expect(find.text('40% complete'), findsOneWidget);
    expect(find.text('40%'), findsOneWidget);
    expect(find.text('Latest updates'), findsOneWidget);
    expect(find.text('Crew on site, removing damaged asphalt.'), findsOneWidget);
  });

  testWidgets('finished work: awaiting final verification', (tester) async {
    await _show(
      tester,
      _report(status: 'IN_PROGRESS', progress: {
        'task_status': 'COMPLETED_PENDING_VERIFICATION',
        'percentage': 100,
        'assigned_to': 'Blue Nile Civil Works',
        'accepted_at': '2026-11-23T20:00:00Z',
        'deadline_date': '2026-11-25',
        'updates': [],
      }),
    );

    expect(find.text('Awaiting Verification'), findsOneWidget); // status badge
    expect(find.text('Awaiting Final Verification'), findsOneWidget);
    expect(find.text('Resolved & Completed'), findsNothing);
    expect(find.text('100%'), findsOneWidget);
  });

  testWidgets('returned for correction is visible to the citizen', (tester) async {
    await _show(
      tester,
      _report(status: 'IN_PROGRESS', progress: {
        'task_status': 'RETURNED',
        'percentage': 90,
        'assigned_to': 'Blue Nile Civil Works',
        'accepted_at': '2026-11-23T20:00:00Z',
        'deadline_date': '2026-12-01',
        'updates': [],
      }),
    );

    expect(find.text('Sent back for correction · 90% complete'), findsOneWidget);
  });

  testWidgets('resolved: every step completed at 100%', (tester) async {
    await _show(
      tester,
      _report(status: 'RESOLVED', progress: {
        'task_status': 'RESOLVED',
        'percentage': 100,
        'assigned_to': 'Blue Nile Civil Works',
        'accepted_at': '2026-11-23T20:00:00Z',
        'deadline_date': '2026-11-25',
        'updates': [
          {
            'timestamp': '2026-11-23T22:00:00Z',
            'note': 'Resolved and verified. Road surface restored.',
            'percentage': 100,
          },
        ],
      }),
    );

    expect(find.text('Resolved'), findsOneWidget); // status badge
    expect(find.text('Resolved & Completed'), findsOneWidget);
    expect(find.text('100%'), findsOneWidget);
    expect(find.text('Resolved and verified. Road surface restored.'), findsOneWidget);
  });
}
