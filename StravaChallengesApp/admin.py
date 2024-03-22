from django.contrib import admin
from .models import Athlete, Activity


class AtheteAdmin(admin.ModelAdmin):
    list_filter = ('athlete_id', 'username')
    list_display = ('username', 'firstname', 'lastname', 'athlete_id')
   
class ActivityAdmin(admin.ModelAdmin):
    list_filter = ('activity_athlete', 'activity_type', 'start_date')
    list_display = ('activity_athlete', 'activity_type', 'start_date', 'activity_id')

admin.site.register(Athlete, AtheteAdmin)
admin.site.register(Activity, ActivityAdmin)