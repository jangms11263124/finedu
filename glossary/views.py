from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

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
