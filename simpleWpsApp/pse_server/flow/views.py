from django.shortcuts import render
from django.http import QueryDict
from flow.models import Service, ServiceProvider
from flow.serializers import ServiceSerializer, ServiceProviderSerializer
from rest_framework import generics, mixins, status
from rest_framework.response import Response
import xml.etree.ElementTree as etree
import requests


# Serve Web App
def index(request):
    return render(request, 'index.html')

# Service Provider Api
class ServiceProviderList(generics.ListAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer

class ServiceProviderDetail(generics.RetrieveDestroyAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer

# Service Api
class ServiceList(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        capabilities_url = 'http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService'
        capabilities_xml = '<?xml version="1.0" encoding="UTF-8"?><wps:GetCapabilities service="WPS" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_request.xsd"><wps:AcceptVersions><ows:Version xmlns:ows="http://www.opengis.net/ows/1.1">1.0.0</ows:Version></wps:AcceptVersions></wps:GetCapabilities>'

        result = requests.post(capabilities_url, capabilities_xml).text


        # Parse Result
        root = etree.fromstring(result)

        ns = {
            'wps': 'http://www.opengis.net/wps/1.0.0',
            'xlink': 'http://www.w3.org/1999/xlink',
            'ows': 'http://www.opengis.net/ows/1.1',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        sp = root.find('ows:ServiceProvider', ns)
        si = root.find('ows:ServiceIdentification', ns)
        om = root.find('ows:OperationsMetadata', ns)
        po = root.find('wps:ProcessOfferings', ns)

        # Service Provider
        provider_name = sp.find('ows:ProviderName', ns).text
        provider_site = sp.find('ows:ProviderSite', ns).attrib['{http://www.w3.org/1999/xlink}href']

        # Service
        service_title = si.find('ows:Title', ns).text
        service_abstract = si.find('ows:Abstract', ns).text


        url = lambda name: om.find(f"./ows:Operation[@name='{name}']/ows:DCP/ows:HTTP/ows:Post", ns).attrib['{http://www.w3.org/1999/xlink}href']

        service_capabilities_url = url('GetCapabilities')
        service_describe_url = url('DescribeProcess')
        service_execute_url = url('Execute')


        # Save Provider data
        provider = ServiceProvider(name=provider_name, site=provider_site)
        provider.save()


        # Save Service data
        serializerService = ServiceSerializer(data={
            'capabilities_url': capabilities_url,
            'describe_url': service_describe_url,
            'execute_url': service_execute_url,
            'title': service_title,
            'abstract': service_abstract,
            'provider': provider.id,
        })

        if not serializerService.is_valid():
            return Response(serializerService.errors, status=status.HTTP_400_BAD_REQUEST)

        serializerService.save()

        return Response(serializerService.data, status=status.HTTP_201_CREATED)


class ServiceDetail(generics.RetrieveDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
