from rest_framework import serializers
from .models import Booking,Ad


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['ad_id', 'ad_title', 'ad_content', 'ad_img']