from django.contrib import admin
from .models import Notification,DeviceFcmToken



admin.site.register(Notification)
admin.site.register(DeviceFcmToken)
