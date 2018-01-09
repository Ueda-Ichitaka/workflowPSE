from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.

class Session(models.Model):
    user = models.ForeignKey(User, editable= False)
    last_workflow = models.ForeignKey(Workflow)
    
    #def __str__(self):
     #   return self.type_value