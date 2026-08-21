from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import Report
from .serializers import ReportSerializer, ReportUpdateSerializer
import httpx
from django.conf import settings


class ReportPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reports
    """
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [AllowAny]
    pagination_class = ReportPagination
    
    def get_queryset(self):
        """
        Filter queryset based on user role and query parameters
        """
        queryset = Report.objects.filter(is_deleted_by_admin=False).order_by('-created_at')
        user = self.request.user
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by priority if provided
        priority_param = self.request.query_params.get('priority', None)
        if priority_param:
            queryset = queryset.filter(priority=priority_param)
        
        # Filter by category if provided
        category_param = self.request.query_params.get('category', None)
        if category_param:
            queryset = queryset.filter(category_id=category_param)
        
        # Search by title or description
        search_param = self.request.query_params.get('search', None)
        if search_param:
            queryset = queryset.filter(
                title__icontains=search_param
            ) | queryset.filter(
                description__icontains=search_param
            )
        
        # Select related to reduce queries
        queryset = queryset.select_related('citizen', 'category')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list to return custom response format
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'success': True,
                'message': 'Reports retrieved successfully',
                'data': serializer.data,
                'count': queryset.count(),
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Reports retrieved successfully',
            'data': serializer.data,
            'count': queryset.count(),
            'next': None,
            'previous': None,
        })
    
    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to return custom response format
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Report retrieved successfully',
            'data': serializer.data,
        })
    
    def create(self, request, *args, **kwargs):
        """
        Override create to return custom response format
        New workflow:
        1. Classify image (AI suggests category)
        2. Check for duplicates
        3. Submit if unique
        
        NO quality checking - all images accepted
        """
        # Skip quality check - accept all images
        
        # Check for duplicates before creating
        duplicate_result = self._check_duplicate(request.data)
        if duplicate_result and duplicate_result.get('is_duplicate'):
            return Response({
                'success': False,
                'message': f"⚠️ This report was reported by another user (Report #{duplicate_result.get('similar_report_id')}). The municipality is already working on it!",
                'is_duplicate': True,
                'similar_report_id': duplicate_result.get('similar_report_id'),
                'similarity_score': duplicate_result.get('similarity_score'),
                'breakdown': duplicate_result.get('breakdown')
            }, status=status.HTTP_409_CONFLICT)
        
        # Create the report
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # After creation, suggest category from image if available
        image_base64 = request.data.get('media_images', [])
        suggested_category = None
        if image_base64 and len(image_base64) > 0:
            classification_result = self._classify_image(image_base64[0])
            if classification_result:
                suggested_category = classification_result
        
        response_data = serializer.data
        if suggested_category:
            response_data['ai_suggested_category'] = suggested_category
        
        return Response({
            'success': True,
            'message': 'Report submitted successfully',
            'data': response_data,
        }, status=status.HTTP_201_CREATED)
    
    def _check_image_quality(self, image_base64):
        """Check image quality using AI service"""
        try:
            import base64
            import io
            from PIL import Image
            
            # Decode base64 image
            image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Save to bytes for upload
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            # Call AI service
            ai_url = getattr(settings, 'AI_SERVICE_URL', 'http://localhost:8001')
            response = httpx.post(
                f"{ai_url}/ai/check-quality/",
                files={"file": ("image.jpg", img_byte_arr, "image/jpeg")},
                timeout=15.0
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Image quality check error: {e}")
        
        return {'status': 'pass', 'message': 'Quality check skipped'}
    
    def _map_category_to_index(self, ai_category: str) -> int:
        """
        Maps AI model category names to mobile app category indices
        
        AI Model → Mobile App Index
        - road_damage → 0 (Road Damage)
        - water_leakage → 1 (Water & Sewage)
        - garbage → 2 (Garbage)
        - streetlight_failure → 3 (Streetlight)
        - drainage → 4 (Drainage)
        - other → 5 (Other)
        - public_facility → 5 (Other - fallback)
        """
        mapping = {
            "road_damage":        0,
            "water_leakage":      1,
            "garbage":            2,
            "streetlight_failure": 3,
            "drainage":           4,
            "other":              5,
            "public_facility":    5,  # Maps to "Other"
        }
        return mapping.get(ai_category.lower(), 5)  # Default to "Other"
    
    def _classify_image(self, image_base64):
        """Classify image using AI service"""
        try:
            import base64
            import io
            from PIL import Image
            
            # Decode base64 image
            image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Save to bytes for upload
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            # Call AI service
            ai_url = getattr(settings, 'AI_SERVICE_URL', 'http://localhost:8001')
            response = httpx.post(
                f"{ai_url}/ai/classify-image/",
                files={"file": ("image.jpg", img_byte_arr, "image/jpeg")},
                timeout=15.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'category': result.get('category'),
                    'confidence': result.get('confidence'),
                    'all_scores': result.get('all_scores')
                }
        except Exception as e:
            print(f"Image classification error: {e}")
        
        return None
    
    def _check_duplicate(self, new_report_data):
        """
        VERY STRICT Duplicate Detection:
        Only blocks if ALL these match:
        - Category: 100% exact match
        - Location: Within 100m (not 500m!)
        - Description: 80%+ similar
        - Image: 85%+ similar
        """
        try:
            category_id = new_report_data.get('category_id')
            latitude = new_report_data.get('latitude')
            longitude = new_report_data.get('longitude')
            
            print(f"\n{'='*70}")
            print(f"🔍 STRICT DUPLICATE CHECK")
            print(f"{'='*70}")
            print(f"Category: {category_id}")
            print(f"Location: ({latitude}, {longitude})")
            print(f"Title: {new_report_data.get('title')}")
            
            if not (category_id and latitude and longitude):
                print(f"❌ Missing required fields")
                return None
            
            from datetime import timedelta
            from django.utils import timezone
            
            recent_date = timezone.now() - timedelta(days=30)
            
            # STRICTER: 100 meters (was 500m)
            lat_range = 0.001  # ~100 meters
            lon_range = 0.001
            
            similar_reports = Report.objects.filter(
                category_id=category_id,  # MUST be exact same category
                latitude__gte=latitude - lat_range,
                latitude__lte=latitude + lat_range,
                longitude__gte=longitude - lon_range,
                longitude__lte=longitude + lon_range,
                created_at__gte=recent_date,
                status__in=[Report.Status.SUBMITTED, Report.Status.ACCEPTED, Report.Status.IN_PROGRESS]
            ).exclude(status=Report.Status.RESOLVED)
            
            print(f"📊 Found {similar_reports.count()} nearby reports with same category")
            
            if similar_reports.count() == 0:
                print(f"✅ No similar reports - NOT DUPLICATE\n")
                return None
            
            for idx, existing_report in enumerate(similar_reports, 1):
                print(f"\n{'─'*70}")
                print(f"Comparing with Report #{existing_report.id} ({idx}/{similar_reports.count()})")
                print(f"{'─'*70}")
                
                duplicate_check = self._check_duplicate_with_ai(new_report_data, existing_report)
                
                if not duplicate_check:
                    print(f"⚠️ AI check failed")
                    continue
                
                breakdown = duplicate_check.get('breakdown', {})
                text_sc = breakdown.get('text', {}).get('score', 0)
                loc_sc = breakdown.get('location', {}).get('score', 0)
                cat_sc = breakdown.get('category', {}).get('score', 0)
                img_sc = breakdown.get('image', {}).get('score', None)
                
                print(f"📈 Scores:")
                print(f"   Category: {cat_sc:.0%} (need 100%)")
                print(f"   Location: {loc_sc:.0%} (need 95%+)")
                print(f"   Text:     {text_sc:.0%} (need 80%+)")
                if img_sc is not None:
                    print(f"   Image:    {img_sc:.0%} (need 85%+)")
                else:
                    print(f"   Image:    N/A (need 85%+)")
                
                # ALL must pass
                is_dup = (
                    cat_sc >= 0.99 and              # Category 100%
                    loc_sc >= 0.95 and              # Very close
                    text_sc >= 0.80 and             # Text 80%+
                    (img_sc is None or img_sc >= 0.85)  # Image 85%+
                )
                
                if is_dup:
                    print(f"\n{'🚨'*35}")
                    print(f"🚨 DUPLICATE DETECTED - ALL FACTORS MATCH! 🚨")
                    print(f"{'🚨'*35}\n")
                    return {
                        'is_duplicate': True,
                        'similarity_score': duplicate_check.get('similarity_score'),
                        'similar_report_id': existing_report.id,
                        'breakdown': breakdown
                    }
                else:
                    print(f"✅ Not duplicate - factors don't all match")
            
            print(f"\n✅ NO DUPLICATES FOUND\n")
            return None
            
        except Exception as e:
            print(f"❌ Duplicate check error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _check_duplicate_with_ai(self, new_data, existing_report):
        """Call AI service to check if reports are duplicates (includes image similarity)"""
        try:
            from apps.medias.models import Media
            import base64
            
            ai_url = getattr(settings, 'AI_SERVICE_URL', 'http://localhost:8001')
            
            # Get images as base64
            new_image = None
            existing_image = None
            
            # Extract new image
            media_images = new_data.get('media_images', [])
            if media_images and len(media_images) > 0:
                new_image = media_images[0]  # First image
            
            # Extract existing image from Media table
            existing_media = Media.objects.filter(
                entity_type=Media.EntityType.REPORT,
                entity_id=existing_report.id,
                file_type=Media.FileType.IMAGE
            ).first()
            
            if existing_media and existing_media.file_url:
                try:
                    # If file_url is already base64
                    if existing_media.file_url.startswith('data:image'):
                        existing_image = existing_media.file_url
                    # If it's a file path
                    elif existing_media.file_url.startswith('/') or existing_media.file_url.startswith('media/'):
                        with open(existing_media.file_url, 'rb') as img_file:
                            existing_image = f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"
                    else:
                        # Assume it's base64 without prefix
                        existing_image = f"data:image/jpeg;base64,{existing_media.file_url}"
                except Exception as e:
                    print(f"Error reading existing image: {e}")
                    existing_image = None
            
            payload = {
                "report_id": 0,  # New report doesn't have ID yet
                "title": new_data.get('title', ''),
                "description": new_data.get('description', ''),
                "category": str(new_data.get('category_id', '')),
                "latitude": new_data.get('latitude'),
                "longitude": new_data.get('longitude'),
                "image": new_image,  # Send image for comparison
                
                "existing_report_id": hash(str(existing_report.id)) % 1000000,  # Convert UUID to int via hash
                "existing_title": existing_report.title,
                "existing_description": existing_report.description,
                "existing_category": str(existing_report.category_id),
                "existing_latitude": float(existing_report.latitude) if existing_report.latitude else None,
                "existing_longitude": float(existing_report.longitude) if existing_report.longitude else None,
                "existing_image": existing_image,  # Send existing image
            }
            
            response = httpx.post(
                f"{ai_url}/ai/detect-duplicate/",
                json=payload,
                timeout=60.0  # Increased timeout for image processing
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Duplicate check result: {result}")  # Debug logging
                return result
                
        except httpx.TimeoutException as e:
            print(f"AI duplicate service timeout: {e}")
        except Exception as e:
            print(f"AI duplicate detection error: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def update(self, request, *args, **kwargs):
        """
        Override update to return custom response format
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Report updated successfully',
            'data': serializer.data,
        })
    
    def get_serializer_class(self):
        """
        Use different serializer for update actions
        """
        if self.action in ['update', 'partial_update']:
            return ReportUpdateSerializer
        return ReportSerializer
    
    @action(detail=False, methods=['post'], url_path='classify-image')
    def classify_image_early(self, request):
        """
        Classify image BEFORE user fills in details
        Returns AI-suggested category with mobile app index
        """
        image_base64 = request.data.get('image')
        if not image_base64:
            return Response({
                'success': False,
                'message': 'No image provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        classification_result = self._classify_image(image_base64)
        
        if classification_result:
            # Map AI category to mobile app index
            ai_category = classification_result['category']
            mobile_index = self._map_category_to_index(ai_category)
            
            return Response({
                'success': True,
                'message': 'Image classified successfully',
                'data': {
                    'category': ai_category,
                    'category_index': mobile_index,  # Mobile app uses this!
                    'confidence': classification_result['confidence'],
                    'all_scores': classification_result['all_scores']
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'Failed to classify image'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='my-reports')
    def my_reports(self, request):
        """
        Get reports created by the current user
        """
        user = request.user
        if user and not user.is_anonymous:
            queryset = Report.objects.filter(citizen=user, is_deleted_by_citizen=False).order_by('-created_at')
        else:
            from apps.users.models import User
            default_citizen = User.objects.filter(role='CITIZEN').first() or User.objects.first()
            if default_citizen:
                queryset = Report.objects.filter(citizen=default_citizen, is_deleted_by_citizen=False).order_by('-created_at')
            else:
                queryset = Report.objects.none()
        
        status_param = request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        queryset = queryset.select_related('citizen', 'category')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Your reports retrieved successfully',
            'data': serializer.data,
            'count': queryset.count()
        })

    @action(detail=True, methods=['post'], url_path='accept')
    def accept_report(self, request, pk=None):
        """
        Admin accepts report, assigns department/worker, and creates operational Task
        """
        from django.utils import timezone
        from datetime import timedelta
        from apps.notifications.models import Notification
        from apps.tasks.models import Task
        from apps.departments.models import Department
        
        try:
            report = self.get_object()
            data = request.data
            
            priority = data.get('priority', report.priority or 'MEDIUM').upper()
            department_id = data.get('departmentId')
            assigned_worker_id = data.get('assignedWorkerId')
            work_description = data.get('workDescription', '')
            internal_note = data.get('internalNote', '')
            
            # Assign department
            if department_id:
                try:
                    report.assigned_department = Department.objects.get(id=department_id)
                except Department.DoesNotExist:
                    print(f"Department {department_id} not found")
                    pass
            
            # If still no department, use first one
            if not report.assigned_department:
                report.assigned_department = Department.objects.first()
                if not report.assigned_department:
                    return Response({
                        'success': False,
                        'message': 'No departments available. Please create a department first.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            report.priority = priority
            report.status = Report.Status.ACCEPTED
            report.admin_feedback = internal_note
            report.save()

            # Create or update operational Task
            task_number = f"TSK-{timezone.now().strftime('%Y%m%d')}-{report.report_number.split('-')[-1]}"
            
            task, created = Task.objects.get_or_create(
                report=report,
                defaults={
                    'task_number': task_number,
                    'title': f"Work Order: {report.title}",
                    'description': work_description or report.description,
                    'department': report.assigned_department,
                    'priority': priority,
                    'status': Task.Status.ACCEPTED,
                    'original_deadline': timezone.now() + timedelta(days=3),
                    'current_deadline': timezone.now() + timedelta(days=3),
                    'accepted_at': timezone.now(),
                }
            )
            
            if not created:
                task.status = Task.Status.ACCEPTED
                task.description = work_description or task.description
                task.save()

            # Create notification for citizen
            Notification.objects.create(
                user=report.citizen,
                title="Report Accepted & Work Order Dispatched",
                message=f"Your report ({report.report_number}) has been accepted and assigned to the {report.assigned_department.name if report.assigned_department else 'Maintenance'} department.",
                type="STATUS_UPDATE"
            )

            return Response({
                'success': True,
                'message': 'Report accepted and task dispatched successfully',
                'data': ReportSerializer(report, context={'request': request}).data,
                'task_id': str(task.id),
                'task_number': task.task_number,
            })
            
        except Exception as e:
            import traceback
            print(f"Error accepting report: {e}")
            traceback.print_exc()
            return Response({
                'success': False,
                'message': f'Error accepting report: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_report(self, request, pk=None):
        """
        Admin rejects report with explanation
        """
        from apps.notifications.models import Notification
        
        report = self.get_object()
        reason = request.data.get('reason', 'Report rejected by municipality admin.')
        
        report.status = Report.Status.REJECTED
        report.admin_feedback = reason
        report.save()

        # Create notification for citizen
        Notification.objects.create(
            user=report.citizen,
            title="Report Status Update",
            message=f"Your report ({report.report_number}) was reviewed. Reason: {reason}",
            type="STATUS_UPDATE"
        )

        return Response({
            'success': True,
            'message': 'Report rejected',
            'data': ReportSerializer(report, context={'request': request}).data
        })

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_report(self, request, pk=None):
        """
        Officer/Contractor submits work completion evidence
        """
        from django.utils import timezone
        from apps.notifications.models import Notification
        
        report = self.get_object()
        completion_notes = request.data.get('completion_notes', 'Work completed by contractor.')
        
        report.status = Report.Status.PENDING_VERIFICATION
        report.completion_notes = completion_notes
        report.save()

        # Update linked tasks
        report.tasks.update(status='COMPLETED_PENDING_VERIFICATION', completion_notes=completion_notes, completed_at=timezone.now())

        return Response({
            'success': True,
            'message': 'Completion evidence submitted for verification',
            'data': ReportSerializer(report, context={'request': request}).data
        })

    @action(detail=True, methods=['post'], url_path='verify')
    def verify_report(self, request, pk=None):
        """
        Admin reviews completion. If approved=True -> RESOLVED. If approved=False -> REOPENED.
        """
        from django.utils import timezone
        from apps.notifications.models import Notification
        from apps.tasks.models import Task
        
        report = self.get_object()
        approved = request.data.get('approved', True)
        note = request.data.get('note', '')

        if approved:
            report.status = Report.Status.RESOLVED
            report.resolved_at = timezone.now()
            report.admin_feedback = note
            report.save()

            report.tasks.update(status=Task.Status.VERIFIED, verified_at=timezone.now())

            # Notify citizen of resolution!
            Notification.objects.create(
                user=report.citizen,
                title="🎉 Problem Resolved!",
                message=f"Great news! Your reported issue ({report.report_number} - {report.title}) has been resolved and verified by municipal inspectors.",
                type="STATUS_UPDATE"
            )
        else:
            report.status = Report.Status.REOPENED
            report.admin_feedback = note
            report.save()

            report.tasks.update(status=Task.Status.REOPENED)

            Notification.objects.create(
                user=report.citizen,
                title="Report Status Update",
                message=f"Work on your report ({report.report_number}) requires additional refinement and has been reopened.",
                type="STATUS_UPDATE"
            )

        return Response({
            'success': True,
            'message': 'Report resolution status updated',
            'data': ReportSerializer(report, context={'request': request}).data
        })

    @action(detail=True, methods=['post'], url_path='in-progress')
    def mark_in_progress(self, request, pk=None):
        """
        Admin or Field Officer marks report status as IN_PROGRESS
        """
        from django.utils import timezone
        from apps.notifications.models import Notification
        from apps.tasks.models import Task

        report = self.get_object()
        report.status = Report.Status.IN_PROGRESS
        report.save()

        # Update tasks
        report.tasks.update(status=Task.Status.IN_PROGRESS, started_at=timezone.now())

        # Send Notification to Citizen!
        Notification.objects.create(
            user=report.citizen,
            title="Work Started (In Progress)",
            message=f"Maintenance crew has started working on your reported issue ({report.report_number} - {report.title}).",
            type="STATUS_UPDATE"
        )

        return Response({
            'success': True,
            'message': 'Report status updated to IN_PROGRESS',
            'data': ReportSerializer(report, context={'request': request}).data
        })

    @action(detail=True, methods=['post'], url_path='resolve')
    def mark_resolved(self, request, pk=None):
        """
        Admin directly marks report status as RESOLVED
        """
        from django.utils import timezone
        from apps.notifications.models import Notification
        from apps.tasks.models import Task

        report = self.get_object()
        note = request.data.get('note', 'Issue resolved and verified by municipal team.')

        report.status = Report.Status.RESOLVED
        report.resolved_at = timezone.now()
        report.admin_feedback = note
        report.save()

        report.tasks.update(status=Task.Status.VERIFIED, verified_at=timezone.now())

        # Send Notification to Citizen!
        Notification.objects.create(
            user=report.citizen,
            title="Problem Resolved!",
            message=f"Great news! Your reported issue ({report.report_number} - {report.title}) has been resolved and verified.",
            type="STATUS_UPDATE"
        )

        return Response({
            'success': True,
            'message': 'Report status updated to RESOLVED',
            'data': ReportSerializer(report, context={'request': request}).data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Admin delete only soft-deletes for admin (is_deleted_by_admin=True)
        so the citizen reporter can still view their resolved report progress!
        """
        report = self.get_object()
        report.is_deleted_by_admin = True
        if report.is_deleted_by_citizen:
            report.delete()
        else:
            report.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='citizen-delete')
    def citizen_delete(self, request, pk=None):
        """
        Citizen reporter removes resolved report from their mobile app history
        """
        report = Report.objects.filter(pk=pk).first()
        if not report:
            return Response({'success': False, 'message': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        report.is_deleted_by_citizen = True
        if report.is_deleted_by_admin:
            report.delete()
        else:
            report.save()

        return Response({
            'success': True,
            'message': 'Report removed from your mobile app history'
        })
