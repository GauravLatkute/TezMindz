from django.contrib import admin
from .models import CreditAccount, CreditTransaction, XPAccount, XPLevelThreshold, XPTransaction, Badge, StudentBadge


# Register your models here.
admin.site.register(CreditAccount)
admin.site.register(CreditTransaction)
admin.site.register(XPAccount)
admin.site.register(XPLevelThreshold)
admin.site.register(XPTransaction)
admin.site.register(Badge)
admin.site.register(StudentBadge)
