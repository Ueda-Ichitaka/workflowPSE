from django.test import TestCase
import base.cron
import xml.etree.ElementTree as ET


# Create your tests here.
class ParsingTestCase(TestCase):
    url_from_scc_vm = 'base/testfiles/getCapabilitiesFromPyWPS.xml'
    url_from_pywps_tut = 'base/testfiles/getCapabilitiesFromEsdiHumboldt.xml'
    xml_namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'xlink': 'http://www.w3.org/1999/xlink',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    def test_parse_service_provider_info_1(self):
        root = ET.parse(self.url_from_scc_vm).getroot()

        wps_provider = base.cron.parse_service_provider_info(root, self.xml_namespaces)
        self.assertEqual(wps_provider.provider_name, 'Organization Name')
        self.assertEqual(wps_provider.provider_site, 'http://pywps.org/')
        self.assertEqual(wps_provider.individual_name, 'Lastname, Firstname')
        self.assertEqual(wps_provider.position_name, 'Position Title')

    def test_parse_service_provider_info_2(self):
        root = ET.parse(self.url_from_pywps_tut).getroot()

        wps_provider = base.cron.parse_service_provider_info(root, self.xml_namespaces)
        self.assertEqual(wps_provider.provider_name, 'Help Service - Remote Sensing')
        self.assertEqual(wps_provider.provider_site, 'http://bnhelp.cz')
        self.assertEqual(wps_provider.individual_name, 'Jachym Cepicky')
        self.assertEqual(wps_provider.position_name, 'developer')

