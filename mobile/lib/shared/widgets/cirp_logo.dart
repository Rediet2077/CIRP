import 'package:flutter/material.dart';
import 'package:cirp/core/theme/app_theme.dart';

class CirpLogo extends StatelessWidget {
  final double size;

  const CirpLogo({super.key, this.size = 90});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.primary,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 20,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'CIRP',
              style: TextStyle(
                fontSize: size * 0.24,
                fontWeight: FontWeight.w900,
                color: AppColors.white,
                letterSpacing: 2,
              ),
            ),
            Text(
              'Issue Reporter',
              style: TextStyle(
                fontSize: size * 0.12,
                fontWeight: FontWeight.w400,
                color: AppColors.white,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
