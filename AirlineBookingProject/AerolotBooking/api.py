from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Ad, Booking
from .serializers import AdSerializer
from . import views
urlpatterns = [
    path('get-ads/', views.get_ads, name='get_ads'),
]
@api_view(['GET'])
def get_ads(request):
    ads = Ad.objects.all()
    serializer = AdSerializer(ads, many=True)
    return Response({"ads": serializer.data})


