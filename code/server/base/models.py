from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from enum import Enum

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, editable=True, related_name='creator_user', on_delete=models.CASCADE)
    #Hab absichtlich editable auf true gesetzt, weil sonst taucht ein Fehler auf. Django kann nicht den creator id finden...

    last_modifier = models.ForeignKey(User, editable=True, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"

    def __str__(self):
        return self.name


class WPSProvider(models.Model):
    provider_name = models.CharField(max_length=200)
    provider_site = models.URLField(max_length=1000)
    individual_name = models.CharField(max_length=200)
    position_name = models.CharField(max_length=200)

    class Meta:
        verbose_name = "WPSProvider"
        verbose_name_plural = "WPSProviders"

    def __str__(self):
        return self.provider_name


class WPS(models.Model):
    service_provider = models.ForeignKey(WPSProvider, on_delete=models.CASCADE)
    title = models.CharField(max_length = 200)
    abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    capabilities_url = models.URLField(max_length=1000)
    describe_url = models.URLField(max_length=1000)
    execute_url = models.URLField(max_length=1000)    

    class Meta:
        verbose_name = "WPS"
        verbose_name_plural = "WPS"

    def __str__(self):
        return self.title


class Process(models.Model):
    wps = models.ForeignKey(WPS, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')

    class Meta:
        verbose_name = "Process"
        verbose_name_plural = "Processes"

    def __str__(self):
        return "%s from Server '%s'" % (self.title, self.wps.title)


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

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return "%s from Workflow '%s'" % (self.title, self.workflow.name)


class Session(models.Model):
    user = models.ForeignKey(User, editable= False, on_delete=models.CASCADE)
    last_workflow = models.ForeignKey(Workflow, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"


class InputOutput(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=ROLE)
    identifier = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    datatype = models.CharField(max_length=1, choices=DATATYPE, null=True)
    format = models.CharField(max_length=200, null=True)
    min_occurs = models.IntegerField()
    max_occurs = models.IntegerField()

    class Meta:
        verbose_name = "InputOutput"
        verbose_name_plural = "InputOutputs"

    def __str__(self):
        input_or_output = 'Input' if self.role == '0' else 'Output'
        return input_or_output + " of Process '" + self.process.title + "'"


class Edge(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    from_task = models.ForeignKey(Task, related_name='out_task', on_delete=models.CASCADE) #rename to out_task?
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE)  #rename to in_task?
    input = models.ForeignKey(InputOutput, related_name='input', null=True, on_delete=models.SET_NULL)
    output =models.ForeignKey(InputOutput, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Edge"
        verbose_name_plural = "Edges"

    def __str__(self):
        return self.from_task.title + " to " + self.to_task.title + " (" + self.workflow.name + ")"

    
class Artefact(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    parameter = models.ForeignKey(InputOutput, null=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=1, choices=ROLE)
    format = models.CharField(max_length=200)
    data = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name = "Artefact"
        verbose_name_plural = "Artefacts"


class WorkflowForm(ModelForm):
    class Meta:
        model = Workflow
        fields = '__all__'


class ProcessForm(ModelForm):
    class Meta:
        model = Process
        fields = '__all__'


class WPSForm(ModelForm):
    class Meta:
        model = WPS
        fields = '__all__'
