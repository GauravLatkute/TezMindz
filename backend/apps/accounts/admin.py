from django.contrib import admin
from .models import User, StudentProfile, ParentProfile, MentorProfile

# Register your models here.
admin.site.register(User)
admin.site.register(StudentProfile)
admin.site.register(ParentProfile)
admin.site.register(MentorProfile)
