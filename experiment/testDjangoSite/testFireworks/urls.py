from django.conf.urls import url
from django.views.generic.base import RedirectView
from testFireworks.views import IndexView, EditorView, TaskerRedirectView, TaskView

app_name = 'testFireworks'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^editor/$', EditorView.as_view(), name='editor'),
    url(r'^tasker', TaskerRedirectView.as_view(url='taskOut'), name='tasker'),
    url(r'^taskOut', TaskView.as_view(), name='taskOut')
]