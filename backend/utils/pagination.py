from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .responses import is_mobile_client


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        # If requested by Flutter mobile app, return the structured envelope
        if is_mobile_client(self.request):
            return Response({
                'success': True,
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'data': data
            })

        # For React Admin Zod arrays or paginated views
        # If client explicitly specifies paginated params, provide count/results; else list
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
