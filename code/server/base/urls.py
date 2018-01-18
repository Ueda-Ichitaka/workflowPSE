from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'base'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    path('user/index/', views.UserView.index),

    path('workflow/index/', views.WorkflowView.index),
    path('workflow/get/<int:workflow_id>', views.WorkflowView.get),
    path('workflow/create', views.WorkflowView.create),
    path('workflow/update/<int:workflow_id>', views.WorkflowView.update),
    path('workflow/delete/<int:workflow_id>', views.WorkflowView.delete),
    path('workflow/start/<int:workflow_id>', views.WorkflowView.start),
    path('workflow/stop/<int:workflow_id>', views.WorkflowView.stop),

    path('process/index/', views.ProcessView.index),
    path('process/get/<int:process_id>', views.ProcessView.get),
    path('process/create', views.ProcessView.create),
    path('process/update/<int:process_id>', views.ProcessView.update),
    path('process/delete/<int:process_id>', views.ProcessView.delete),

    path('wps/index/', views.WPSView.index),
    path('wps/get/<int:wps_id>', views.WPSView.get),
    path('wps/create', views.WPSView.create),
    path('wps/update/<int:wps_id>', views.WPSView.update),
    path('wps/delete/<int:wps_id>', views.WPSView.delete),
    path('wps/refresh/<int:wps_id>', views.WPSView.refresh),

    url(r'^workflows/', views.WorkflowsView.as_view(), name='workflows'),
    url(r'^editor/', views.EditorView.as_view(), name='editor'),
    url(r'^settings/', views.SettingsView.as_view(), name='settings'),
]