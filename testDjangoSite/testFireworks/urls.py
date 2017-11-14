from django.conf.urls import url

from . import views
from .views import IndexView, EditorView

app_name = 'testFireworks'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^editor/', EditorView.as_view(), name='editor'),
]