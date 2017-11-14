from django.conf.urls import url

from . import views
from .views import IndexView

app_name = 'base'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
]