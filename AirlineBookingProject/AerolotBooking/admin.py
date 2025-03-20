from django.contrib import admin
from .models import Flight,Booking,Ad,CustomUser
# Register your models here.
admin.site.register(Flight)
admin.site.register(Booking)
admin.site.register(Ad)
admin.site.register(CustomUser)