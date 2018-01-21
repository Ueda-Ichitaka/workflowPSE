from django.db import models

INPUT_TYPES = (
    (0, 'ComplexData'),
    (1, 'LiteralData'),
    (2, 'BoundingBoxData'),
)

OUTPUT_TYPES = (
    (0, 'ComplexOutput'),
    (1, 'LiteralOutput'),
    (2, 'BoundingBoxOutput'),
)

class Workflow(models.Model):
    title = models.CharField(max_length=128)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    schema = models.TextField
    created_at = models.DateTimeField
    updated_at = models.DateTimeField

class ServiceProvider(models.Model):
    name = models.CharField(max_length=128)
    site = models.CharField(max_length=512)

class Service(models.Model):
    capabilities_url =  models.CharField(max_length=512)
    describe_url =  models.CharField(max_length=512)
    execute_url =  models.CharField(max_length=512)
    title = models.CharField(max_length=128)
    abstract = models.CharField(max_length=512)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)

class Process(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    abstract = models.CharField(max_length=512)

class ProcessOutput(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    abstract = models.CharField(max_length=512)
    min_occurs = models.SmallIntegerField()
    max_occurs = models.SmallIntegerField()
    type = models.CharField(max_length=1, choices=OUTPUT_TYPES)

class ProcessInput(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    abstract = models.CharField(max_length=512)
    min_occurs = models.SmallIntegerField()
    max_occurs = models.SmallIntegerField()
    type = models.CharField(max_length=1, choices=INPUT_TYPES)


