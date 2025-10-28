from rest_framework import serializers
from .models import IPO, SimilarIPO, HistoricalIPO

class SimilarIPOSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarIPO
        fields = '__all__'

class IPOSerializer(serializers.ModelSerializer):
    similar_ipos = SimilarIPOSerializer(many=True, read_only=True)

    class Meta:
        model = IPO
        fields = '__all__'

class HistoricalIPOSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalIPO
        fields = '__all__'
