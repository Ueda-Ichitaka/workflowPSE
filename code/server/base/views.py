from django.shortcuts import render
from django.views import generic
from django.http import JsonResponse
from django.views.generic import View
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "base/index.html"


class UserView(View):
    def index(request):
        return JsonResponse({})


class WorkflowView(View):
    def index(request):
        return JsonResponse({})

    def get(request, workflowId):
        return JsonResponse({})

    def create(request):
        return JsonResponse({})

    def update(request, workflowId):
        return JsonResponse({})

    def delete(request, workflowId):
        return JsonResponse({})

    def start(request, workflowId):
        return JsonResponse({})

    def stop(request, workflowId):
        return JsonResponse({})


class ProcessView(View):
    def index(request):
        return JsonResponse({})

    def get(request, processId):
        return JsonResponse({})

    def create(request):
        return JsonResponse({})

    def update(request, processId):
        return JsonResponse({})

    def delete(request, processId):
        return JsonResponse({})


class WPSView(View):
    def index(request):
        return JsonResponse({})

    def get(request, wpsId):
        return JsonResponse({})

    def create(request):
        return JsonResponse({})

    def update(request, wpsId):
        return JsonResponse({})

    def delete(request, wpsId):
        return JsonResponse({})

    def refresh(request, wpsId):
        return JsonResponse({})


class WorkflowsView(TemplateView):
    template_name = "base/workflows.html"


class EditorView(TemplateView):
    template_name = "base/editor.html"


class SettingsView(TemplateView):
    template_name = "base/settings.html"
