from rest_framework import serializers
from flow.models import Service, ServiceProvider


class ServiceSerializer(serializers.ModelSerializer):
   class Meta:
       model = Service
       fields = ('capabilities_url', 'describe_url', 'execute_url', 'title', 'abstract', 'provider')

class ServiceProviderSerializer(serializers.ModelSerializer):
   class Meta:
       model = ServiceProvider
       fields = ('name', 'site')