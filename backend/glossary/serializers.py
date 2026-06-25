from rest_framework import serializers

from .models import Term


class TermSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(
        source='get_subject_display', read_only=True
    )

    class Meta:
        model = Term
        fields = ('id', 'subject', 'subject_display', 'term', 'description',
                  'initial', 'created_at')
