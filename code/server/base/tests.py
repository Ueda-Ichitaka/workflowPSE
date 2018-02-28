import json
import os
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

import base.cron
import base.utils as utils
from base.models import WPSProvider, WPS, Process, Workflow, Task, InputOutput, Artefact


class CronTestCase(TestCase):
    """
    Test Class for scheduler and execution tests
    """
    dir_path = os.path.dirname(os.path.abspath(__file__))
    xmlDir = os.path.join(dir_path, 'testfiles/')

    def setUp(self):
        """
        Sets up test data in test db, gets called before every test function
        @return: None
        @rtype: NoneType
        """
        self.u = User.objects.create(username='testUser')
        self.u.save()
        self.w = Workflow.objects.create(name="TestWF", description="tl;dr", percent_done='0', created_at=datetime.now(), creator_id='1',
                                         last_modifier_id='1')
        self.w.save()
        self.wp = WPSProvider.objects.create(provider_name="Test Provider", provider_site="pse.rudolphrichard.de", individual_name="Rudolph, Richard",
                                             position_name="Software Engineer")
        self.wp.save()
        self.wps = WPS.objects.create(service_provider_id='1', title="PyWPS Testserver", abstract="tl;dr",
                                      capabilities_url="http://pse.rudolphrichard.de:5000/wps",
                                      describe_url="http://pse.rudolphrichard.de:5000/wps", execute_url="http://pse.rudolphrichard.de:5000/wps")
        self.p = Process.objects.create(wps_id='1', identifier="say_hello", title="Process Say Hello", abstract="tl;dr")
        self.p.save()
        self.t = Task.objects.create(workflow_id='1', process_id='1', x='1', y='1', status='1', title="Say Hello Task",
                                     status_url="http://pse.rudolphrichard.de")
        self.t.save()
        self.io1 = InputOutput.objects.create(process_id='1', role='0', identifier="name", title="Input name", abstract="tl;dr", datatype='0',
                                              format="string",
                                              min_occurs='1', max_occurs='1')
        self.io1.save()
        self.io2 = InputOutput.objects.create(process_id='1', role='1', identifier="response", title="Output name response", abstract="tl;dr",
                                              datatype='0',
                                              format="string",
                                              min_occurs='1', max_occurs='1')
        self.io2.save()
        self.a = Artefact.objects.create(task_id='1', parameter_id='1', role='0', format="string", data="Ueda")
        self.a.save()

    def tearDown(self):
        """
        Destroys the test datasets in database after test method was executed. Gets called after every test method
        @return: None
        @rtype: NoneType
        """
        self.u.delete()
        self.w.delete()
        self.wp.delete()
        self.wps.delete()
        self.p.delete()
        self.t.delete()
        self.io1.delete()
        self.io2.delete()
        self.a.delete()

    def test_send_task(self):
        """
        Schedules the test Task and asserts it gets a response from server and status url is written to DB
        @return: None
        @rtype: NoneType
        """
        base.cron.scheduler()
        task = Task.objects.get(title="Say Hello Task")
        self.assertIn("http://pse.rudolphrichard.de:5000/outputs/", task.status_url)

    def test_execution(self):
        """
        Executes Task and tests if the correct answer is written to DB.
        @return: None
        @rtype: NoneType
        """
        base.cron.scheduler()
        base.cron.receiver()
        base.cron.receiver()
        output = Artefact.objects.get(role='1', task='1', parameter='2')
        self.assertEqual(output.data, 'Hello Ueda')

    def test_update_wps_processes_with_empty_database(self):
        base.cron.update_wps_processes()
        self.assertEqual(Process.objects.all().__len__(), 0)

    def test_update_wps_processes(self):
        base.utils.add_wps_server('http://milbaier.com:5000')
        self.assertEqual(Process.objects.all().__len__(), 14)


# Create your tests here.
class ParserTestCase(TestCase):
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
                                          abstract=None,
                                          datatype='0',  # Literal
                                          format='string',
                                          min_occurs='1',
                                          max_occurs='1')

    say_hello_literal_output = InputOutput(process=say_hello_literal_process,
                                           role='1',  # Output
                                           identifier='response',
                                           title='Output response',
                                           abstract=None,
                                           datatype='0',  # Literal
                                           format='string',
                                           min_occurs='1',
                                           max_occurs='1')

    say_hello_process_element = describe_processes_root.find("./ProcessDescription/[ows:Identifier='say_hello']",
                                                             xml_namespaces)

    centroids_process = Process(wps=wps_server,
                                identifier='centroids',
                                title='Process Centroids',
                                abstract='Returns a GeoJSON with centroids of features from an uploaded GML.')
    centroids_complex_input = InputOutput(process=centroids_process,
                                          role='0',
                                          identifier='layer',
                                          title='Layer',
                                          abstract=None,
                                          datatype='1',
                                          format='application/gml+xml', #application/gml+xml
                                          min_occurs='1',
                                          max_occurs='1')
    centroids_complex_output = InputOutput(process=centroids_process,
                                           role='1',
                                           identifier='out',
                                           title='Referenced Output',
                                           abstract=None,
                                           datatype='1',
                                           format='application/json', #application/json
                                           min_occurs='1',
                                           max_occurs='1')
    centroid_process_element = describe_processes_root.find("./ProcessDescription/[ows:Identifier='centroids']",
                                                            xml_namespaces)

    bbox_process = Process(wps=wps_server,
                           identifier='boundingbox',
                           title='Bounding box in- and out',
                           abstract='Given a bounding box, it returns the same bounding box')
    bbox_bounding_box_input = InputOutput(process=bbox_process,
                                          role='0',
                                          identifier='bboxin',
                                          title='box in',
                                          abstract=None,
                                          datatype='2',
                                          format=None,
                                          min_occurs='1',
                                          max_occurs='1')
    bbox_bounding_box_output = InputOutput(process=bbox_process,
                                           role='1',
                                           identifier='bboxout',
                                           title='box out',
                                           abstract=None,
                                           datatype='2',
                                           format=None,
                                           min_occurs='1',
                                           max_occurs='1')
    bbox_process_element = describe_processes_root.find("./ProcessDescription/[ows:Identifier='boundingbox']",
                                                        xml_namespaces)

    def test_parse_service_provider_info(self):
        """
        Tests, if parse_service_provider_info parses correct
        @return: None
        @rtype: NoneType
        """

        wps_provider = base.utils.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        self.assertEqual(wps_provider.provider_name, self.wps_provider.provider_name)
        self.assertEqual(wps_provider.provider_site, self.wps_provider.provider_site)
        self.assertEqual(wps_provider.individual_name, self.wps_provider.individual_name)
        self.assertEqual(wps_provider.position_name, self.wps_provider.position_name)

    def test_parse_service_provider_info_fail(self):
        """
        Test of exception throw
        @return: None
        @rtype: NoneType
        """
        self.assertRaises(AttributeError, base.utils.parse_service_provider_info(None, self.xml_namespaces))

    def test_parse_wps_server_info(self):
        """
        Tests, if parse_wps_server_info parses correct
        @return: None
        @rtype: NoneType
        """
        wps_provider = base.utils.parse_service_provider_info(self.capabilities_root, self.xml_namespaces)
        wps_server = base.utils.parse_wps_server_info(self.capabilities_root, self.xml_namespaces, wps_provider)
        self.assertEqual(wps_server.title, self.wps_server.title)
        self.assertEqual(wps_server.abstract, self.wps_server.abstract, )
        self.assertEqual(wps_server.capabilities_url, self.wps_server.capabilities_url, )
        self.assertEqual(wps_server.describe_url, self.wps_server.describe_url)
        self.assertEqual(wps_server.execute_url, self.wps_server.execute_url)

    def test_parse_wps_server_info_fail(self):
        """
        Test of exception throw
        @return: None
        @rtype: NoneType
        """
        self.assertRaises(AttributeError, base.utils.parse_wps_server_info(None, self.xml_namespaces,
                                                                           self.wps_provider))

    def test_parse_wps_process(self):
        """
        Tests, if parse_process_info parses correct
        @return: None
        @rtype: NoneType
        """
        wps_process = base.utils.parse_process_info(self.say_hello_process_element, self.xml_namespaces,
                                                    self.wps_server)

        self.assertEqual(wps_process.identifier, self.say_hello_literal_process.identifier)
        self.assertEqual(wps_process.title, self.say_hello_literal_process.title)
        self.assertEqual(wps_process.abstract, self.say_hello_literal_process.abstract)

    def test_parse_wps_process_fail(self):
        """
        Test of exception throw
        @return: None
        @rtype: NoneType
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
        wps_process_output = base.utils.parse_output_info(say_hello_process_output_element, self.xml_namespaces,
                                                          self.say_hello_literal_process)

        self.assertEqual(wps_process_output.role, self.say_hello_literal_output.role)
        self.assertEqual(wps_process_output.identifier, self.say_hello_literal_output.identifier)
        self.assertEqual(wps_process_output.title, self.say_hello_literal_output.title)
        self.assertEqual(wps_process_output.abstract, self.say_hello_literal_output.abstract)
        self.assertEqual(wps_process_output.datatype, self.say_hello_literal_output.datatype)
        self.assertEqual(wps_process_output.format, self.say_hello_literal_output.format)
        self.assertEqual(wps_process_output.min_occurs, self.say_hello_literal_output.min_occurs)
        self.assertEqual(wps_process_output.max_occurs, self.say_hello_literal_output.max_occurs)

    def test_parse_process_input_complex(self):
        """
        Tests, if parse_input_info parses correct
        @return: None
        @rtype: NoneType
        """
        centroids_input_element = self.centroid_process_element.find('./DataInputs/Input')
        wps_process_input = base.utils.parse_input_info(centroids_input_element, self.xml_namespaces,
                                                        self.centroids_process)

        self.assertEqual(wps_process_input.role, self.centroids_complex_input.role)
        self.assertEqual(wps_process_input.identifier, self.centroids_complex_input.identifier)
        self.assertEqual(wps_process_input.title, self.centroids_complex_input.title)
        self.assertEqual(wps_process_input.abstract, self.centroids_complex_input.abstract)
        self.assertEqual(wps_process_input.datatype, self.centroids_complex_input.datatype)
        self.assertEqual(wps_process_input.format, self.centroids_complex_input.format)
        self.assertEqual(wps_process_input.min_occurs, self.centroids_complex_input.min_occurs)
        self.assertEqual(wps_process_input.max_occurs, self.centroids_complex_input.max_occurs)

    def test_parse_process_output_complex(self):
        """
        Tests, if parse_output_info parses correct
        @return: None
        @rtype: NoneType
        """
        centroids_output_element = self.centroid_process_element.find('./ProcessOutputs/Output')
        wps_process_output = base.utils.parse_output_info(centroids_output_element, self.xml_namespaces,
                                                          self.centroids_process)

        self.assertEqual(wps_process_output.role, self.centroids_complex_output.role)
        self.assertEqual(wps_process_output.identifier, self.centroids_complex_output.identifier)
        self.assertEqual(wps_process_output.title, self.centroids_complex_output.title)
        self.assertEqual(wps_process_output.abstract, self.centroids_complex_output.abstract)
        self.assertEqual(wps_process_output.datatype, self.centroids_complex_output.datatype)
        self.assertEqual(wps_process_output.format, self.centroids_complex_output.format)
        self.assertEqual(wps_process_output.min_occurs, self.centroids_complex_output.min_occurs)
        self.assertEqual(wps_process_output.max_occurs, self.centroids_complex_output.max_occurs)

    def test_parse_process_input_bounding_box(self):
        """
        Tests, if parse_input_info parses correct
        @return: None
        @rtype: NoneType
        """
        bbox_input_element = self.bbox_process_element.find('./DataInputs/Input')
        wps_process_input = base.utils.parse_input_info(bbox_input_element, self.xml_namespaces,
                                                        self.bbox_process)

        self.assertEqual(wps_process_input.role, self.bbox_bounding_box_input.role)
        self.assertEqual(wps_process_input.identifier, self.bbox_bounding_box_input.identifier)
        self.assertEqual(wps_process_input.title, self.bbox_bounding_box_input.title)
        self.assertEqual(wps_process_input.abstract, self.bbox_bounding_box_input.abstract)
        self.assertEqual(wps_process_input.datatype, self.bbox_bounding_box_input.datatype)
        self.assertEqual(wps_process_input.format, self.bbox_bounding_box_input.format)
        self.assertEqual(wps_process_input.min_occurs, self.bbox_bounding_box_input.min_occurs)
        self.assertEqual(wps_process_input.max_occurs, self.bbox_bounding_box_input.max_occurs)

    def test_parse_process_output_bounding_box(self):
        """
        Tests, if parse_output_info parses correct
        @return: None
        @rtype: NoneType
        """
        bbox_output_element = self.bbox_process_element.find('./ProcessOutputs/Output')
        wps_process_output = base.utils.parse_output_info(bbox_output_element, self.xml_namespaces,
                                                          self.bbox_process)

        self.assertEqual(wps_process_output.role, self.bbox_bounding_box_output.role)
        self.assertEqual(wps_process_output.identifier, self.bbox_bounding_box_output.identifier)
        self.assertEqual(wps_process_output.title, self.bbox_bounding_box_output.title)
        self.assertEqual(wps_process_output.abstract, self.bbox_bounding_box_output.abstract)
        self.assertEqual(wps_process_output.datatype, self.bbox_bounding_box_output.datatype)
        self.assertEqual(wps_process_output.format, self.bbox_bounding_box_output.format)
        self.assertEqual(wps_process_output.min_occurs, self.bbox_bounding_box_output.min_occurs)
        self.assertEqual(wps_process_output.max_occurs, self.bbox_bounding_box_output.max_occurs)

    def test_parse_process_input_fail(self):
        """
        Test of exception throw
        @return: None
        @rtype: NoneType
        """
        self.assertRaises(AttributeError, base.utils.parse_input_info(None, self.xml_namespaces,
                                                                      self.say_hello_literal_process))

    def test_parse_process_output_fail(self):
        """
        Test of exception throw
        @return: None
        @rtype: NoneType
        """
        self.assertRaises(AttributeError, base.utils.parse_output_info(None, self.xml_namespaces,
                                                                       self.say_hello_literal_process))


class DatabaseTestCase(TestCase):
    """

    """
    wps_provider = None
    wps_server = None
    wps_process = None
    wps_process_input = None
    wps_process_output = None

    def setUp(self):
        self.wps_provider = WPSProvider.objects.create(provider_name='Organization Name',
                                                       provider_site='http://pywps.org/',
                                                       individual_name='Lastname, Firstname',
                                                       position_name='Position Title')
        self.wps_server = WPS.objects.create(service_provider=self.wps_provider,
                                             title='PyWPS Processing Service',
                                             abstract='PyWPS is an implementation of the Web Processing '
                                                      'Service standard from the Open Geospatial Consortium. '
                                                      'PyWPS is written in Python.',
                                             capabilities_url='http://localhost/wps?request=GetCapabilities&service=WPS',
                                             describe_url='http://localhost/wps?request=DescribeProcess'
                                                          '&service=WPS&identifier=all&version=1.0.0',
                                             execute_url='http://localhost/wps?request=Execute&service=WPS')
        self.wps_process = Process.objects.create(wps=self.wps_server,
                                                  identifier='say_hello',
                                                  title='Process Say Hello',
                                                  abstract='Returns a literal string output with Hello plus '
                                                           'the inputed name')
        self.wps_process_input = InputOutput.objects.create(process=self.wps_process,
                                                            role='0',  # Input
                                                            identifier='name',
                                                            title='Input name',
                                                            abstract='No description for input available',
                                                            datatype='0',  # Literal
                                                            format='string',
                                                            min_occurs=1,
                                                            max_occurs=1)
        self.wps_process_output = InputOutput.objects.create(process=self.wps_process,
                                                             role='1',  # Output
                                                             identifier='response',
                                                             title='Output response',
                                                             abstract='No description for output available',
                                                             datatype='0',  # Literal
                                                             format='string',
                                                             min_occurs=1,
                                                             max_occurs=1)

    def test_search_provider_in_database(self):
        """
        Tests, if search_provider_in_database search correct
        @return: None
        @rtype: NoneType
        """
        provider_from_database = utils.search_provider_in_database(self.wps_provider)
        self.assertIsNotNone(provider_from_database)

    def test_search_provider_in_empty_database(self):
        """

        @return: None
        @rtype: NoneType
        """
        WPSProvider.objects.all().delete()
        provider_from_database = utils.search_provider_in_database(self.wps_provider)
        self.assertIsNone(provider_from_database)

    def test_search_server_in_database(self):
        """

        @return: None
        @rtype: NoneType
        """
        server_from_database = utils.search_server_in_database(self.wps_server)
        self.assertIsNotNone(server_from_database)

    def test_search_server_in_empty_database_(self):
        """

        @return: None
        @rtype: NoneType
        """
        WPS.objects.all().delete()
        server_from_database = utils.search_server_in_database(self.wps_server)
        self.assertIsNone(server_from_database)

    def test_search_process_in_database(self):
        process_from_database = utils.search_process_in_database(self.wps_process)
        self.assertIsNotNone(process_from_database)

    def test_search_process_in_empty_database(self):
        Process.objects.all().delete()
        process_from_database = utils.search_process_in_database(self.wps_process)
        self.assertIsNone(process_from_database)

    def test_search_input_output_in_database(self):
        input_from_database = utils.search_input_output_in_database(self.wps_process_input)
        self.assertIsNotNone(input_from_database)

    def test_search_input_output_in_empty_database(self):
        InputOutput.objects.all().delete()
        input_from_database = utils.search_input_output_in_database(self.wps_process_input)
        self.assertIsNone(input_from_database)

    def test_overwrite_server(self):
        """
        Tests, if information about a WPS server will be overwritten.
        @return: None
        @rtype: NoneType
        """
        old_database_entry = WPS.objects.get(title='PyWPS Processing Service')
        new_wps_server = WPS(service_provider=self.wps_provider,
                             title='PyWPS Processing Service',
                             abstract='new_PyWPS is an implementation of the Web Processing '
                                      'Service standard from the Open Geospatial Consortium. '
                                      'PyWPS is written in Python.',
                             capabilities_url='new_http://localhost/wps?request=GetCapabilities&service=WPS',
                             describe_url='new_http://localhost/wps?request=DescribeProcess'
                                          '&service=WPS&identifier=all&version=1.0.0',
                             execute_url='new_http://localhost/wps?request=Execute&service=WPS')

        base.utils.overwrite_server(old_database_entry, new_wps_server)
        new_database_entry = WPS.objects.get(title='PyWPS Processing Service')

        self.assertEqual(old_database_entry.pk, new_database_entry.pk)

        self.assertEqual(new_database_entry.abstract, new_wps_server.abstract)
        self.assertEqual(new_database_entry.capabilities_url, new_wps_server.capabilities_url)
        self.assertEqual(new_database_entry.describe_url, new_wps_server.describe_url)
        self.assertEqual(new_database_entry.execute_url, new_wps_server.execute_url)

    def test_overwrite_process(self):
        old_database_entry = Process.objects.get(identifier='say_hello')
        new_wps_process = Process(wps=self.wps_server,
                                  identifier='say_hello',
                                  title='new_Process Say Hello',
                                  abstract='new_Returns a literal string output with Hello plus '
                                  'the inputed name')

        base.utils.overwrite_process(old_database_entry, new_wps_process)
        new_database_entry = Process.objects.get(identifier='say_hello')

        self.assertEqual(old_database_entry.pk, new_database_entry.pk)

        self.assertEqual(new_database_entry.title, new_wps_process.title)
        self.assertEqual(new_database_entry.abstract, new_wps_process.abstract)

    def test_overwrite_input_output(self):
        old_database_entry = InputOutput.objects.get(identifier='name')
        new_literal_input = InputOutput(process=self.wps_process,
                                          role='0',  # Input
                                          identifier='name',
                                          title='new_Input name',
                                          abstract='I have description now',
                                          datatype='1',  # Complex
                                          format='application/gml',
                                          min_occurs=1,
                                          max_occurs=1)

        base.utils.overwrite_input_output(old_database_entry, new_literal_input)
        new_database_entry = InputOutput.objects.get(identifier='name')

        self.assertEqual(old_database_entry.pk, new_database_entry.pk)

        self.assertEqual(new_database_entry.title, new_literal_input.title)
        self.assertEqual(new_database_entry.abstract, new_literal_input.abstract)
        self.assertEqual(new_database_entry.datatype, new_literal_input.datatype)
        self.assertEqual(new_database_entry.format, new_literal_input.format)
        self.assertEqual(new_database_entry.min_occurs, new_literal_input.min_occurs)
        self.assertEqual(new_database_entry.max_occurs, new_literal_input.max_occurs)


class ProcessViewCase(TestCase):
    def setUp(self):
        WPSProvider.objects.create(
            provider_name="Test Provider",
            provider_site="pse.rudolphrichard.de",
            individual_name="Rudolph, Richard",
            position_name="Software Engineer"
        )
        WPS.objects.create(
            service_provider_id='1',
            title="PyWPS Testserver",
            abstract="tl;dr",
            capabilities_url="http://pse.rudolphrichard.de:5000/wps",
            describe_url="http://pse.rudolphrichard.de:5000/wps",
            execute_url="http://pse.rudolphrichard.de:5000/wps")
        Process.objects.create(
            wps_id='1',
            identifier="say_hello",
            title="Process Say Hello",
            abstract="tl;dr"
        )
        InputOutput.objects.create(
            process_id='1',
            role='0',
            identifier="name",
            title="Input name",
            abstract="tl;dr",
            datatype='0',
            format="string",
            min_occurs='1',
            max_occurs='1')
        InputOutput.objects.create(
            process_id='1',
            role='1',
            identifier="response",
            title="Output name response",
            abstract="tl;dr",
            datatype='0',
            format="string",
            min_occurs='1',
            max_occurs='1')

    def assert_process_equal_to_expected(self, process):
        self.assertEqual(process['id'], 1)
        self.assertEqual(process['identifier'], 'say_hello')
        self.assertEqual(process['title'], 'Process Say Hello')
        self.assertEqual(process['abstract'], 'tl;dr')

        self.assertEqual(process['inputs'][0]['id'], 1)
        self.assertEqual(process['inputs'][0]['process_id'], 1)
        self.assertEqual(process['inputs'][0]['identifier'], 'name')
        self.assertEqual(process['inputs'][0]['title'], 'Input name')
        self.assertEqual(process['inputs'][0]['abstract'], 'tl;dr')
        self.assertEqual(process['inputs'][0]['role'], 'input')
        self.assertEqual(process['inputs'][0]['type'], 0)
        self.assertEqual(process['inputs'][0]['format'], 'string')
        self.assertEqual(process['inputs'][0]['max_occurs'], 1)
        self.assertEqual(process['inputs'][0]['min_occurs'], 1)

        self.assertEqual(process['inputs'][0]['id'], 1)
        self.assertEqual(process['inputs'][0]['process_id'], 1)
        self.assertEqual(process['inputs'][0]['identifier'], 'name')
        self.assertEqual(process['inputs'][0]['title'], 'Input name')
        self.assertEqual(process['inputs'][0]['abstract'], 'tl;dr')
        self.assertEqual(process['inputs'][0]['role'], 'input')
        self.assertEqual(process['inputs'][0]['type'], 0)
        self.assertEqual(process['inputs'][0]['format'], 'string')
        self.assertEqual(process['inputs'][0]['max_occurs'], 1)
        self.assertEqual(process['inputs'][0]['min_occurs'], 1)

        self.assertEqual(process['outputs'][0]['id'], 2)
        self.assertEqual(process['outputs'][0]['process_id'], 1)
        self.assertEqual(process['outputs'][0]['identifier'], 'response')
        self.assertEqual(process['outputs'][0]['title'], 'Output name response')
        self.assertEqual(process['outputs'][0]['abstract'], 'tl;dr')
        self.assertEqual(process['outputs'][0]['role'], 'output')
        self.assertEqual(process['outputs'][0]['type'], 0)
        self.assertEqual(process['outputs'][0]['format'], 'string')
        self.assertEqual(process['outputs'][0]['max_occurs'], 1)
        self.assertEqual(process['outputs'][0]['min_occurs'], 1)

    def test_process_get_single(self):
        response = json.loads(self.client.get('/process/1').content)

        self.assert_process_equal_to_expected(response)

    def test_process_get_all(self):
        response = json.loads(self.client.get('/process/').content)

        self.assert_process_equal_to_expected(response[0])

    def test_process_post(self):
        response = json.loads(self.client.post('/process/').content)

        self.assertTrue('error' in response)

    def test_process_path(self):
        response = json.loads(self.client.patch('/process/').content)

        self.assertTrue('error' in response)

    def test_process_delete(self):
        response = json.loads(self.client.delete('/process/').content)

        self.assertTrue('error' in response)
