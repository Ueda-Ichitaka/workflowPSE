from django.shortcuts import render
from django.views.generic.base import TemplateView, RedirectView
from fireworks import Firework, LaunchPad, ScriptTask, FWorker
from fireworks.core.rocket_launcher import rapidfire
#from fireworks.scripts.lpad_run import webgui

# Create your views here.
class IndexView(TemplateView):
    template_name = "testFireworks/index.html"
    
    
class EditorView(TemplateView):
    template_name = "testFireworks/editor.html" 
    
class TaskerRedirectView(RedirectView):    
    
    permanent = True
    query_string = False
    pattern_name = 'webgui'
    
    def get_redirect_url(self, *args, **kwargs):
        
        # set up the LaunchPad and reset it
        launchpad = LaunchPad()#(host="127.0.0.1", port=27017, name="fw_tutorial", username="fwtestadmin", password="bla")
        launchpad.reset('', require_password=False)

        # create the Firework consisting of a single task
        ft1 = ScriptTask.from_str('echo "howdy, your job launched successfully!"')
        ft2 = ScriptTask.from_str('echo "hello world"')
        ft3 = ScriptTask.from_str('echo "where am i?"')
        firework = Firework([ft1, ft2, ft3])

        # store workflow and launch it locally
        launchpad.add_wf(firework)
        rapidfire(launchpad, FWorker())
        
        return super(TaskerRedirectView, self).get_redirect_url(*args, **kwargs)
    
class TaskView(TemplateView):
    template_name = "testFireworks/tasker.html"    
    