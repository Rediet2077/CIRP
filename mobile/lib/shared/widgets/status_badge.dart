import 'package:flutter/material.dart';
import 'package:cirp/core/theme/app_theme.dart';

class StatusBadge extends StatelessWidget {
  final String status;
  final bool small;

  const StatusBadge({super.key, required this.status, this.small = false});

  /// "IN_PROGRESS" -> "in progress"
  String get _key => status.toLowerCase().replaceAll('_', ' ').trim();

  String get _label {
    switch (_key) {
      case 'new':
      case 'pending':
      case 'submitted':
        return 'Submitted';
      case 'accepted':
      case 'assigned':
      case 'under review':
        return 'Under Review';
      case 'in progress':
        return 'In Progress';
      case 'completed pending verification':
        return 'Awaiting Verification';
      case 'resolved':
        return 'Resolved';
      case 'rejected':
      case 'disputed':
        return 'Rejected';
      default:
        return status;
    }
  }

  Color get _color {
    switch (_key) {
      case 'in progress':
      case 'completed pending verification':
        return AppColors.inProgress;
      case 'under review':
      case 'accepted':
      case 'assigned':
        return AppColors.underReview;
      case 'resolved':
        return AppColors.resolved;
      case 'rejected':
      case 'disputed':
        return AppColors.rejected;
      case 'new':
      case 'pending':
      case 'submitted':
        return AppColors.textSecondary;
      case 'assigned to contractor':
        return AppColors.purple;
      case 'completed':
        return AppColors.resolved;
      case 'confirmed':
        return AppColors.green;
      default:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final dotSize = small ? 6.0 : 7.0;
    final fontSize = small ? 10.0 : 12.0;
    final hPad = small ? 7.0 : 10.0;
    final vPad = small ? 2.0 : 4.0;

    return Container(
      padding: EdgeInsets.symmetric(horizontal: hPad, vertical: vPad),
      decoration: BoxDecoration(
        color: _color.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: dotSize,
            height: dotSize,
            decoration: BoxDecoration(
              color: _color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 5),
          Text(
            _label,
            style: TextStyle(
              color: _color,
              fontSize: fontSize,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
