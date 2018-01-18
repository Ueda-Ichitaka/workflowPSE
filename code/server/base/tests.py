from django.test import TestCase
from base.models import WPS, WPSProvider
import xml.etree.ElementTree as ET


# Create your tests here.
class ParsingTestCase(TestCase):
    def test_capabilities_parsing(self):
        url_from_scc_vm = 'base/getCapabilitiesFromPyWPS.xml'

        xml_namespaces = {
            'gml': 'http://www.opengis.net/gml',
            'xlink': 'http://www.w3.org/1999/xlink',
            'wps': 'http://www.opengis.net/wps/1.0.0',
            'ows': 'http://www.opengis.net/ows/1.1',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        #Parse the xml file
        tree = ET.parse(url_from_scc_vm)
        root = tree.getroot()

        print(root.tag)

        #Parse service provider and save him
        service_provider_element = root.find('{http://www.opengis.net/ows/1.1}ServiceProvider')

        if service_provider_element is None:
            print('ERROR')
        else:
            provider_name = service_provider_element.find('ows:ProviderName', xml_namespaces).text
            provider_site = service_provider_element.find('ows:ProviderSite', xml_namespaces).attrib.get(
                '{' + xml_namespaces.get('xlink') + '}href')
            service_contact_element = service_provider_element.find('ows:ServiceContact', xml_namespaces)
            if service_contact_element is None:
                print('ERROR')
            else:
                individual_name = service_contact_element.find('ows:IndividualName', xml_namespaces).text
                position_name = service_contact_element.find('ows:PositionName', xml_namespaces).text

                provider = WPSProvider(provider_name=provider_name,
                                       provider_site=provider_site,
                                       individual_name=individual_name,
                                       position_name=position_name)
                provider.save()
        #Saving of service provider ends here

        #Parse wps server and save it
        service_identification_element = root.find('ows:ServiceIdentification', xml_namespaces)
        server_title = service_identification_element.find('ows:Title', xml_namespaces).text
        server_abstract = service_identification_element.find('ows:Abstract', xml_namespaces).text

        #server_get_capabilities_url = root.findall('ows:Operation')


        wps_server = WPS(service_provider=provider,
                         title=server_title,
                         abstract=server_abstract,
                         capabilities_url='http://test.net',
                         describe_url='http://test.net',
                         execute_url='http://test.net')

        wps_server.save()