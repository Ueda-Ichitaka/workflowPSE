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

    # TODO: all TODO's in this view for are effective for corresponding methods in other views
    @staticmethod
    def get(request, *args, **kwargs):
        if 'process_id' in kwargs:
            return as_json_response(model_to_dict(Workflow.objects.get(pk=kwargs['process_id'])))
        else:
            return as_json_response(list(Workflow.objects.all().values()))

    @staticmethod
    def post(request):
        workflow_form = WorkflowForm(request.POST)
        new_workflow = workflow_form.save()

        # TODO: return something more than ID?
        return JsonResponse(model_to_dict(new_workflow))

    @staticmethod
    def patch(request, *args, **kwargs):
        workflow = WPS.objects.get(pk=kwargs['process_id'])
        workflow_form = WPSForm(request.POST, instance=workflow)
        workflow_form.save()

        return JsonResponse({})

    @staticmethod
    def delete(request, *args, **kwargs):
        workflow = get_object_or_404(Workflow, pk=kwargs['process_id'])
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
    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ProcessView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, *args, **kwargs):
        if 'process_id' in kwargs:
            return as_json_response(model_to_dict(Process.objects.get(pk=kwargs['process_id'])))
        else:
            return as_json_response(list(Process.objects.all().values()))

    @staticmethod
    def post(request):
        process_form = ProcessForm(request.POST)
        new_process = process_form.save()

        return JsonResponse({'id': new_process.pk})

    @staticmethod
    def patch(request, *args, **kwargs):
        process = WPS.objects.get(pk=kwargs['process_id'])
        process_form = WPSForm(request.POST, instance=process)
        process_form.save()

        return JsonResponse({})

    @staticmethod
    def delete(request, *args, **kwargs):
        process = get_object_or_404(Process, pk=kwargs['process_id'])
        process.delete()

        return JsonResponse({})


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

        return JsonResponse({'id': new_wps.pk})

    @staticmethod
    def patch(request, *args, **kwargs):
        wps = WPS.objects.get(pk=kwargs['wps_id'])
        wps_form = WPSForm(request.POST, instance=wps)
        wps_form.save()

        return JsonResponse({})

    @staticmethod
    def delete(request, *args, **kwargs):
        wps = get_object_or_404(WPS, pk=kwargs['wps_id'])
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
