from django.shortcuts import render
from django.views.generic.base import TemplateView


# Create your views here.
class IndexView(TemplateView):
    template_name = "testFireworks/index.html"
    
    
class EditorView(TemplateView):
    template_name = "testFireworks/editor.html" 
    
