from django.contrib import admin
from .models import Plan, Subscription, TrialGameLog, Payment

# Register your models here.
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(TrialGameLog)
admin.site.register(Payment)
