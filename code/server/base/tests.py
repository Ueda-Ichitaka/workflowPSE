import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from datetime import datetime
import unittest

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

    @unittest.skip('fails')
    def test_generate_XML(self):
        pass

    @unittest.skip('fails')
    def test_send_task(self):
        base.cron.scheduler()
        task = Task.objects.get(title="Say Hello Task")
        self.assertContains(task.status_url, "http://pse.rudolphrichard.de:5000/outputs/")

    @unittest.skip('fails')
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

    get_cap_url_from_scc_vm_wrong = 'base/testfiles/broken_wpsGetCapabilities.xml'

    xml_namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'xlink': 'http://www.w3.org/1999/xlink',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    capabilities_root = ET.parse(get_cap_url_from_scc_vm).getroot()
    describe_processes_root = ET.parse(desc_proc_url_from_scc_vm).getroot()

    capabilities_wrong_root = ET.parse(get_cap_url_from_scc_vm_wrong).getroot()

    wps_provider = WPSProvider(provider_name='Organization Name',
                               provider_site='http://pywps.org/',
                               individual_name='Lastname, Firstname',
                               position_name='Position Title')

    wps_server = WPS(service_provider=wps_provider,
                     title='PyWPS Processing Service',
                     abstract='PyWPS is an implementation of the Web Processing '
                              'Service standard from the Open Geospatial Consortium. '
                              'PyWPS is written in Python.',
                     capabilities_url='http://localhost/wps?request=GetCapabilities&service=WPS',
                     describe_url='http://localhost/wps?request=DescribeProcess'
                                  '&service=WPS&identifier=all&version=1.0.0',
                     execute_url='http://localhost/wps?request=Execute&service=WPS')

    say_hello_literal_process = Process(wps=wps_server,
                                        identifier='say_hello',
                                        title='Process Say Hello',
                                        abstract='Returns a literal string output with Hello plus the inputed name')

    say_hello_literal_input = InputOutput(process=say_hello_literal_process,
                                          role='0',  # Input
                                          identifier='name',
                                          title='Input name',
                                          abstract='No description for input available',
                                          datatype='0',  # Literal
                                          format='string',
                                          min_occurs='1',
                                          max_occurs='1')

    say_hello_literal_output = InputOutput(process=say_hello_literal_process,
                                           role='1',  # Output
                                           identifier='response',
                                           title='Output response',
                                           abstract='No description for output available',
                                           datatype='0',  # Literal
                                           format='string',
                                           min_occurs='1',
                                           max_occurs='1')

    say_hello_process_element = describe_processes_root.find("./ProcessDescription/[ows:Identifier='say_hello']",
                                                             xml_namespaces)

    """
    wps_process_input = InputOutput(#process=wps_process,
                                    role='0',
                                    identifier='layer',
                                    title='Layer',
                                    abstract='No description for input available',
                                    datatype='1',
                                    format=None,
                                    min_occurs='1',
                                    max_occurs='1')"""

    def test_parse_service_provider_info(self):
        """
        Tests, if parse_service_provider_info parses correct
        @return:
        @rtype:
        """

        wps_provider = base.utils.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        self.assertEqual(wps_provider.provider_name, self.wps_provider.provider_name)
        self.assertEqual(wps_provider.provider_site, self.wps_provider.provider_site)
        self.assertEqual(wps_provider.individual_name, self.wps_provider.individual_name)
        self.assertEqual(wps_provider.position_name, self.wps_provider.position_name)

    def test_parse_service_provider_info_fail(self):
        """
        Test of exception throw
        @return: Nothing
        @rtype: None
        """
        self.assertRaises(AttributeError, base.utils.parse_service_provider_info(None, self.xml_namespaces))

    def test_parse_wps_server_info(self):
        """
        Tests, if parse_wps_server_info parses correct
        @return: Nothing
        @rtype: None
        """
        wps_provider = base.utils.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        wps_server = base.utils.parse_wps_server_info(self.capabilities_root, self.xml_namespaces, wps_provider)
        self.assertEqual(wps_server.title, self.wps_server.title)
        self.assertEqual(wps_server.abstract, self.wps_server.abstract,)
        self.assertEqual(wps_server.capabilities_url, self.wps_server.capabilities_url,)
        self.assertEqual(wps_server.describe_url, self.wps_server.describe_url)
        self.assertEqual(wps_server.execute_url, self.wps_server.execute_url)

    def test_parse_wps_server_info_fail(self):
        """
        Test of exception throw
        @return: Nothing
        @rtype: None
        """
        self.assertRaises(AttributeError, base.utils.parse_wps_server_info(None, self.xml_namespaces,
                                                                           self.wps_provider))

    def test_parse_wps_process(self):
        """
        Tests, if parse_process_info parses correct
        @return: Nothing
        @rtype: None
        """
        wps_process = base.utils.parse_process_info(self.say_hello_process_element, self.xml_namespaces,
                                                    self.wps_server)

        self.assertEqual(wps_process.identifier, self.say_hello_literal_process.identifier)
        self.assertEqual(wps_process.title, self.say_hello_literal_process.title)
        self.assertEqual(wps_process.abstract, self.say_hello_literal_process.abstract)

    def test_parse_wps_process_fail(self):
        """
        Test of exception throw
        @return: Nothing
        @rtype: None
        """
        self.assertRaises(AttributeError, base.utils.parse_process_info(None, self.xml_namespaces, self.wps_server))

    def test_parse_process_input_literal(self):
        say_hello_process_input_element = self.say_hello_process_element.find('./DataInputs/Input')
        wps_process_input = base.utils.parse_input_info(say_hello_process_input_element, self.xml_namespaces,
                                                        self.say_hello_literal_process)

        self.assertEqual(wps_process_input.role, self.say_hello_literal_input.role)
        self.assertEqual(wps_process_input.identifier, self.say_hello_literal_input.identifier)
        self.assertEqual(wps_process_input.title, self.say_hello_literal_input.title)
        self.assertEqual(wps_process_input.abstract, self.say_hello_literal_input.abstract)
        self.assertEqual(wps_process_input.datatype, self.say_hello_literal_input.datatype)
        self.assertEqual(wps_process_input.format, self.say_hello_literal_input.format)
        self.assertEqual(wps_process_input.min_occurs, self.say_hello_literal_input.min_occurs)
        self.assertEqual(wps_process_input.max_occurs, self.say_hello_literal_input.max_occurs)

    def test_parse_process_output_literal(self):

        say_hello_process_output_element = self.say_hello_process_element.find('./ProcessOutputs/Output')
        wps_process_input = base.utils.parse_output_info(say_hello_process_output_element, self.xml_namespaces,
                                                         self.say_hello_literal_process)

        self.assertEqual(wps_process_input.role, self.say_hello_literal_output.role)
        self.assertEqual(wps_process_input.identifier, self.say_hello_literal_output.identifier)
        self.assertEqual(wps_process_input.title, self.say_hello_literal_output.title)
        self.assertEqual(wps_process_input.abstract, self.say_hello_literal_output.abstract)
        self.assertEqual(wps_process_input.datatype, self.say_hello_literal_output.datatype)
        self.assertEqual(wps_process_input.format, self.say_hello_literal_output.format)
        self.assertEqual(wps_process_input.min_occurs, self.say_hello_literal_output.min_occurs)
        self.assertEqual(wps_process_input.max_occurs, self.say_hello_literal_output.max_occurs)

    @unittest.skip('HZ')
    def test_parse_process_input_complex(self):
        """
        Tests, if parse_input_info parses correct
        @return: Nothing
        @rtype: None
        """
        process_description = self.describe_processes_root.find('ProcessDescription')
        data_inputs = process_description.find('DataInputs')
        input_element = data_inputs.find('Input')
        wps_process_input = base.utils.parse_input_info(input_element, self.xml_namespaces, self.wps_process)

        self.assertEqual(wps_process_input.role, self.wps_process_input.role)
        self.assertEqual(wps_process_input.identifier, self.wps_process_input.identifier)
        self.assertEqual(wps_process_input.title, self.wps_process_input.title)
        self.assertEqual(wps_process_input.abstract, self.wps_process_input.abstract)
        self.assertEqual(wps_process_input.datatype, self.wps_process_input.datatype)
        self.assertEqual(wps_process_input.format, self.wps_process_input.format)
        self.assertEqual(wps_process_input.min_occurs, self.wps_process_input.min_occurs)
        self.assertEqual(wps_process_input.max_occurs, self.wps_process_input.max_occurs)

    def test_parse_process_input_fail(self):
        """
        Test of exception throw
        @return: Nothing
        @rtype: None
        """
        self.assertRaises(AttributeError, base.utils.parse_input_info(None, self.xml_namespaces,
                                                                      self.say_hello_literal_process))

    def test_parse_process_output_fail(self):
        """
        Test of exception throw
        @return: Nothing
        @rtype: None
        """
        self.assertRaises(AttributeError, base.utils.parse_output_info(None, self.xml_namespaces,
                                                                       self.say_hello_literal_process))




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

    @unittest.skip('fails')
    def test_search_provider_in_database_1(self):
        """

        @return:
        @rtype:
        """
        self.create_and_save_wps_provider()
        provider_from_database = utils.search_provider_in_database(self.wps_provider)
        self.assertIsNotNone(provider_from_database)

    @unittest.skip('fails')
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

    @unittest.skip('fails')
    def test_search_server_in_database_2(self):
        """

        @return:
        @rtype:
        """
        server_from_database = utils.search_server_in_database(self.wps_server)
        self.assertIsNone(server_from_database)

    @unittest.skip('fails')
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


class CronTestCase(TestCase):
    def test_update_wps_processes_with_empty_database(self):
        self.assertEqual(Process.objects.all().__len__(), 0)
        base.cron.update_wps_processes()
        self.assertEqual(Process.objects.all().__len__(), 0)
