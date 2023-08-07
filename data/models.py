from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import json
import os
from django.conf import settings

class Race(models.Model):
    year = models.IntegerField(default='2023')
    name = models.CharField(max_length=255)

class Driver(models.Model):
    year = models.IntegerField(default=0)  # Add default value here
    abbreviation = models.CharField(max_length=255, default='N/A')

#@receiver(post_migrate) 
#def populate_models(sender, **kwargs):
    #if sender.name == 'data':  # Replace 'yourapp' with the name of your Django app
        #file_path = os.path.join(settings.BASE_DIR, 'data', 'races.json')
        #with open(file_path) as json_file:
            #data = json.load(json_file)
#
            #for year, races in data.items():
                #for race_name in races:
                    #Race.objects.create(year=int(year), name=race_name)

@receiver(post_migrate)
def populate_drivers(sender, **kwargs):
    if sender.name == 'data':
        file_path = os.path.join(settings.BASE_DIR, 'data', 'drivers.json')
        with open(file_path) as json_file:
            data = json.load(json_file)

            for year, drivers in data.items():
                for driver_name in drivers:
                    Driver.objects.create(year=int(year), abbreviation=driver_name)
