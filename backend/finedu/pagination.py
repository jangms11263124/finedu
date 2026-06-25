from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class OptionalPageNumberPagination(PageNumberPagination):
    """`?page` 파라미터가 있을 때만 페이지네이션을 적용한다.

    기존 엔드포인트(배열 응답을 기대하는 홈/커뮤니티 등)는 그대로 두고,
    목록 페이지에서만 ?page=N 으로 페이지네이션을 사용한다.
    """

    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 60

    def paginate_queryset(self, queryset, request, view=None):
        if 'page' not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'total_pages': self.page.paginator.num_pages,
            'results': data,
        })
