from django.db import models
from django.contrib.auth.models import User

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
    creator = models.ForeignKey(User, editable=False, related_name='creator_user', on_delete=models.CASCADE)
    last_modifier = models.ForeignKey(User, editable=True, null=True, blank=True, on_delete=models.SET_NULL)
    

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
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    x = models.DecimalField(max_digits=5, decimal_places=0)
    y = models.DecimalField(max_digits=5, decimal_places=0)
    status = models.CharField(max_length=1, choices=STATUS)
    title = models.CharField(max_length=200)
    abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    status_url = models.URLField(max_length=1000)
    started_at = models.DateTimeField(auto_now=False, auto_now_add=False)


class Session(models.Model):
    user = models.ForeignKey(User, editable= False, on_delete=models.CASCADE)
    last_workflow = models.ForeignKey(Workflow, null=True, on_delete=models.SET_NULL)


class InputOutput(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=ROLE)
    identifier = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    datatype = models.CharField(max_length=1, choices=DATATYPE)
    min_occurs = models.IntegerField()
    max_occurs = models.IntegerField()


class Edge(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    from_task = models.ForeignKey(Task, related_name='out_task', on_delete=models.CASCADE) #rename to out_task?
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE)  #rename to in_task?
    input = models.ForeignKey(InputOutput, related_name='input', null=True, on_delete=models.SET_NULL)
    output =models.ForeignKey(InputOutput, null=True, on_delete=models.SET_NULL)
    
    
class Artefact(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    parameter = models.ForeignKey(InputOutput, null=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=1, choices=ROLE)
    format = models.CharField(max_length=200)
    data = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False)
