from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from base import views

app_name = 'base'
urlpatterns = [
    url(r'^$', views.EditorView.as_view(), name='index'),

    path('user/', views.UserView.as_view()),

    path('workflow/', views.WorkflowView.as_view()),
    path('workflow/<int:workflow_id>', views.WorkflowView.as_view()),
    path('workflow_start/<int:workflow_id>', views.WorkflowView.start),
    path('workflow_stop/<int:workflow_id>', views.WorkflowView.stop),
    path('workflow_refresh/<int:workflow_id>', views.WorkflowView.refresh),

    path('process/', views.ProcessView.as_view()),
    path('process/<int:process_id>', views.ProcessView.as_view()),

    path('wps/', views.WPSView.as_view()),
    path('wps/<int:wps_id>', views.WPSView.as_view()),
    path('wps_refresh/', views.WPSView.refresh),

    url(r'^workflows/', views.WorkflowsView.as_view(), name='workflows'),
    url(r'^editor/', views.EditorView.as_view(), name='editor'),
    url(r'^settings/', views.SettingsView.as_view(), name='settings'),

    url(r'^login/', views.OurLoginView.as_view(), name='login'),
    url(r'^logout/', views.OurLogoutView.as_view(), name='logout')
]
