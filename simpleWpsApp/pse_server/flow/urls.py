from django.conf.urls import url, include
from . import views

urlpatterns = [
    # Serve web app
    url(r'^$', views.index),

    # Service api
    url(r'^service/$', views.ServiceList.as_view()),
    url(r'^service/(?P<pk>[0-9]+)/$', views.ServiceDetail.as_view()),

    # Service Provider api
    url(r'^service-provider/$', views.ServiceProviderList.as_view()),
    url(r'^service-provider/(?P<pk>[0-9]+)/$', views.ServiceProviderDetail.as_view()),

    # Auth
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
