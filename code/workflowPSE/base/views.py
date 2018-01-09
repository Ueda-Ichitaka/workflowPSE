from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "base/index.html"