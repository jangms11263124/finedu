from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Term
from .serializers import TermSerializer


class TermViewSet(viewsets.ModelViewSet):
    """경제 용어 사전. ?subject= 주제 / ?initial= 두문자 / ?q= 검색."""

    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if subject := params.get('subject'):
            qs = qs.filter(subject=subject)
        if initial := params.get('initial'):
            qs = qs.filter(initial=initial)
        if q := params.get('q'):
            qs = (qs.filter(term__icontains=q)
                  | qs.filter(description__icontains=q))
        return qs.distinct()

    @action(detail=False, methods=['get'])
    def initials(self, request):
        """DB에 실제 존재하는 모든 두문자 목록을 반환."""
        used_initials = Term.objects.values_list('initial', flat=True).distinct()
        used_initials = [x for x in used_initials if x]
        return Response(used_initials)
