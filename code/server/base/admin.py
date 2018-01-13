from django.contrib import admin
from base.models import *


# Register your models here.
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent_done', 'creator']

    class Meta:
        model = Workflow


class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'workflow', 'status', 'status_url']
    list_filter = ['workflow']

    class Meta:
        model = Task


class EdgeAdmin(admin.ModelAdmin):
    list_filter = ['workflow']

    class Meta:
        model = Edge


admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(Session)
admin.site.register(Process)
admin.site.register(Artefact)
admin.site.register(WPS)
admin.site.register(WPSProvider)
admin.site.register(InputOutput)