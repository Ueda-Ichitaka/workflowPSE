from django.contrib import admin
from base.models import Session, Workflow, Task, Edge, Process, Artefact, WPS, WPSProvider, InputOutput

# Register your models here.

admin.site.register(Session)
admin.site.register(Workflow)
admin.site.register(Task)
admin.site.register(Edge)
admin.site.register(Process)
admin.site.register(Artefact)
admin.site.register(WPS)
admin.site.register(WPSProvider)
admin.site.register(InputOutput)