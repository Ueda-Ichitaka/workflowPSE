from django.db import models
from pymongo.message import MAX_INT32

# Create your models here.

    
class DataTypes(models.Model):
    type_value = models.CharField(max_length=200)
    
    
class ProcessStatus(models.Model):
    status_value = models.CharField(max_length=200)    
    

class Process(models.Model):
    process_identifier = models.CharField(max_length=200)
    process_title = models.CharField(max_length=200)
    process_abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    process_workflow = models.DecimalField(max_digits=20, decimal_places=20)
    process_status = models.ForeignKey(ProcessStatus, on_delete=models.CASCADE)
    
    
class Inputs(models.Model):
    process_id = models.ForeignKey(Process, on_delete=models.CASCADE)
    input_identifier = models.CharField(max_length=200)
    input_title = models.CharField(max_length=200)
    input_abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    input_type = models.ForeignKey(DataTypes, on_delete=models.CASCADE)
    input_max_occurs = models.DecimalField(max_digits=10, decimal_places=10)
    input_max_occurs = models.DecimalField(max_digits=10, decimal_places=10)
    input_value = models.CharField(max_length=200)
    
    
class Outputs(models.Model):
    process_id = models.ForeignKey(Process, on_delete=models.CASCADE)
    output_identifier = models.CharField(max_length=200)
    output_title = models.CharField(max_length=200)
    output_abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    output_type = models.ForeignKey(DataTypes, on_delete=models.CASCADE)
    output_max_occurs = models.DecimalField(max_digits=10, decimal_places=10)
    output_max_occurs = models.DecimalField(max_digits=10, decimal_places=10)
    output_value = models.CharField(max_length=200)
    

class Workflow(models.Model):
    workflow_title = models.CharField(max_length=200)
    workflow_status = models.CharField(max_length=200)
    workflow_num_processes = models.DecimalField(max_digits=10, decimal_places=10)
            
            