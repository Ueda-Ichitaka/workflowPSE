from django.db import models
from django.db.models.deletion import CASCADE
#from pymongo.message import MAX_INT32

# Create your models here.

    
class DataType(models.Model):
    type_value = models.CharField(max_length=200)
    
    def __str__(self):
        return self.type_value
    
    
class ProcessStatus(models.Model):
    status_value = models.CharField(max_length=200)    
    
    def __str__(self):
        return self.status_value

class WorkflowStatus(models.Model):
    status_value = models.CharField(max_length=200)    
    
    def __str__(self):
        return self.status_value


class Workflow(models.Model):
    workflow_title = models.CharField(max_length=200)
    workflow_status = models.ForeignKey(WorkflowStatus, on_delete=CASCADE)
    workflow_num_processes = models.DecimalField(max_digits=10, decimal_places=0)
    
    def __str__(self):
        return self.workflow_title


class Process(models.Model):
    process_identifier = models.CharField(max_length=200)
    process_title = models.CharField(max_length=200)
    process_abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    process_workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    #process_workflow = models.DecimalField(max_digits=20, decimal_places=20)
    process_status = models.ForeignKey(ProcessStatus, on_delete=models.CASCADE)
    
    
class Input(models.Model):
    process_id = models.ForeignKey(Process, on_delete=models.CASCADE)
    input_identifier = models.CharField(max_length=200)
    input_title = models.CharField(max_length=200)
    input_abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    input_type = models.ForeignKey(DataType, on_delete=models.CASCADE)
    input_max_occurs = models.DecimalField(max_digits=10, decimal_places=10)
    input_max_occurs = models.DecimalField(max_digits=10, decimal_places=10)
    input_value = models.CharField(max_length=200)
    
    
class Output(models.Model):
    process_id = models.ForeignKey(Process, on_delete=models.CASCADE)
    output_identifier = models.CharField(max_length=200)
    output_title = models.CharField(max_length=200)
    output_abstract = models.TextField('Descriptive text', default='Add your super descriptive text here...')
    output_type = models.ForeignKey(DataType, on_delete=models.CASCADE)
    output_max_occurs = models.DecimalField(max_digits=10, decimal_places=10)
    output_max_occurs = models.DecimalField(max_digits=10, decimal_places=10)
    output_value = models.CharField(max_length=200)
    


            
            