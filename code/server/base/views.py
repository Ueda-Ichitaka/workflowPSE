from django.shortcuts import render
from django.views import generic
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.views.generic import TemplateView
from django.views.decorators.http import require_GET, require_POST, require_http_methods
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
    # TODO: all TODO's in this view for are effective for corresponding methods in other views
    @staticmethod
    @require_GET
    def index(request):
        return as_json_response(list(Workflow.objects.all().values()))

    @staticmethod
    @require_POST
    def create(request):
        # TODO: validation needed?
        workflow_form = WorkflowForm(request.POST)
        new_workflow = workflow_form.save()

        # TODO: return something more than ID?
        return JsonResponse({'id': new_workflow.pk})

    @staticmethod
    @require_GET
    def get(request, workflow_id):
        workflow = model_to_dict(Workflow.objects.get(pk=workflow_id))
        return as_json_response(workflow)

    @staticmethod
    @require_http_methods(['PATCH'])
    def update(request, workflow_id):
        workflow = WPS.objects.get(pk=workflow_id)
        workflow_form = WPSForm(request.POST, instance=workflow)
        workflow_form.save()

        return JsonResponse({})

    @staticmethod
    @require_http_methods(['DELETE'])
    def delete(request, workflow_id):
        workflow = get_object_or_404(Workflow, pk=workflow_id)
        workflow.delete()

        # TODO: return something?
        return JsonResponse({})

    @staticmethod
    @require_GET
    def start(request, workflow_id):
        return JsonResponse({})

    @staticmethod
    @require_GET
    def stop(request, workflow_id):
        return JsonResponse({})


class ProcessView(View):
    @staticmethod
    @require_GET
    def index(request):
        return as_json_response(list(Process.objects.all().values()))

    @staticmethod
    @require_POST
    def create(request):
        process_form = ProcessForm(request.POST)
        new_process = process_form.save()

        return JsonResponse({'id': new_process.id})

    @staticmethod
    @require_GET
    def get(request, process_id):
        process = model_to_dict(Process.objects.get(pk=process_id))
        return as_json_response(process)

    @staticmethod
    @require_http_methods(['PATCH'])
    def update(request, process_id):
        process = Process.objects.get(pk=process_id)
        process_form = ProcessForm(request.POST, instance=process)
        process_form.save()

        return JsonResponse({})

    @staticmethod
    @require_http_methods(['DELETE'])
    def delete(request, process_id):
        process = get_object_or_404(Process, pk=process_id)
        process.delete()

        return JsonResponse({})


class WPSView(View):
    @staticmethod
    @require_GET
    def index(request):
        return as_json_response(list(WPS.objects.all().values()))

    @staticmethod
    @require_POST
    def create(request):
        wps_form = WPSForm(request.POST)
        new_wps = wps_form.save()

        return JsonResponse({'id': new_wps.pk})

    @staticmethod
    @require_GET
    def get(request, wps_id):
        wps = model_to_dict(WPS.objects.get(pk=wps_id))
        return as_json_response(wps)

    @staticmethod
    @require_http_methods(['PATCH'])
    def update(request, wps_id):
        wps = WPS.objects.get(pk=wps_id)
        wps_form = WPSForm(request.POST, instance=wps)
        wps_form.save()

        return JsonResponse({})

    @staticmethod
    @require_http_methods(['DELETE'])
    def delete(request, wps_id):
        wps = get_object_or_404(WPS, pk=wps_id)
        wps.delete()

        return JsonResponse({})

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
