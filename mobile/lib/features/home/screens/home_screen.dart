import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cirp/core/theme/app_theme.dart';
import 'package:cirp/core/routes/app_routes.dart';
import 'package:cirp/generated/app_localizations.dart';
import 'package:cirp/features/reports/screens/report_details_screen.dart';
import 'package:cirp/shared/widgets/status_badge.dart';
import 'package:cirp/core/storage/local_auth_service.dart';
import 'package:cirp/core/storage/local_reports_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _userName = 'User';
  List<dynamic> _recentReports = [];
  List<dynamic> _categories = [];
  bool _isLoading = true;
  int _unreadNotifications = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      // Get current user from local storage
      final currentUser = await LocalAuthService.getCurrentUser();
      
      String formattedName = currentUser?['full_name'] ?? 'User';
      if (formattedName.contains(' ')) {
        formattedName = formattedName.split(' ').first;
      }

      // Get recent reports from local storage
      final userId = currentUser?['id'] ?? '1';
      final reports = await LocalReportsService.getRecentReports(userId);
      
      setState(() {
        _userName = formattedName;
        _recentReports = reports.map((r) => {
          'id': r['id'],
          'title': r['description']?.toString().split('\n').first ?? 'Untitled',
          'status': r['status'],
          'category': {'name': r['category']},
          'address': r['location'],
          'created_at': r['created_at'],
        }).toList();
        _categories = [
          {'id': 1, 'name': 'Road Damage'},
          {'id': 2, 'name': 'Water Leakage'},
          {'id': 3, 'name': 'Garbage'},
          {'id': 4, 'name': 'Streetlight'},
          {'id': 5, 'name': 'Drainage'},
          {'id': 6, 'name': 'Other'},
        ];
        _unreadNotifications = 0; // Mock notification count
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading home data: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Color(0xFF2E7D32),
        body: Center(
          child: CircularProgressIndicator(color: Colors.white),
        ),
      );
    }
    
    return Scaffold(
      backgroundColor: Color(0xFFF5F5F5),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: CustomScrollView(
          slivers: [
            _buildHeader(context),
            SliverToBoxAdapter(
              child: Column(
                children: [
                  _buildCategoriesSection(context),
                  _buildRecentIssuesSection(context),
                  const SizedBox(height: 100),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return SliverToBoxAdapter(
      child: Stack(
        children: [
          // Green curved header with city silhouette
          ClipPath(
            clipper: _HeaderClipper(),
            child: Container(
              height: 200,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFF2E7D32), Color(0xFF43A047)],
                ),
              ),
              child: Stack(
                children: [
                  // City silhouette at bottom
                  Positioned(
                    bottom: 0,
                    left: 0,
                    right: 0,
                    child: Container(
                      height: 80,
                      child: CustomPaint(
                        painter: _CitySilhouettePainter(),
                        size: Size.infinite,
                      ),
                    ),
                  ),
                  // Content
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 50, 20, 20),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Hello, $_userName 👋',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 28,
                                  fontWeight: FontWeight.w700,
                                  height: 1.2,
                                ),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                "Let's make our community\nbetter together",
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 14,
                                  height: 1.4,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Row(
                          children: [
                            Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: IconButton(
                                icon: const Icon(Icons.search, color: Colors.white, size: 22),
                                onPressed: () {},
                                padding: EdgeInsets.zero,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Stack(
                              children: [
                                Container(
                                  width: 40,
                                  height: 40,
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: IconButton(
                                    icon: const Icon(Icons.notifications_outlined, color: Colors.white, size: 22),
                                    onPressed: () => Navigator.pushNamed(context, AppRoutes.notifications),
                                    padding: EdgeInsets.zero,
                                  ),
                                ),
                                if (_unreadNotifications > 0)
                                  Positioned(
                                    right: 6,
                                    top: 6,
                                    child: Container(
                                      width: 8,
                                      height: 8,
                                      decoration: const BoxDecoration(
                                        color: Color(0xFFFF5252),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoriesSection(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(
        color: Color(0xFFF5F5F5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Report Category',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w700,
              color: Color(0xFF212121),
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Select the type of issue',
            style: TextStyle(
              fontSize: 14,
              color: Color(0xFF9E9E9E),
            ),
          ),
          const SizedBox(height: 24),
          _buildCategoryGrid(),
        ],
      ),
    );
  }

  Widget _buildCategoryGrid() {
    // Category data with exact colors and icons from the image
    final categories = [
      {
        'name': 'Road Damage',
        'icon': '🛣️',
        'bgColor': Color(0xFFFFEBEE),
        'iconBg': Color(0xFFFFCDD2),
        'iconColor': Color(0xFFD32F2F),
        'arrowColor': Color(0xFFEF5350),
      },
      {
        'name': 'Water Leakage',
        'icon': '💧',
        'bgColor': Color(0xFFE3F2FD),
        'iconBg': Color(0xFFBBDEFB),
        'iconColor': Color(0xFF1976D2),
        'arrowColor': Color(0xFF42A5F5),
      },
      {
        'name': 'Garbage',
        'icon': '🗑️',
        'bgColor': Color(0xFFFFF3E0),
        'iconBg': Color(0xFFFFE0B2),
        'iconColor': Color(0xFFF57C00),
        'arrowColor': Color(0xFFFF9800),
      },
      {
        'name': 'Streetlight',
        'icon': '💡',
        'bgColor': Color(0xFFF1F8E9),
        'iconBg': Color(0xFFDCEDC8),
        'iconColor': Color(0xFF689F38),
        'arrowColor': Color(0xFF8BC34A),
      },
      {
        'name': 'Drainage',
        'icon': '🌊',
        'bgColor': Color(0xFFE0F7FA),
        'iconBg': Color(0xFFB2EBF2),
        'iconColor': Color(0xFF0097A7),
        'arrowColor': Color(0xFF00BCD4),
      },
      {
        'name': 'Other',
        'icon': '⋯',
        'bgColor': Color(0xFFF3E5F5),
        'iconBg': Color(0xFFE1BEE7),
        'iconColor': Color(0xFF7B1FA2),
        'arrowColor': Color(0xFF9C27B0),
      },
    ];
    
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.15,
      ),
      itemCount: categories.length,
      itemBuilder: (context, index) {
        final category = categories[index];
        
        return GestureDetector(
          onTap: () => Navigator.pushNamed(
            context,
            AppRoutes.reportProblem,
            arguments: {'category': {'name': category['name']}},
          ),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: category['bgColor'] as Color,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Stack(
              children: [
                // Decorative curve at bottom right
                Positioned(
                  bottom: -8,
                  right: -8,
                  child: Container(
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.3),
                      borderRadius: BorderRadius.circular(25),
                    ),
                  ),
                ),
                // Content
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Icon
                    Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        color: category['iconBg'] as Color,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Center(
                        child: Text(
                          category['icon'] as String,
                          style: const TextStyle(fontSize: 26),
                        ),
                      ),
                    ),
                    const Spacer(),
                    // Title
                    Text(
                      category['name'] as String,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF212121),
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 6),
                    // Arrow button
                    Align(
                      alignment: Alignment.centerRight,
                      child: Container(
                        width: 28,
                        height: 28,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.7),
                          borderRadius: BorderRadius.circular(7),
                        ),
                        child: Icon(
                          Icons.arrow_forward,
                          size: 16,
                          color: category['arrowColor'] as Color,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildRecentIssuesSection(BuildContext context) {
    return Container(
      color: Color(0xFFF5F5F5),
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Recent Issues',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF212121),
                ),
              ),
              GestureDetector(
                onTap: () => Navigator.pushNamed(context, AppRoutes.myReports),
                child: const Text(
                  'See All',
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFF2E7D32),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (_recentReports.isEmpty)
            const Padding(
              padding: EdgeInsets.all(40),
              child: Text(
                'No recent issues',
                style: TextStyle(
                  color: Color(0xFF9E9E9E),
                  fontSize: 14,
                ),
              ),
            )
          else
            Column(
              children: _recentReports.take(5).map((report) => _IssueCard(
                report: report,
                onTap: () async {
                  final reloaded = await Navigator.push<bool>(
                    context,
                    MaterialPageRoute(
                      builder: (_) => ReportDetailsScreen(report: report),
                    ),
                  );
                  if (reloaded == true) {
                    _loadData();
                  }
                },
              )).toList(),
            ),
        ],
      ),
    );
  }
}

class _CategoryCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _CategoryCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(height: 10),
            Text(
              label,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

class _IssueCard extends StatelessWidget {
  final Map<String, dynamic> report;
  final VoidCallback onTap;

  const _IssueCard({
    required this.report,
    required this.onTap,
  });

  Color _getStatusColor(String status) {
    final s = status.toLowerCase();
    if (s.contains('resolved') || s.contains('completed')) return AppColors.green;
    if (s.contains('assigned') || s.contains('progress')) return AppColors.orange;
    if (s.contains('review')) return AppColors.blue;
    if (s.contains('rejected')) return AppColors.red;
    return AppColors.textSecondary;
  }

  IconData _getCategoryIcon(String? category) {
    if (category == null) return Icons.report_outlined;
    final cat = category.toLowerCase();
    if (cat.contains('water')) return Icons.water_drop_outlined;
    if (cat.contains('street')) return Icons.lightbulb_outline;
    if (cat.contains('pothole') || cat.contains('road')) return Icons.build_outlined;
    return Icons.report_outlined;
  }

  @override
  Widget build(BuildContext context) {
    final status = report['status'] ?? 'pending';
    final title = report['title'] ?? 'Untitled Issue';
    final category = report['category']?['name'];
    final address = report['address'] ?? '';
    final createdAt = report['created_at'] ?? '';
    
    // Format time (e.g., "Reported 6pm")
    String timeText = 'Recently';
    if (createdAt.isNotEmpty) {
      try {
        final date = DateTime.parse(createdAt);
        final hour = date.hour;
        final ampm = hour >= 12 ? 'pm' : 'am';
        final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
        timeText = 'Reported $displayHour$ampm';
      } catch (e) {
        timeText = 'Recently';
      }
    }
    
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 14),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey.shade200),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.03),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: _getStatusColor(status).withOpacity(0.12),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                _getCategoryIcon(category),
                color: _getStatusColor(status),
                size: 28,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${category ?? 'Issue'} · $timeText',
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  if (address.isNotEmpty)
                    Text(
                      '${address.split(',').first}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade500,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            const SizedBox(width: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: _getStatusColor(status).withOpacity(0.12),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                _getStatusLabel(status),
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: _getStatusColor(status),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getStatusLabel(String status) {
    final s = status.toLowerCase();
    if (s.contains('assigned') || s.contains('progress')) return 'Assigned';
    if (s.contains('resolved') || s.contains('completed')) return 'Resolved';
    if (s.contains('review')) return 'Review';
    if (s.contains('rejected')) return 'Rejected';
    return 'Pending';
  }
}

// Header clipper for smooth curved bottom
class _HeaderClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final path = Path();
    path.lineTo(0, size.height - 40);
    
    // Create smooth curve
    path.quadraticBezierTo(
      size.width * 0.5,
      size.height,
      size.width,
      size.height - 40,
    );
    
    path.lineTo(size.width, 0);
    path.close();
    return path;
  }

  @override
  bool shouldReclip(CustomClipper<Path> oldClipper) => false;
}

// City silhouette painter
class _CitySilhouettePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.15)
      ..style = PaintingStyle.fill;

    final path = Path();
    
    // Start from bottom left
    path.moveTo(0, size.height);
    
    // Building 1 (left side - short)
    path.lineTo(0, size.height - 30);
    path.lineTo(size.width * 0.12, size.height - 30);
    path.lineTo(size.width * 0.12, size.height);
    
    // Building 2 (tall building)
    path.moveTo(size.width * 0.15, size.height);
    path.lineTo(size.width * 0.15, size.height - 50);
    path.lineTo(size.width * 0.28, size.height - 50);
    path.lineTo(size.width * 0.28, size.height);
    
    // Building 3 (medium)
    path.moveTo(size.width * 0.32, size.height);
    path.lineTo(size.width * 0.32, size.height - 40);
    path.lineTo(size.width * 0.42, size.height - 40);
    path.lineTo(size.width * 0.42, size.height);
    
    // Building 4 (very tall - center)
    path.moveTo(size.width * 0.45, size.height);
    path.lineTo(size.width * 0.45, size.height - 60);
    path.lineTo(size.width * 0.55, size.height - 60);
    path.lineTo(size.width * 0.55, size.height);
    
    // Building 5 (tall)
    path.moveTo(size.width * 0.58, size.height);
    path.lineTo(size.width * 0.58, size.height - 55);
    path.lineTo(size.width * 0.68, size.height - 55);
    path.lineTo(size.width * 0.68, size.height);
    
    // Tree 1
    path.moveTo(size.width * 0.72, size.height);
    path.lineTo(size.width * 0.74, size.height - 20);
    path.lineTo(size.width * 0.73, size.height - 35);
    path.lineTo(size.width * 0.75, size.height - 30);
    path.lineTo(size.width * 0.77, size.height - 35);
    path.lineTo(size.width * 0.76, size.height - 20);
    path.lineTo(size.width * 0.78, size.height);
    
    // Building 6 (right side)
    path.moveTo(size.width * 0.82, size.height);
    path.lineTo(size.width * 0.82, size.height - 45);
    path.lineTo(size.width * 0.92, size.height - 45);
    path.lineTo(size.width * 0.92, size.height);
    
    // Tree 2
    path.moveTo(size.width * 0.94, size.height);
    path.lineTo(size.width * 0.95, size.height - 15);
    path.lineTo(size.width * 0.94, size.height - 28);
    path.lineTo(size.width * 0.96, size.height - 25);
    path.lineTo(size.width * 0.98, size.height - 28);
    path.lineTo(size.width * 0.97, size.height - 15);
    path.lineTo(size.width * 0.98, size.height);
    
    path.lineTo(size.width, size.height);
    path.close();
    
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
