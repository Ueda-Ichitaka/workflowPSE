from django.test import TestCase
from base.models import WPSProvider
import base.cron
import xml.etree.ElementTree as ET


# Create your tests here.
class ParsingTestCase(TestCase):
    get_cap_url_from_scc_vm = 'base/testfiles/wpsGetCapabilities.xml'
    desc_proc_url_from_pywps_tut = 'base/testfiles/getCapabilitiesFromEsdiHumboldt.xml'
    xml_namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'xlink': 'http://www.w3.org/1999/xlink',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    capabilities_root = ET.parse(get_cap_url_from_scc_vm).getroot()

    def test_parse_service_provider_info(self):

        wps_provider = base.cron.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        self.assertEqual(wps_provider.provider_name, 'Organization Name')
        self.assertEqual(wps_provider.provider_site, 'http://pywps.org/')
        self.assertEqual(wps_provider.individual_name, 'Lastname, Firstname')
        self.assertEqual(wps_provider.position_name, 'Position Title')

    def test_parse_wps_server_info(self):
        wps_provider = base.cron.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        wps_server = base.cron.parse_wps_server_info(self.capabilities_root, self.xml_namespaces, wps_provider)
        self.assertEqual(wps_server.title, 'PyWPS Processing Service')
        self.assertEqual(wps_server.abstract, 'PyWPS is an implementation of the Web Processing '
                                              'Service standard from the Open Geospatial Consortium. PyWPS is written in Python.')
        self.assertEqual(wps_server.capabilities_url, 'http://localhost/wps')
        self.assertEqual(wps_server.describe_url, 'http://localhost/wps')
        self.assertEqual(wps_server.execute_url, 'http://localhost/wps')

    def test_describe_processes_parsing(self):
        wps_provider = base.cron.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        wps_server = base.cron.parse_wps_server_info(self.capabilities_root, self.xml_namespaces, wps_provider)
        base.cron.get_capabilities_parsing()



