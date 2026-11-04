import 'dart:io';
import 'dart:ui' as ui;
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:image_picker/image_picker.dart';
import 'package:latlong2/latlong.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cirp/core/theme/app_theme.dart';
import 'package:cirp/generated/app_localizations.dart';
import 'package:cirp/features/location/screens/location_picker_screen.dart';
import 'package:cirp/core/services/api_service.dart';
import 'package:cirp/core/services/auth_service.dart';

class ReportProblemScreen extends StatefulWidget {
  const ReportProblemScreen({super.key});

  @override
  State<ReportProblemScreen> createState() => _ReportProblemScreenState();
}

class _ReportProblemScreenState extends State<ReportProblemScreen> with WidgetsBindingObserver {
  int _currentStep = 0;

  LatLng _pickedLatLng = const LatLng(9.0054, 38.7636);
  String _pickedAddress = 'Bole Road, near Atlas, Addis Ababa';
  final MapController _previewMap = MapController();

  int _selectedCategory = 0;
  int _selectedSubcategory = 0;
  int _severityIndex = 1;
  String _selectedDate = 'Today';
  final _descController = TextEditingController();
  final _notesController = TextEditingController();

  XFile? _pickedImage;
  Uint8List? _pickedImageBytes;
  final ImagePicker _picker = ImagePicker();
  
  // Store image path to restore after camera lifecycle
  String? _savedImagePath;
  
  // Use global AuthService for token management
  final AuthService _authService = AuthService();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _loadTokenAndRestoreImage();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    print('📱 App lifecycle state changed to: $state');
    
    // When app resumes after camera, restore token and image
    if (state == AppLifecycleState.resumed) {
      _authService.restoreToken(); // Restore token from memory cache
      _loadTokenAndRestoreImage();
    }
  }

  Future<void> _loadTokenAndRestoreImage() async {
    try {
      // Restore image if path was saved
      if (_savedImagePath != null && _pickedImage == null) {
        final file = File(_savedImagePath!);
        if (await file.exists()) {
          final bytes = await file.readAsBytes();
          if (mounted) {
            setState(() {
              _pickedImage = XFile(_savedImagePath!);
              _pickedImageBytes = bytes;
            });
            print('✅ Image restored after camera: $_savedImagePath');
          }
        }
      }
    } catch (e) {
      print('Error restoring state: $e');
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      print('📸 Starting image picker: ${source == ImageSource.camera ? "CAMERA" : "GALLERY"}');
      
      final img = await _picker.pickImage(
        source: source, imageQuality: 85, maxWidth: 1920, maxHeight: 1920,
      );
      
      if (img != null) {
        print('✅ Image picked successfully: ${img.path}');
        final bytes = await img.readAsBytes();
        print('✅ Image bytes read: ${bytes.length} bytes');
        
        if (mounted) {
          setState(() {
            _pickedImage = img;
            _pickedImageBytes = bytes;
            _savedImagePath = img.path; // Save path for restoration
          });
          print('✅ Image state updated in UI');
        }
      } else {
        print('❌ No image selected (user cancelled)');
      }
    } catch (e) {
      print('❌ Error picking image: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not pick image: $e'),
              backgroundColor: AppColors.red),
        );
      }
    }
  }

  Widget _buildPreviewImage({double? width, double? height, BoxFit fit = BoxFit.cover}) {
    if (_pickedImageBytes != null) {
      return Image.memory(_pickedImageBytes!, width: width, height: height, fit: fit);
    }
    return const Center(child: CircularProgressIndicator(color: Colors.white));
  }

  final Map<int, List<String>> _subcategories = {
    0: ['Pothole', 'Crack', 'Erosion'],
    1: ['Pipe burst', 'Drainage overflow', 'Leak'],
    2: ['Uncollected trash', 'Illegal dumping'],
    3: ['Not working', 'Damaged pole'],
    4: ['Blocked drain', 'Flood risk'],
    5: ['Other'],
  };

  List<String> get _currentSubcategories =>
      _subcategories[_selectedCategory] ?? ['Other'];

  final List<String> _dateOptions = [
    'Today', 'Yesterday', '2 days ago', 'This week', 'This month'
  ];

  List<IconData> get _stepIcons => [
        Icons.photo_camera_outlined,
        Icons.location_on_outlined,
        Icons.info_outline,
        Icons.rate_review_outlined,
      ];

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _descController.dispose();
    _notesController.dispose();
    _previewMap.dispose();
    super.dispose();
  }

  Future<void> _openLocationPicker() async {
    final result = await Navigator.push<PickedLocation>(
      context,
      MaterialPageRoute(builder: (_) => const LocationPickerScreen()),
    );
    if (result != null) {
      setState(() {
        _pickedLatLng = result.latLng;
        _pickedAddress = result.address;
      });
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _previewMap.move(_pickedLatLng, 15.0);
      });
    }
  }


  void _next() async {
    if (_currentStep < 3) {
      setState(() => _currentStep++);
    } else {
      // Submit report to API
      await _submitReport();
    }
  }

  Future<void> _submitReport() async {
    final l10n = AppLocalizations.of(context);
    
    print('🚀 Starting report submission...');
    
    // Check authentication using AuthService
    String? token = await _authService.getAccessToken();
    
    print('🔑 Token check: ${token == null || token.isEmpty ? "EMPTY" : "EXISTS (${token.substring(0, 20)}...)"}');
    
    if (token == null || token.isEmpty) {
      print('❌ No token found - redirecting to login');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Session expired. Please login again.'),
            backgroundColor: AppColors.red,
          ),
        );
        Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
      }
      return;
    }
    
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => const Center(child: CircularProgressIndicator()),
    );
    
    // Prepare image data (convert to base64 if image exists)
    List<String>? imageUrls;
    if (_pickedImage != null) {
      try {
        final bytes = await _pickedImage!.readAsBytes();
        final base64Image = base64Encode(bytes);
        imageUrls = [base64Image]; // Backend should handle base64 or file upload
      } catch (e) {
        print('Error reading image: $e');
      }
    }
    
    // Get category name and UUID (from actual database)
    final categories = ['Road Damage', 'Water Leakage', 'Garbage', 'Streetlight', 'Drainage', 'Other'];
    final categoryUUIDs = [
      '771ed052-e3f0-4709-bf8c-30cf532751d8', // Road Damage -> Public Works
      'c0810993-eba1-4649-bab3-759c52b5b6b6', // Water Leakage -> Water & Sewage
      '01393c0f-6bff-44ac-9533-7cdbeae21a4e', // Garbage -> Sanitation
      'aeac7e07-736a-46ac-a8d4-e8d95ddc8138', // Streetlight -> Electrical Services
      'ca7060f8-52d7-478b-9a46-da95eb3ac224', // Drainage -> Water & Sewage
      '0964f75b-4375-4986-803a-1a2bfaf2dd7e', // Other -> Public Works
    ];
    final categoryName = categories[_selectedCategory];
    final categoryId = categoryUUIDs[_selectedCategory % categoryUUIDs.length];
    final subcategoryName = _currentSubcategories[_selectedSubcategory];
    
    // Determine priority based on severity
    String priority = 'MEDIUM';
    if (_severityIndex == 0) priority = 'LOW';
    if (_severityIndex == 2) priority = 'HIGH';
    
    print('🚀 Submitting report with category_id: $categoryId');
    
    // Create report
    final result = await ApiService.createReport(
      title: '$categoryName: $subcategoryName',
      description: _descController.text.isEmpty 
          ? 'No description provided' 
          : _descController.text,
      categoryId: categoryId,
      latitude: _pickedLatLng.latitude,
      longitude: _pickedLatLng.longitude,
      address: _pickedAddress,
      priority: priority,
      images: imageUrls,
    );
    
    if (mounted) {
      Navigator.pop(context); // Close loading dialog
      
      if (result['success'] == true) {
        _showSuccess();
      } else {
        final errorMsg = result['message'] ?? 'Failed to submit report';
        print('❌ Report submission failed: $errorMsg');
        
        // If auth error, redirect to login
        if (errorMsg.toLowerCase().contains('unauthorized') || 
            errorMsg.toLowerCase().contains('token') ||
            errorMsg.toLowerCase().contains('authentication')) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Session expired. Please login again.'),
              backgroundColor: AppColors.red,
            ),
          );
          Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMsg),
              backgroundColor: AppColors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      }
    }
  }

  void _back() {
    if (_currentStep > 0) setState(() => _currentStep--);
  }

  void _showSuccess() {
    final l10n = AppLocalizations.of(context);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 8),
            Container(
              width: 64, height: 64,
              decoration: const BoxDecoration(
                  color: Color(0xFFE8F5E9), shape: BoxShape.circle),
              child: const Icon(Icons.check, color: AppColors.green, size: 36),
            ),
            const SizedBox(height: 16),
            Text(l10n.reportSubmitted,
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
            const SizedBox(height: 8),
            Text(l10n.reportSubmittedMsg,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, height: 1.5)),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () { Navigator.pop(ctx); Navigator.pop(context); },
              child: Text(l10n.done),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final steps = [l10n.stepPhoto, l10n.stepLocation, l10n.stepDetails, l10n.stepReview];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(l10n.reportProblemTitle),
        backgroundColor: AppColors.white,
        elevation: 0,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(72),
          child: _buildStepper(steps),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.only(bottom: 24),
        child: Column(children: [
          const SizedBox(height: 20),
          _buildStep(context, l10n),
        ]),
      ),
      bottomNavigationBar: _buildBottomBar(context, l10n),
    );
  }

  Widget _buildStepper(List<String> steps) {
    return Container(
      color: AppColors.white,
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 14),
      child: Row(
        children: List.generate(steps.length, (i) {
          final done = i < _currentStep;
          final active = i == _currentStep;
          return Expanded(
            child: Row(children: [
              Column(mainAxisSize: MainAxisSize.min, children: [
                Container(
                  width: 34, height: 34,
                  decoration: BoxDecoration(
                    color: done ? AppColors.green : active ? AppColors.primary : AppColors.divider,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(done ? Icons.check : _stepIcons[i],
                      color: (done || active) ? AppColors.white : AppColors.textSecondary, size: 17),
                ),
                const SizedBox(height: 4),
                Text(steps[i], style: TextStyle(
                  fontSize: 10,
                  fontWeight: active ? FontWeight.w700 : FontWeight.w400,
                  color: active ? AppColors.primary : done ? AppColors.green : AppColors.textSecondary,
                )),
              ]),
              if (i < steps.length - 1)
                Expanded(child: Container(
                  height: 2, margin: const EdgeInsets.only(bottom: 20),
                  color: i < _currentStep ? AppColors.green : AppColors.divider,
                )),
            ]),
          );
        }),
      ),
    );
  }

  Widget _buildBottomBar(BuildContext context, AppLocalizations l10n) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      color: AppColors.white,
      child: Row(children: [
        if (_currentStep > 0) ...[
          Expanded(
            child: OutlinedButton(
              onPressed: _back,
              style: OutlinedButton.styleFrom(minimumSize: const Size(0, 50)),
              child: Text(l10n.cancel),
            ),
          ),
          const SizedBox(width: 12),
        ],
        Expanded(
          flex: 2,
          child: ElevatedButton(
            onPressed: _next,
            style: ElevatedButton.styleFrom(minimumSize: const Size(0, 50)),
            child: Text(_currentStep == 3 ? l10n.submit : l10n.next),
          ),
        ),
      ]),
    );
  }

  Widget _buildStep(BuildContext context, AppLocalizations l10n) {
    switch (_currentStep) {
      case 0: return _photoStep(context, l10n);
      case 1: return _locationStep(context, l10n);
      case 2: return _detailsStep(context, l10n);
      case 3: return _reviewStep(context, l10n);
      default: return const SizedBox.shrink();
    }
  }

  Widget _locationStep(BuildContext context, AppLocalizations l10n) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: SizedBox(
            height: 220,
            child: Stack(children: [
              FlutterMap(
                mapController: _previewMap,
                options: MapOptions(
                  initialCenter: _pickedLatLng, initialZoom: 15.0,
                  interactionOptions: const InteractionOptions(flags: InteractiveFlag.none),
                ),
                children: [
                  TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.cirp.app', maxZoom: 19),
                  MarkerLayer(markers: [
                    Marker(point: _pickedLatLng, width: 40, height: 48,
                        child: const _PinWidget()),
                  ]),
                ],
              ),
              Positioned.fill(child: GestureDetector(
                  onTap: _openLocationPicker, child: Container(color: Colors.transparent))),
              Positioned(right: 10, bottom: 10, child: GestureDetector(
                onTap: _openLocationPicker,
                child: Container(
                  width: 36, height: 36,
                  decoration: BoxDecoration(color: AppColors.white, borderRadius: BorderRadius.circular(8),
                      boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.15), blurRadius: 6)]),
                  child: const Icon(Icons.my_location, color: AppColors.primary, size: 20),
                ),
              )),
            ]),
          ),
        ),
        const SizedBox(height: 14),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(color: AppColors.white, borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.divider)),
          child: Row(children: [
            Container(
              width: 38, height: 38,
              decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(10)),
              child: const Icon(Icons.location_on, color: AppColors.primary, size: 20),
            ),
            const SizedBox(width: 12),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(l10n.stepLocation, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, fontWeight: FontWeight.w500)),
              const SizedBox(height: 2),
              Text(_pickedAddress, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
              const SizedBox(height: 2),
              Text('Lat: ${_pickedLatLng.latitude.toStringAsFixed(4)}, Lng: ${_pickedLatLng.longitude.toStringAsFixed(4)}',
                  style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
            ])),
            GestureDetector(
              onTap: _openLocationPicker,
              child: Text(l10n.changeLocation, style: const TextStyle(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.w600)),
            ),
          ]),
        ),
      ]),
    );
  }

  Widget _detailsStep(BuildContext context, AppLocalizations l10n) {
    final categories = [l10n.catRoadDamage, l10n.catWaterLeakage, l10n.catGarbage,
        l10n.catStreetlight, l10n.catDrainage, l10n.catOther];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _SectionLabel(label: l10n.categoryAI),
        const SizedBox(height: 8),
        _DropdownField(
          icon: Icons.category_outlined, value: _selectedCategory,
          items: List.generate(categories.length,
              (i) => DropdownMenuItem(value: i, child: Text(categories[i]))),
          onChanged: (v) => setState(() { _selectedCategory = v!; _selectedSubcategory = 0; }),
        ),
        const SizedBox(height: 14),
        const _SectionLabel(label: 'Subcategory (optional)'),
        const SizedBox(height: 8),
        _DropdownField(
          icon: Icons.subdirectory_arrow_right, value: _selectedSubcategory,
          items: List.generate(_currentSubcategories.length,
              (i) => DropdownMenuItem(value: i, child: Text(_currentSubcategories[i]))),
          onChanged: (v) => setState(() => _selectedSubcategory = v!),
        ),
        const SizedBox(height: 14),
        const _SectionLabel(label: 'Severity Level'),
        const SizedBox(height: 10),
        _SeveritySelector(selected: _severityIndex, onChanged: (i) => setState(() => _severityIndex = i)),
        const SizedBox(height: 14),
        const _SectionLabel(label: 'When did you notice it?'),
        const SizedBox(height: 8),
        _DropdownField(
          icon: Icons.calendar_today_outlined, value: _selectedDate,
          items: _dateOptions.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
          onChanged: (v) => setState(() => _selectedDate = v as String),
        ),
        const SizedBox(height: 14),
        _SectionLabel(label: l10n.description),
        const SizedBox(height: 8),
        TextFormField(controller: _descController, maxLines: 4, maxLength: 500,
            decoration: InputDecoration(hintText: l10n.descriptionHint, alignLabelWithHint: true)),
        const SizedBox(height: 14),
        const _SectionLabel(label: 'Additional Notes (optional)'),
        const SizedBox(height: 8),
        TextFormField(controller: _notesController, maxLines: 3, maxLength: 300,
            decoration: const InputDecoration(hintText: 'Any other information...', alignLabelWithHint: true)),
      ]),
    );
  }

  Widget _photoStep(BuildContext context, AppLocalizations l10n) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(children: [
        Container(
          height: 280, width: double.infinity,
          decoration: BoxDecoration(color: Colors.grey.shade900, borderRadius: BorderRadius.circular(16)),
          child: _pickedImage != null
              ? Stack(fit: StackFit.expand, children: [
                  ClipRRect(borderRadius: BorderRadius.circular(16),
                      child: _buildPreviewImage(fit: BoxFit.cover)),
                  Positioned(top: 10, right: 10, child: GestureDetector(
                    onTap: () => setState(() {
                      _pickedImage = null;
                      _pickedImageBytes = null;
                    }),
                    child: Container(
                      width: 32, height: 32,
                      decoration: BoxDecoration(color: Colors.black.withValues(alpha: 0.6), shape: BoxShape.circle),
                      child: const Icon(Icons.close, color: Colors.white, size: 18),
                    ),
                  )),
                ])
              : ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Stack(fit: StackFit.expand, children: [
                    Container(color: Colors.black87),
                    const Center(child: Icon(Icons.photo_library_outlined, color: Colors.white38, size: 64)),
                    Positioned(bottom: 0, left: 0, right: 0, child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.45),
                        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(16)),
                      ),
                      child: const Text('Select a photo from your gallery', textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.white, fontSize: 13)),
                    )),
                  ]),
                ),
        ),
        const SizedBox(height: 16),
        // Warning about camera
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.yellow.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.yellow.withValues(alpha: 0.3)),
          ),
          child: Row(children: [
            const Icon(Icons.info_outline, color: AppColors.yellow, size: 20),
            const SizedBox(width: 10),
            const Expanded(
              child: Text(
                'Take photo with your phone camera first, then select from gallery here',
                style: TextStyle(fontSize: 12, color: AppColors.textSecondary, height: 1.4),
              ),
            ),
          ]),
        ),
        const SizedBox(height: 24),
        _PhotoActionButton(icon: Icons.photo_library_outlined, label: 'Select from Gallery',
            onTap: () => _pickImage(ImageSource.gallery), primary: true),
        const SizedBox(height: 20),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.primary.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.primary.withValues(alpha: 0.15)),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              const Icon(Icons.lightbulb_outline, color: AppColors.primary, size: 18),
              const SizedBox(width: 6),
              const Text('Photo Tips', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.primary)),
            ]),
            const SizedBox(height: 8),
            _tipRow('Take clear photos showing the problem'),
            _tipRow('Make sure the area is well-lit'),
            _tipRow('Include landmarks for location reference'),
          ]),
        ),
      ]),
    );
  }

  Widget _tipRow(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('• ', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w700)),
        Expanded(child: Text(text, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary))),
      ]),
    );
  }

  Widget _reviewStep(BuildContext context, AppLocalizations l10n) {
    final categories = [l10n.catRoadDamage, l10n.catWaterLeakage, l10n.catGarbage,
        l10n.catStreetlight, l10n.catDrainage, l10n.catOther];
    final severityLabels = ['Low', 'Medium', 'High'];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(l10n.reviewYourReport,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(height: 16),
        ClipRRect(borderRadius: BorderRadius.circular(14), child: SizedBox(
          height: 130,
          child: FlutterMap(
            options: MapOptions(initialCenter: _pickedLatLng, initialZoom: 15.0,
                interactionOptions: const InteractionOptions(flags: InteractiveFlag.none)),
            children: [
              TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.cirp.app', maxZoom: 19),
              MarkerLayer(markers: [Marker(point: _pickedLatLng, width: 36, height: 44, child: const _PinWidget())]),
            ],
          ),
        )),
        const SizedBox(height: 12),
        _ReviewRow(icon: Icons.location_on_outlined, label: l10n.stepLocation, value: _pickedAddress),
        _ReviewRow(icon: Icons.category_outlined, label: l10n.stepDetails,
            value: '${categories[_selectedCategory]} › ${_currentSubcategories[_selectedSubcategory]}'),
        _ReviewRow(icon: Icons.warning_amber_outlined, label: 'Severity', value: severityLabels[_severityIndex]),
        _ReviewRow(icon: Icons.description_outlined, label: l10n.description,
            value: _descController.text.isNotEmpty ? _descController.text : '—'),
        if (_pickedImage != null) ...[
          const SizedBox(height: 10),
          ClipRRect(borderRadius: BorderRadius.circular(12), child: SizedBox(
            height: 150, width: double.infinity,
            child: _buildPreviewImage(fit: BoxFit.cover),
          )),
        ],
        const SizedBox(height: 10),
        _ReviewRow(icon: Icons.photo_camera_outlined, label: l10n.stepPhoto,
            value: _pickedImage != null ? l10n.photoAttached : l10n.noPhotoAttached),
      ]),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  const _SectionLabel({required this.label});

  @override
  Widget build(BuildContext context) {
    return Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary));
  }
}

class _DropdownField<T> extends StatelessWidget {
  final IconData icon;
  final T value;
  final List<DropdownMenuItem<T>> items;
  final ValueChanged<T?> onChanged;

  const _DropdownField({required this.icon, required this.value, required this.items, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
      decoration: BoxDecoration(color: AppColors.inputFill, borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.divider)),
      child: Row(children: [
        Icon(icon, color: AppColors.textSecondary, size: 20),
        const SizedBox(width: 10),
        Expanded(child: DropdownButtonHideUnderline(child: DropdownButton<T>(
          value: value, isExpanded: true,
          icon: const Icon(Icons.keyboard_arrow_down, color: AppColors.textSecondary),
          style: const TextStyle(fontSize: 14, color: AppColors.textPrimary),
          items: items, onChanged: onChanged,
        ))),
      ]),
    );
  }
}

class _SeveritySelector extends StatelessWidget {
  final int selected;
  final ValueChanged<int> onChanged;

  const _SeveritySelector({required this.selected, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final labels = ['Low', 'Medium', 'High'];
    final colors = [AppColors.severityLow, AppColors.severityMedium, AppColors.severityHigh];

    return Row(
      children: List.generate(3, (i) {
        final isSelected = selected == i;
        return Expanded(child: GestureDetector(
          onTap: () => onChanged(i),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            margin: EdgeInsets.only(right: i < 2 ? 8 : 0),
            padding: const EdgeInsets.symmetric(vertical: 10),
            decoration: BoxDecoration(
              color: isSelected ? colors[i].withValues(alpha: 0.12) : AppColors.inputFill,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: isSelected ? colors[i] : AppColors.divider, width: isSelected ? 1.8 : 1),
            ),
            child: Center(child: Text(labels[i], style: TextStyle(
              fontSize: 13, fontWeight: isSelected ? FontWeight.w700 : FontWeight.w400,
              color: isSelected ? colors[i] : AppColors.textSecondary,
            ))),
          ),
        ));
      }),
    );
  }
}

class _PhotoActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool primary;

  const _PhotoActionButton({required this.icon, required this.label, required this.onTap, required this.primary});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: primary ? AppColors.primary : AppColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: primary ? AppColors.primary : AppColors.divider),
        ),
        child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(icon, color: primary ? AppColors.white : AppColors.primary, size: 22),
          const SizedBox(width: 8),
          Text(label, style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600,
              color: primary ? AppColors.white : AppColors.primary)),
        ]),
      ),
    );
  }
}

class _ReviewRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _ReviewRow({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: AppColors.white, borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.divider)),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Container(
          width: 34, height: 34,
          decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.08), borderRadius: BorderRadius.circular(8)),
          child: Icon(icon, color: AppColors.primary, size: 17),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, fontWeight: FontWeight.w500)),
          const SizedBox(height: 3),
          Text(value, style: const TextStyle(fontSize: 14, color: AppColors.textPrimary, height: 1.4)),
        ])),
      ]),
    );
  }
}

class _PinWidget extends StatelessWidget {
  const _PinWidget();

  @override
  Widget build(BuildContext context) {
    return Column(mainAxisSize: MainAxisSize.min, children: [
      Container(
        width: 30, height: 30,
        decoration: BoxDecoration(color: AppColors.red, shape: BoxShape.circle,
            boxShadow: [BoxShadow(color: AppColors.red.withValues(alpha: 0.4), blurRadius: 6, offset: const Offset(0, 3))]),
        child: const Icon(Icons.location_on, color: Colors.white, size: 16),
      ),
      CustomPaint(size: const Size(10, 8), painter: _PinTail()),
    ]);
  }
}

class _PinTail extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final path = ui.Path()
      ..moveTo(0, 0)
      ..lineTo(size.width / 2, size.height)
      ..lineTo(size.width, 0)
      ..close();
    canvas.drawPath(path, Paint()..color = AppColors.red);
  }

  @override
  bool shouldRepaint(covariant CustomPainter _) => false;
}
