from django.contrib import admin

from testWPS.models import Input, Output, Process, ProcessStatus, Workflow, DataType, WorkflowStatus

admin.site.register(Input)
admin.site.register(Output)
admin.site.register(Process)
admin.site.register(ProcessStatus)
admin.site.register(Workflow)
admin.site.register(DataType)
admin.site.register(WorkflowStatus)


# Register your models here.
