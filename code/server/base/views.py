from django.shortcuts import render
from django.views import generic
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic import View
from django.views.generic import TemplateView
from .models import *


def as_json_response(list):
    return JsonResponse(list, safe=False)


class IndexView(TemplateView):
    template_name = "base/index.html"


class UserView(View):
    @staticmethod
    @require_GET
    def index(request):
        # TODO: Was not tested yet because of absence of user management in our project now
        return as_json_response(model_to_dict(request.user))


class WorkflowView(View):
    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(WorkflowView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, *args, **kwargs):
        if 'workflow_id' in kwargs:
            return as_json_response(model_to_dict(Workflow.objects.get(pk=kwargs['workflow_id'])))
        else:
            return as_json_response(list(Workflow.objects.all().values()))

    @staticmethod
    def post(request):
        workflow_form = WorkflowForm(request.POST)
        new_workflow = workflow_form.save()

        return as_json_response(model_to_dict(new_workflow))

    @staticmethod
    def patch(request, *args, **kwargs):
        workflow = WPS.objects.get(pk=kwargs['workflow_id'])
        workflow_form = WPSForm(request.POST, instance=workflow)
        workflow = workflow_form.save()

        return as_json_response(model_to_dict(workflow))

    @staticmethod
    def delete(request, *args, **kwargs):
        workflow = get_object_or_404(Workflow, pk=kwargs['workflow_id'])
        (deletedWorkflowCount, countOfDeletionsPerType) = workflow.delete()
        deleted = (deletedWorkflowCount > 0)

        return JsonResponse({'deleted': deleted})

    @staticmethod
    @require_GET
    def start(request, workflow_id):
        return JsonResponse({})

    @staticmethod
    @require_GET
    def stop(request, workflow_id):
        return JsonResponse({})


class ProcessView(View):
    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ProcessView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, *args, **kwargs):
        if 'process_id' in kwargs:
            process = Process.objects.get(pk=kwargs['process_id'])
            returned = model_to_dict(process)
            returned['inputs'] = list(process.inputoutput_set.all().filter(role=0).values())
            returned['outputs'] = list(process.inputoutput_set.all().filter(role=1).values())
            return as_json_response(returned)
        else:
            return as_json_response(list(Process.objects.all().values()))

    @staticmethod
    def post(request):
        process_form = ProcessForm(request.POST)
        new_process = process_form.save()

        return as_json_response(model_to_dict(new_process))

    @staticmethod
    def patch(request, *args, **kwargs):
        process = WPS.objects.get(pk=kwargs['process_id'])
        process_form = WPSForm(request.POST, instance=process)
        process = process_form.save()

        return as_json_response(model_to_dict(process))

    @staticmethod
    def delete(request, *args, **kwargs):
        process = get_object_or_404(Process, pk=kwargs['process_id'])
        (deletedProcessCount, countOfDeletionsPerType) = process.delete()
        deleted = (deletedProcessCount > 0)

        return JsonResponse({'deleted': deleted})


class WPSView(View):
    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(WPSView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, *args, **kwargs):
        if 'wps_id' in kwargs:
            return as_json_response(model_to_dict(WPS.objects.get(pk=kwargs['wps_id'])))
        else:
            return as_json_response(list(WPS.objects.all().values()))

    @staticmethod
    def post(request):
        wps_form = WPSForm(request.POST)
        new_wps = wps_form.save()

        return as_json_response(model_to_dict(new_wps))

    @staticmethod
    def patch(request, *args, **kwargs):
        wps = WPS.objects.get(pk=kwargs['wps_id'])
        wps_form = WPSForm(request.POST, instance=wps)
        wps = wps_form.save()

        return as_json_response(model_to_dict(wps))

    @staticmethod
    def delete(request, *args, **kwargs):
        wps = get_object_or_404(Process, pk=kwargs['wps_id'])
        (deletedWPSCount, countOfDeletionsPerType) = wps.delete()
        deleted = (deletedWPSCount > 0)

        return JsonResponse({'deleted': deleted})

    @staticmethod
    @require_GET
    def refresh(request):
        return JsonResponse({})


class WorkflowsView(TemplateView):
    template_name = "base/workflows.html"


class EditorView(TemplateView):
    template_name = "base/editor.html"


class SettingsView(TemplateView):
    template_name = "base/settings.html"
