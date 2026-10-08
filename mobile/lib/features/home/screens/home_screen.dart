import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cirp/core/theme/app_theme.dart';
import 'package:cirp/core/routes/app_routes.dart';
import 'package:cirp/generated/app_localizations.dart';
import 'package:cirp/features/reports/screens/report_details_screen.dart';
import 'package:cirp/shared/widgets/status_badge.dart';
import 'package:cirp/core/services/api_service.dart';

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
      final prefs = await SharedPreferences.getInstance();
      final firstName = (prefs.getString('user_first_name') ?? '').trim();
      
      String formattedName = firstName.isNotEmpty ? firstName : 'User';

      // Fetch categories
      final categoriesResult = await ApiService.getCategories();
      
      // Fetch recent reports from API
      final reportsResult = await ApiService.getReports(pageSize: 10);
      
      // Fetch notifications to get unread count
      final notificationsResult = await ApiService.getNotifications();
      
      setState(() {
        _userName = formattedName;
        
        if (categoriesResult['success'] == true) {
          final data = categoriesResult['data'];
          // Handle both List and Map responses
          if (data is List) {
            _categories = data;
          } else if (data is Map) {
            _categories = [data]; // Wrap single object in list
          } else {
            _categories = [];
          }
        }
        
        if (reportsResult['success'] == true) {
          final data = reportsResult['data'];
          // Handle both List and Map responses
          if (data is List) {
            _recentReports = data;
          } else if (data is Map) {
            _recentReports = [data]; // Wrap single object in list
          } else {
            _recentReports = [];
          }
        }
        
        if (notificationsResult['success'] == true) {
          _unreadNotifications = notificationsResult['unread_count'] ?? 0;
        }
        
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
        backgroundColor: AppColors.primary,
        body: Center(
          child: CircularProgressIndicator(color: Colors.white),
        ),
      );
    }
    
    return RefreshIndicator(
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
    );
  }

  Widget _buildHeader(BuildContext context) {
    return SliverToBoxAdapter(
      child: Container(
        padding: const EdgeInsets.fromLTRB(20, 50, 20, 30),
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF2E7D32), Color(0xFF388E3C)],
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'Hello, $_userName 👋',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 26,
                            fontWeight: FontWeight.w800,
                            height: 1.2,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    "Let's make our community\nbetter together",
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 13,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.search, color: Colors.white, size: 26),
                  onPressed: () {},
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
                const SizedBox(width: 12),
                Stack(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.notifications_outlined, color: Colors.white, size: 26),
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.notifications),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                    if (_unreadNotifications > 0)
                      Positioned(
                        right: 0,
                        top: 0,
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                          ),
                          constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
                          child: Text(
                            _unreadNotifications > 9 ? '9+' : '$_unreadNotifications',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 8,
                              fontWeight: FontWeight.bold,
                            ),
                            textAlign: TextAlign.center,
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
    );
  }

  Widget _buildCategoriesSection(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 20),
      padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(30),
          topRight: Radius.circular(30),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Report Category',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Select the type of issue',
            style: TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 20),
          _buildCategoryGrid(),
        ],
      ),
    );
  }

  Widget _buildCategoryGrid() {
    // Default categories with icons
    final categoryIcons = {
      'streetlight': {'icon': Icons.lightbulb_outline, 'color': Color(0xFF4CAF50)},
      'water': {'icon': Icons.water_drop_outlined, 'color': Color(0xFF2196F3)},
      'damage': {'icon': Icons.warning_amber_outlined, 'color': Color(0xFFF44336)},
      'waste': {'icon': Icons.delete_outline, 'color': Color(0xFFFF9800)},
      'pothole': {'icon': Icons.build_outlined, 'color': Color(0xFF9C27B0)},
      'safety': {'icon': Icons.shield_outlined, 'color': Color(0xFFE91E63)},
    };

    // Fallback categories if API returns less than 6
    final fallbackCategories = [
      {'id': 1, 'name': 'Streetlight'},
      {'id': 2, 'name': 'No Water'},
      {'id': 3, 'name': 'Damage'},
      {'id': 4, 'name': 'Waste Mgt'},
      {'id': 5, 'name': 'Potholes'},
      {'id': 6, 'name': 'Safety'},
    ];

    // Use API categories if we have enough, otherwise use fallback
    final displayCategories = _categories.length >= 6 
        ? _categories.take(6).toList() 
        : fallbackCategories;
    
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.95,
      ),
      itemCount: displayCategories.length,
      itemBuilder: (context, index) {
        final category = displayCategories[index];
        final name = (category['name'] ?? '').toString().toLowerCase();
        final categoryKey = name.contains('street') ? 'streetlight' 
            : name.contains('water') ? 'water'
            : name.contains('damage') ? 'damage'
            : name.contains('waste') ? 'waste'
            : name.contains('pothole') || name.contains('road') ? 'pothole'
            : name.contains('safety') ? 'safety'
            : 'damage';
        
        final iconData = categoryIcons[categoryKey] ?? categoryIcons['damage']!;
        
        return _CategoryCard(
          icon: iconData['icon'] as IconData,
          label: category['name'] ?? 'Category',
          color: iconData['color'] as Color,
          onTap: () => Navigator.pushNamed(
            context,
            AppRoutes.reportProblem,
            arguments: {'category': category},
          ),
        );
      },
    );
  }

  Widget _buildRecentIssuesSection(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(20, 30, 20, 20),
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
                  color: AppColors.textPrimary,
                ),
              ),
              GestureDetector(
                onTap: () => Navigator.pushNamed(context, AppRoutes.myReports),
                child: const Text(
                  'See All',
                  style: TextStyle(
                    fontSize: 14,
                    color: AppColors.primary,
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
                  color: AppColors.textSecondary,
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
