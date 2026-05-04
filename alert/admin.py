from django.contrib import admin
from .models import DetectionEvent,Camera, ObjectType,User
# Register your models here.


admin.site.register(DetectionEvent)
admin.site.register(Camera)
admin.site.register(ObjectType)
admin.site.register(User)
