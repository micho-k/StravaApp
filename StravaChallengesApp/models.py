from django.db import models

# Create your models here.

class Athlete(models.Model):
    athlete_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100, default='Brak')
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    sex = models.CharField(max_length=100)
    photo_medium_url = models.URLField()
    photo_large_url = models.URLField()
    total_ytd_distance = models.IntegerField(default = 0)
    ride_ytd_distance = models.IntegerField(default = 0)
    run_ytd_distance = models.IntegerField(default = 0)
    walk_ytd_distance = models.IntegerField(default = 0)
    swim_ytd_distance = models.IntegerField(default = 0)
    ski_ytd_distance = models.IntegerField(default = 0)
    other_ytd_distance = models.IntegerField(default = 0)
    last_modified = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    
class Activity(models.Model):
    activity_athlete = models.CharField(max_length=100)
    activity_id = models.CharField(max_length=100)
    activity_type = models.CharField(max_length=100)
    start_date = models.DateField()
    distance = models.IntegerField()