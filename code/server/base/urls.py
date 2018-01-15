from django.conf.urls import url

from . import views

app_name = 'base'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^user/', views.UserView.as_view(), name='user'),
    url(r'^workflow/', views.WorkflowView.as_view(), name='workflow'),
    url(r'^process/', views.ProcessView.as_view(), name='process'),
    url(r'^wps/', views.WPSView.as_view(), name='wps'),
    url(r'^workflows/', views.WorkflowsView.as_view(), name='workflows'),
    url(r'^editor/', views.EditorView.as_view(), name='editor'),
    url(r'^settings/', views.SettingsView.as_view(), name='settings'),
]