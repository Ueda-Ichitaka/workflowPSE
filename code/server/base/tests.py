import os
import xml.etree.ElementTree as ET
from datetime import datetime

from django.test import TestCase

import base.cron
import base.utils as utils
from base.models import WPSProvider, WPS, Process, Workflow, Task, InputOutput, Artefact


class SchedulerTestCase(TestCase):
    """

    """
    dir_path = os.path.dirname(os.path.abspath(__file__))
    xmlDir = os.path.join(dir_path, 'testfiles/')

    def setUp(self):
        # user
        Workflow.objects.create(name="TestWF", description="tl;dr", percent_done='0', created_at=datetime.now(), creator='1')
        WPSProvider.objects.create(provider_name="Test Provider", provider_site="pse.rudolphrichard.de", individual_name="Rudolph, Richard",
                                   position_name="Software Engineer")
        WPS.objects.create(service_provider='1', title="PyWPS Testserver", abstract="tl;dr", capabilities_url="http://pse.rudolphrichard.de:5000/wps",
                           describe_url="http://pse.rudolphrichard.de:5000/wps", execute_url="http://pse.rudolphrichard.de:5000/wps")
        Process.objects.create(wps='1', identifier="say_hello", title="Process Say Hello", abstract="tl;dr")
        Task.objects.create(workflow='1', process='1', x='1', y='1', status='1', title="Say Hello Task", status_url="http://pse.rudolphrichard.de")
        InputOutput.objects.create(process='1', role='0', identifier="name", title="Input name", abstract="tl;dr", datatype='0', format="string",
                                   min_occurs='1', max_occurs='1')
        InputOutput.objects.create(process='1', role='1', identifier="response", title="Output name response", abstract="tl;dr", datatype='0',
                                   format="string",
                                   min_occurs='1', max_occurs='1')
        Artefact.objects.create(task='1', parameter='1', role='0', format="string", data="Ueda")

    def test_generate_XML(self):
        pass

    def test_send_task(self):
        base.cron.scheduler()
        task = Task.objects.get(title="Say Hello Task")
        self.assertContains(task.status_url, "http://pse.rudolphrichard.de:5000/outputs/")

    def test_execution(self):
        base.cron.scheduler()
        base.cron.receiver()
        base.cron.receiver()
        output = Artefact.objects.get(role='1', task='1', parameter='2')
        self.assertEqual(output.data, 'Hello Ueda')


# Create your tests here.
class ParsingTestCase(TestCase):
    """

    """
    get_cap_url_from_scc_vm = 'base/testfiles/wpsGetCapabilities.xml'
    desc_proc_url_from_scc_vm = 'base/testfiles/wpsDescribeProcesses.xml'
    xml_namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'xlink': 'http://www.w3.org/1999/xlink',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    capabilities_root = ET.parse(get_cap_url_from_scc_vm).getroot()
    describe_processes_root = ET.parse(desc_proc_url_from_scc_vm).getroot()

    def test_parse_service_provider_info(self):
        """

        @return:
        @rtype:
        """

        wps_provider = base.utils.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        self.assertEqual(wps_provider.provider_name, 'Organization Name')
        self.assertEqual(wps_provider.provider_site, 'http://pywps.org/')
        self.assertEqual(wps_provider.individual_name, 'Lastname, Firstname')
        self.assertEqual(wps_provider.position_name, 'Position Title')

    def test_parse_wps_server_info(self):
        """

        @return:
        @rtype:
        """
        wps_provider = base.utils.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        wps_server = base.utils.parse_wps_server_info(self.capabilities_root, self.xml_namespaces, wps_provider)
        self.assertEqual(wps_server.title, 'PyWPS Processing Service')
        self.assertEqual(wps_server.abstract, 'PyWPS is an implementation of the Web Processing '
                                              'Service standard from the Open Geospatial Consortium. PyWPS is written in Python.')
        self.assertEqual(wps_server.capabilities_url, 'http://localhost/wps')
        self.assertEqual(wps_server.describe_url, 'http://localhost/wps')
        self.assertEqual(wps_server.execute_url, 'http://localhost/wps')

    def test_add_wps_server(self):
        """

        @return:
        @rtype:
        """
        test_url = ['http://pse.rudolphrichard.de:5000']
        # base.utils.add_wps_server(test_url)
        base.cron.update_wps_processes()
        print(WPS.objects.all(), WPSProvider.objects.all())

        print(str(Process.objects.all().__len__()) + ' processes available')

    def test_overwrite_server(self):
        """

        @return:
        @rtype:
        """
        provider = base.utils.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        provider.save()
        old_database_entry = WPS(service_provider=provider,
                                 title='Title',
                                 abstract='Description',
                                 capabilities_url='http://pywps.org/capab',
                                 describe_url='http://pywps.org/desc',
                                 execute_url='http://pywps.org/exec')
        old_database_entry.save()
        new_entry = WPS(service_provider=provider,
                        title='Title',
                        abstract='new_Description',
                        capabilities_url='http://new_pywps.org/capab',
                        describe_url='http://new_pywps.org/desc',
                        execute_url='http://new_pywps.org/exec')

        base.utils.overwrite_server(old_database_entry, new_entry)
        new_database_entry = WPS.objects.get(title='Title')
        self.assertEqual(old_database_entry.pk, new_database_entry.pk)
        self.assertEqual(new_database_entry.abstract, new_entry.abstract)
        self.assertEqual(new_database_entry.capabilities_url, new_entry.capabilities_url)
        self.assertEqual(new_database_entry.describe_url, new_entry.describe_url)
        self.assertEqual(new_database_entry.execute_url, new_entry.execute_url)


class DatabaseSearcherTestCase(TestCase):
    """

    """
    wps_provider = None
    wps_server = None

    def create_and_save_wps_provider(self):
        """

        @return:
        @rtype:
        """
        self.wps_provider = WPSProvider(provider_name='Help Service - Remote Sensing',
                                        provider_site='http://bnhelp.cz',
                                        individual_name='Jachym Cepicky',
                                        position_name='developer')
        self.wps_provider.save()

    def create_and_save_wps_server(self):
        """

        @return:
        @rtype:
        """
        self.create_and_save_wps_provider()
        self.wps_server = WPS(service_provider=self.wps_provider,
                              title='PyWPS Example deploy server',
                              abstract='Instance of PyWPS, for testing and teaching purposes.',
                              capabilities_url='http://appd.esdi-humboldt.cz/pywps/?',
                              describe_url='http://appd.esdi-humboldt.cz/pywps/?',
                              execute_url='http://appd.esdi-humboldt.cz/pywps/?')
        self.wps_server.save()

    def test_search_provider_in_database_1(self):
        """

        @return:
        @rtype:
        """
        self.create_and_save_wps_provider()
        provider_from_database = utils.search_provider_in_database(self.wps_provider)
        self.assertIsNotNone(provider_from_database)

    def test_search_provider_in_database_2(self):
        """

        @return:
        @rtype:
        """
        provider_from_database = utils.search_provider_in_database(self.wps_provider)
        self.assertIsNone(provider_from_database)

    def test_search_server_in_database_1(self):
        """

        @return:
        @rtype:
        """
        self.create_and_save_wps_server()
        server_from_database = utils.search_server_in_database(self.wps_server)
        self.assertIsNotNone(server_from_database)

    def test_search_server_in_database_2(self):
        """

        @return:
        @rtype:
        """
        server_from_database = utils.search_server_in_database(self.wps_server)
        self.assertIsNone(server_from_database)


class CronTestCase(TestCase):
    def test_update_wps_processes_with_empty_database(self):
        self.assertEqual(Process.objects.all().__len__(), 0)
        base.cron.update_wps_processes()
        self.assertEqual(Process.objects.all().__len__(), 0)
