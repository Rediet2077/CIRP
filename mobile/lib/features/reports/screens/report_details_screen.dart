import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:cirp/core/theme/app_theme.dart';
import 'package:cirp/generated/app_localizations.dart';
import 'package:cirp/shared/widgets/status_badge.dart';
import 'package:cirp/core/services/api_service.dart';
import 'package:cirp/core/constants/api_constants.dart';

class ReportDetailsScreen extends StatefulWidget {
  final Map<String, dynamic>? report;
  final String? reportId;

  const ReportDetailsScreen({
    super.key,
    this.report,
    this.reportId,
  });

  @override
  State<ReportDetailsScreen> createState() => _ReportDetailsScreenState();
}

class _ReportDetailsScreenState extends State<ReportDetailsScreen> {
  Map<String, dynamic>? _reportData;
  bool _isLoading = false;
  Timer? _refreshTimer;

  String? get _reportId {
    final id = widget.reportId ?? widget.report?['id']?.toString();
    return (id != null && id.isNotEmpty) ? id : null;
  }

  @override
  void initState() {
    super.initState();
    _reportData = widget.report;
    final id = _reportId;
    if (id != null) {
      _fetchDetails(id);
      // Keep the timeline current while the citizen has this screen open
      _refreshTimer = Timer.periodic(
        const Duration(seconds: 20),
        (_) => _fetchDetails(id),
      );
    }
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchDetails(String id) async {
    if (_reportData == null) {
      setState(() => _isLoading = true);
    }
    final result = await ApiService.getReportDetails(id);
    if (!mounted) return;
    if (result['success'] == true && result['data'] is Map) {
      setState(() {
        _reportData = Map<String, dynamic>.from(result['data'] as Map);
        _isLoading = false;
      });
    } else {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _deleteReport() async {
    final reportId = (_reportData?['id'] ?? widget.reportId ?? '').toString();
    if (reportId.isEmpty) return;

    final confirm = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: const Text('Remove Report'),
        content: const Text('Are you sure you want to remove this resolved report from your history?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx, rootNavigator: true).pop(false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx, rootNavigator: true).pop(true),
            style: FilledButton.styleFrom(backgroundColor: AppColors.red),
            child: const Text('Remove'),
          ),
        ],
      ),
    );

    if (confirm == true && mounted) {
      final res = await ApiService.deleteReport(reportId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(res['message'] ?? 'Report removed'),
            backgroundColor: res['success'] == true ? AppColors.primary : AppColors.red,
          ),
        );
        Navigator.pop(context, true); // Return true so parent screen reloads list
      }
    }
  }

  String _formatDate(String? rawDate) {
    if (rawDate == null || rawDate.isEmpty) return '';
    try {
      // "2026-11-23 19:38:00" is UTC; mark it so toLocal() converts correctly
      final isNaiveUtc =
          RegExp(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$').hasMatch(rawDate.trim());
      final dt = DateTime.parse(isNaiveUtc ? '${rawDate.trim().replaceFirst(' ', 'T')}Z' : rawDate).toLocal();
      return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return rawDate.split('T')[0];
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final data = _reportData ?? {};
    final statusRaw = (data['status'] as String? ?? 'SUBMITTED').toUpperCase();
    final isResolved = statusRaw == 'RESOLVED';
    final isRejected = statusRaw == 'REJECTED';
    final progress = data['progress'] is Map
        ? Map<String, dynamic>.from(data['progress'] as Map)
        : null;
    final taskStatus = (progress?['task_status'] as String? ?? '').toUpperCase();
    final percentage = ((progress?['percentage'] as num?) ?? 0).toInt().clamp(0, 100);
    final updates = (progress?['updates'] as List?) ?? const [];
    final awaitingVerification = taskStatus == 'COMPLETED_PENDING_VERIFICATION' && !isResolved;
    final isReturned = taskStatus == 'RETURNED' && !isResolved;
    final isInProgress = !awaitingVerification &&
        !isResolved &&
        (statusRaw == 'IN_PROGRESS' ||
            statusRaw == 'IN PROGRESS' ||
            taskStatus == 'IN_PROGRESS' ||
            isReturned);
    final isAccepted = statusRaw == 'ACCEPTED' ||
        statusRaw == 'ASSIGNED' ||
        progress != null ||
        isInProgress ||
        awaitingVerification ||
        isResolved;
    final assignedTo = progress?['assigned_to']?.toString() ?? '';
    final deadline = progress?['deadline_date']?.toString() ?? '';
    final shownStatus = awaitingVerification ? 'COMPLETED_PENDING_VERIFICATION' : statusRaw;

    final title = data['title'] ?? 'Infrastructure Issue';
    final reportNo = data['report_number'] ?? (data['id'] != null ? '#${data['id'].toString().substring(0, 8)}' : '#---');
    final dateStr = _formatDate(data['created_at']);
    final desc = data['description'] ?? 'No description provided';
    final address = data['address'] ?? '';
    final completionNotes = data['completion_notes'] ?? data['admin_feedback'] ?? '';

    // Extract photo URL if available
    String? photoUrl;
    if (data['media'] != null && (data['media'] as List).isNotEmpty) {
      final m = (data['media'] as List).first;
      final fileStr = m['file'] ?? m['file_url'];
      if (fileStr != null && fileStr.toString().isNotEmpty) {
        final f = fileStr.toString();
        if (f.startsWith('http') || f.startsWith('data:')) {
          photoUrl = f;
        } else {
          photoUrl = '${ApiConstants.baseUrl}${f.startsWith('/') ? '' : '/'}$f';
        }
      }
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(l10n.reportDetails),
        backgroundColor: AppColors.white,
        elevation: 0,
        actions: [
          if (isResolved)
            IconButton(
              icon: const Icon(Icons.delete_outline, color: AppColors.red),
              tooltip: 'Remove Report',
              onPressed: _deleteReport,
            ),
        ],
      ),
      body: _isLoading && _reportData == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () async {
                final id = _reportId;
                if (id != null) await _fetchDetails(id);
              },
              child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      StatusBadge(status: shownStatus),
                      if (data['priority'] != null)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.orange.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            '${data['priority']} PRIORITY',
                            style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: AppColors.orange,
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Report ID: $reportNo  •  $dateStr',
                    style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                  ),
                  if (address.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        const Icon(Icons.location_on_outlined, size: 14, color: AppColors.textSecondary),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Text(
                            address,
                            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ],
                  const SizedBox(height: 16),

                  // Description card
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppColors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Description',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          desc,
                          style: const TextStyle(
                            fontSize: 14,
                            color: AppColors.textPrimary,
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Image Evidence Box
                  if (photoUrl != null)
                    Container(
                      height: 200,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(14),
                        color: Colors.black,
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(14),
                        child: Image.network(
                          photoUrl,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => const Center(
                            child: Icon(Icons.broken_image, size: 40, color: Colors.white54),
                          ),
                        ),
                      ),
                    ),

                  const SizedBox(height: 24),
                  Text(
                    l10n.progressTimeline,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Dynamic Progress Timeline Steps (driven by the admin's work order)
                  _TimelineItem(
                    label: 'Report Submitted',
                    time: dateStr,
                    color: AppColors.primary,
                    isCompleted: true,
                  ),
                  _TimelineItem(
                    label: isAccepted ? 'Accepted & Assigned' : 'Under Review / Triage',
                    time: isAccepted
                        ? _formatDate(progress?['accepted_at']?.toString() ?? data['updated_at']?.toString())
                        : '',
                    detail: isAccepted && assignedTo.isNotEmpty
                        ? 'Assigned to $assignedTo${deadline.isNotEmpty ? ' · Expected by $deadline' : ''}'
                        : null,
                    color: isAccepted ? AppColors.underReview : AppColors.textHint,
                    isCompleted: isAccepted,
                    isPending: !isAccepted,
                  ),
                  _TimelineItem(
                    label: 'Work In Progress',
                    time: (isInProgress || awaitingVerification || isResolved)
                        ? _formatDate(data['updated_at']?.toString())
                        : '',
                    detail: isReturned
                        ? 'Sent back for correction · $percentage% complete'
                        : (isInProgress ? '$percentage% complete' : null),
                    color: (isInProgress || awaitingVerification || isResolved)
                        ? (isInProgress ? AppColors.inProgress : AppColors.primary)
                        : AppColors.textHint,
                    isActive: isInProgress,
                    isCompleted: awaitingVerification || isResolved,
                    isPending: !isInProgress && !awaitingVerification && !isResolved,
                  ),
                  _TimelineItem(
                    label: isRejected
                        ? 'Rejected'
                        : (awaitingVerification ? 'Awaiting Final Verification' : 'Resolved & Completed'),
                    time: isResolved
                        ? _formatDate((data['resolved_at'] ?? data['updated_at'])?.toString())
                        : '',
                    color: isResolved
                        ? AppColors.resolved
                        : (isRejected
                            ? AppColors.red
                            : (awaitingVerification ? AppColors.inProgress : AppColors.textHint)),
                    isCompleted: isResolved,
                    isActive: awaitingVerification,
                    isPending: !isResolved && !isRejected && !awaitingVerification,
                    isLast: true,
                  ),

                  // Overall progress and the latest messages from the municipality
                  if (progress != null) ...[
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: AppColors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppColors.border),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Repair progress',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                              Text(
                                '${isResolved ? 100 : percentage}%',
                                style: const TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.primary,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(6),
                            child: LinearProgressIndicator(
                              value: (isResolved ? 100 : percentage) / 100,
                              minHeight: 8,
                              backgroundColor: AppColors.border,
                              color: isResolved ? AppColors.resolved : AppColors.inProgress,
                            ),
                          ),
                          if (updates.isNotEmpty) ...[
                            const SizedBox(height: 14),
                            const Text(
                              'Latest updates',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                color: AppColors.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 8),
                            for (final u in updates)
                              if (u is Map)
                                Padding(
                                  padding: const EdgeInsets.only(bottom: 10),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        (u['note'] ?? '').toString(),
                                        style: const TextStyle(
                                          fontSize: 13,
                                          color: AppColors.textPrimary,
                                          height: 1.35,
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        '${_formatDate(u['timestamp']?.toString())} · ${(u['percentage'] ?? 0)}%',
                                        style: const TextStyle(
                                          fontSize: 11,
                                          color: AppColors.textSecondary,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                          ],
                        ],
                      ),
                    ),
                  ],

                  // Resolution / Admin Feedback Box
                  if (completionNotes.toString().isNotEmpty) ...[
                    const SizedBox(height: 20),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: isResolved ? AppColors.resolved.withValues(alpha: 0.1) : AppColors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isResolved ? AppColors.resolved.withValues(alpha: 0.4) : AppColors.border,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                isResolved ? Icons.check_circle_outline : Icons.info_outline,
                                size: 18,
                                color: isResolved ? AppColors.resolved : AppColors.textPrimary,
                              ),
                              const SizedBox(width: 6),
                              Text(
                                isResolved ? 'Resolution Update' : 'Admin Notes',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: isResolved ? AppColors.resolved : AppColors.textPrimary,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            completionNotes.toString(),
                            style: const TextStyle(
                              fontSize: 13,
                              color: AppColors.textPrimary,
                              height: 1.4,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],

                  // Remove Button for Resolved Reports
                  if (isResolved) ...[
                    const SizedBox(height: 28),
                    FilledButton.icon(
                      onPressed: _deleteReport,
                      icon: const Icon(Icons.delete_outline, size: 20),
                      label: const Text('Remove Report from History'),
                      style: FilledButton.styleFrom(
                        minimumSize: const Size(double.infinity, 50),
                        backgroundColor: AppColors.red,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            ),
    );
  }
}

class _TimelineItem extends StatelessWidget {
  final String label;
  final String time;
  final String? detail;
  final Color color;
  final bool isCompleted;
  final bool isActive;
  final bool isPending;
  final bool isLast;

  const _TimelineItem({
    required this.label,
    required this.time,
    this.detail,
    required this.color,
    this.isCompleted = false,
    this.isActive = false,
    this.isPending = false,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 24,
            child: Column(
              children: [
                Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: isCompleted
                        ? color
                        : (isActive ? color.withValues(alpha: 0.15) : Colors.transparent),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: isPending ? AppColors.border : color,
                      width: 2,
                    ),
                  ),
                  child: isCompleted
                      ? const Icon(Icons.check, size: 12, color: Colors.white)
                      : (isActive
                          ? Center(
                              child: Container(
                                width: 8,
                                height: 8,
                                decoration: BoxDecoration(
                                  color: color,
                                  shape: BoxShape.circle,
                                ),
                              ),
                            )
                          : null),
                ),
                if (!isLast)
                  Expanded(
                    child: Container(
                      width: 2,
                      color: isCompleted ? color : AppColors.border,
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: isActive || isCompleted ? FontWeight.w700 : FontWeight.w500,
                      color: isPending ? AppColors.textHint : AppColors.textPrimary,
                    ),
                  ),
                  if (time.isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Text(
                      time,
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                  if (detail != null && detail!.isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Text(
                      detail!,
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
