from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from unittest.util import _MAX_LENGTH

# Create your models here.

STATUS = (
    ('0', 'READY'),
    ('1', 'WAITING'),
    ('2', 'RUNNING'),
    ('3', 'FINISHED'),
    ('4', 'FAILED'),
    ('5', 'DEPRECATED'),
)

ROLE = (
    ('0', 'INPUT'),
    ('1', 'OUTPUT'),
)

DATATYPE = (
    ('0', 'LITERAL'),
    ('1', 'COMPLEX'),
    ('2', 'BOUNDING_BOX'),
)


class Workflow(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    percent_done = models.DecimalField(max_digits=3, decimal_places=0)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    creator = models.ForeignKey(User, editable=False)
    last_modifier = models.ForeignKey(User, editable=True)
    

class WPSProvider(models.Model):
    provider_name = models.CharField(max_length=200)
    provider_site = models.URLField(max_length=1000)
    individual_name = models.CharField(max_length=200)
    position_name = models.CharField(max_length=200)


class WPS(models.Model):
    service_provider = models.ForeignKey(WPSProvider, on_delete=models.CASCADE)
    title = models.CharField(max_length = 200)
    abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    capabilities_url = models.URLField(max_length=1000)
    describe_url = models.URLField(max_length=1000)
    execute_url = models.URLField(max_length=1000)    
    
    
class Process(models.Model):
    wps = models.ForeignKey(WPS, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
        

class Task(models.Model):    
    workflow = models.ForeignKey(Workflow)
    process = models.ForeignKey(Process)
    x = models.DecimalField(max_digits=5, decimal_places=0)
    y = models.DecimalField(max_digits=5, decimal_places=0)
    status = models.CharField(max_length=1, choices=STATUS)
    title = models.CharField(max_length=200)
    abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    status_url = models.URLField(max_length=1000)
    started_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    



class Session(models.Model):
    user = models.ForeignKey(User, editable= False)
    last_workflow = models.ForeignKey(Workflow)
    

class Edge(models.Model):


    
    
class InputOutput(models.Model):
    
class Artefact(models.Model):            