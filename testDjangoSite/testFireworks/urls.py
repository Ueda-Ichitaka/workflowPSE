from django.conf.urls import url
from django.views.generic.base import RedirectView
from testFireworks.views import IndexView, EditorView, TaskerRedirectView

app_name = 'testFireworks'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^editor/$', EditorView.as_view(), name='editor'),
    url(r'^tasker/$', TaskerRedirectView.as_view(url='http://heise.de'), name='tasker'),
    #url(r'^tasker/$', TaskerRedirectView.as_view(url='http://127.0.0.1:5000'), name='tasker'),
]