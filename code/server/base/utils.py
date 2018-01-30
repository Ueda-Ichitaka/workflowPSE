import urllib.request
import xml.etree.ElementTree as ET

from lxml.builder import ElementMaker
from pywps import NAMESPACES as ns

import base.cron
from base.models import WPSProvider, WPS, Process, InputOutput, DATATYPE, ROLE

E = ElementMaker()
wps_em = ElementMaker(namespace=ns['wps'], nsmap=ns)
ows_em = ElementMaker(namespace=ns['ows'], nsmap=ns)
xlink_em = ElementMaker(namespace=ns['ows'], nsmap=ns)

ns_map = {
    # wps namespaced tags
    "Capabilities": f"{{{ns['wps']}}}Capabilities",
    "ProcessDescriptions": f"{{{ns['wps']}}}ProcessDescriptions",
    "ExecuteResponse": f"{{{ns['wps']}}}ExecuteResponse",
    "Process": f"{{{ns['wps']}}}Process",
    "Status": f"{{{ns['wps']}}}Status",
    "Data": f"{{{ns['wps']}}}Data",
    "LiteralData": f"{{{ns['wps']}}}LiteralData",
    "ComplexData": f"{{{ns['wps']}}}ComplexData",
    "Output": f"{{{ns['wps']}}}Output",
    "ProcessOutputs": f"{{{ns['wps']}}}ProcessOutputs",
    "Input": f"{{{ns['wps']}}}Input",
    "DataInput": f"{{{ns['wps']}}}DataInput",
    "Default": f"{{{ns['wps']}}}Default",
    "Format": f"{{{ns['wps']}}}Format",
    "MimeType": f"{{{ns['wps']}}}MimeType",
    "Supported": f"{{{ns['wps']}}}Supported",
    "CRS": f"{{{ns['wps']}}}CRS",
    "Reference": f"{{{ns['wps']}}}Reference",

    # ows namespaced tags
    "Identifier": f"{{{ns['ows']}}}Identifier",
    "Title": f"{{{ns['ows']}}}Title",
    "Abstract": f"{{{ns['ows']}}}Abstract",
    "BoundingBox": f"{{{ns['ows']}}}BoundingBox",
    "DataType": f"{{{ns['ows']}}}DataType",
    "AllowedValues": f"{{{ns['ows']}}}AllowedValues",
    "Value": f"{{{ns['ows']}}}Value",
    "Range": f"{{{ns['ows']}}}Range",
    "MinimumValue": f"{{{ns['ows']}}}MinimumValue",
    "MaximumValue": f"{{{ns['ows']}}}MaximumValue",
    "LowerCorner": f"{{{ns['ows']}}}LowerCorner",
    "UpperCorner": f"{{{ns['ows']}}}UpperCorner",
    "Spacing": f"{{{ns['ows']}}}Spacing",
    "AnyValue": f"{{{ns['ows']}}}AnyValue",
    "Metadata": f"{{{ns['ows']}}}Metadata",

    # xlink namespaced tags
    "href": f"{{{ns['xlink']}}}href",
}

possible_stats = ["ProcessAccepted", "ProcessStarted", "ProcessPaused", "ProcessSucceeded", "ProcessFailed"]


# TODO: tests, documentation
def add_wps_server(server_urls):
    """
    This method add new wps server to the database.
    It receives a list of server urls as parameter from the admin page
    and creates new wps server and service provider objects, which will saved
    in the database.

    After that the method update_wps_processes will called.

    @param server_urls: List of urls given by admin on admin page
    @type server_urls: str list
    @return: None
    @rtype:
    """
    # server_urls = ['http://pse.rudolphrichard.de:5000/wps?request=GetCapabilities&service=WPS']
    for server_url in server_urls:
        if server_url[-1] != '/':
            server_url = server_url + '/'

        server_url = server_url + 'wps?request=GetCapabilities&service=WPS'
        temp_xml, headers = urllib.request.urlretrieve(server_url)

        # TODO: method, that parse xml namespaces
        xml_namespaces = {
            'gml': 'http://www.opengis.net/gml',
            'xlink': 'http://www.w3.org/1999/xlink',
            'wps': 'http://www.opengis.net/wps/1.0.0',
            'ows': 'http://www.opengis.net/ows/1.1',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        # Parse the xml file
        get_capabilities_tree = ET.parse(temp_xml)
        get_capabilities_root = get_capabilities_tree.getroot()

        # Parse and save information about server provider
        service_provider = parse_service_provider_info(get_capabilities_root, xml_namespaces)
        service_provider_from_database = search_provider_in_database(service_provider)
        if service_provider_from_database is None:
            service_provider.save()
        else:
            service_provider = service_provider_from_database
            # Parse and save information about wps server
        wps_server = parse_wps_server_info(get_capabilities_root, xml_namespaces, service_provider)
        wps_server_from_database = search_server_in_database(wps_server)
        if wps_server_from_database is None:
            wps_server.save()
        else:
            wps_server = overwrite_server(wps_server_from_database, wps_server)

    base.cron.update_wps_processes()


def search_provider_in_database(service_provider):
    """
    Check that the service_provider instance given in parameter
    is not already in database.
    The istances are equal, if their 'provider_name' and
    'provider_site' fields are equal
    If database has the same instance, it will be returned.
    If database not contains instance, None will be returned.

    @param service_provider: A instance of service_provider
    @type service_provider: WPSProvider
    @return: saved instance | None
    @rtype: WPSProvider | None
    """
    try:
        provider = WPSProvider.objects.get(provider_name=service_provider.provider_name, provider_site=service_provider.provider_site)
    except WPSProvider.DoesNotExist:
        provider = None

    return provider


def search_server_in_database(wps_server):
    """
    Check that the wps_service instance given in parameter
    is not already in database.
    The instances are equal, if their 'title' fields
    are equal.
    If database has the same instance, it will be returned.
    If database not contains instance, None will be returned.

    @param wps_server: An instance of wps_server
    @type wps_server: WPS
    @return: saved instance | None
    @rtype: WPS | None
    """
    try:
        server = WPS.objects.get(title=wps_server.title)
    except WPS.DoesNotExist:
        server = None

    return server


def search_process_in_database(parsed_process):
    """
    Check that the wps process instance given in parameter
    is not already in database.
    The instances are equal, if their 'identifier' fields
    are equal
    If database has the same instance, it will be returned.
    If database not contains instance, None will be returned.
    @param parsed_process: An instance od process
    @type parsed_process: Process
    @return: saved instance | None
    @rtype: Process | None
    """
    try:
        process_from_database = Process.objects.get(identifier=parsed_process.identifier)
    except Process.DoesNotExist:
        process_from_database = None

    return process_from_database


def search_input_output_in_database(parsed_input_output):
    """
    The instances are equal, if their 'identifier' fields
    are equal,they have the same role (Input or Output) and
    they belong to the same process.
    :param parsed_input_output:
    :return:
    """
    try:
        ioput = InputOutput.objects.get(identifier=parsed_input_output.identifier,
                                        process=parsed_input_output.process, role=parsed_input_output.role)
    except InputOutput.DoesNotExist:
        ioput = None

    return ioput


# TODO: tests, documentation
def overwrite_server(old_entry, new_entry):
    """

    @param old_entry:
    @type old_entry:
    @param new_entry:
    @type new_entry:
    @return:
    @rtype:
    """
    old_entry.abstract = new_entry.abstract
    old_entry.capabilities_url = new_entry.capabilities_url
    old_entry.describe_url = new_entry.describe_url
    old_entry.execute_url = new_entry.execute_url

    old_entry.save()
    return old_entry


def overwrite_process(old_entry, new_entry):
    """

    @param old_entry:
    @type old_entry:
    @param new_entry:
    @type new_entry:
    @return:
    @rtype:
    """
    old_entry.title = new_entry.title
    old_entry.abstract = new_entry.abstract

    old_entry.save()
    return old_entry


def overwrite_input_output(old_entry, new_entry):
    """

    :param old_entry:
    :param new_entry:
    :return:
    """
    old_entry.title = new_entry.title
    old_entry.abstract = new_entry.abstract
    old_entry.datatype = new_entry.datatype
    old_entry.format = new_entry.format
    old_entry.min_occurs = new_entry.min_occurs
    old_entry.max_occurs = new_entry.max_occurs

    old_entry.save()
    return old_entry


# TODO: tests, documentation
def parse_service_provider_info(root, namespaces):
    """

    @param root:
    @type root:
    @param namespaces:
    @type namespaces:
    @return:
    @rtype:
    """
    service_provider_element = root.find('ows:ServiceProvider', namespaces)
    provider_name = service_provider_element.find('ows:ProviderName', namespaces).text
    provider_site = service_provider_element.find('ows:ProviderSite', namespaces).attrib.get(
        '{' + namespaces.get('xlink') + '}href')

    service_contact_element = service_provider_element.find('ows:ServiceContact', namespaces)

    individual_name = service_contact_element.find('ows:IndividualName', namespaces).text
    position_name = service_contact_element.find('ows:PositionName', namespaces).text

    try:
        service_provider = WPSProvider.objects.get(provider_name=provider_name,
                                                   provider_site=provider_site,
                                                   individual_name=individual_name)
    except WPSProvider.DoesNotExist:
        service_provider = WPSProvider(provider_name=provider_name,
                                       provider_site=provider_site,
                                       individual_name=individual_name,
                                       position_name=position_name)
    return service_provider


# TODO: tests, documentation
def parse_wps_server_info(root, namespaces, provider):
    """

    @param root:
    @type root:
    @param namespaces:
    @type namespaces:
    @param provider:
    @type provider:
    @return:
    @rtype:
    """
    service_identification_element = root.find('ows:ServiceIdentification', namespaces)

    server_title = service_identification_element.find('ows:Title', namespaces).text
    server_abstract = service_identification_element.find('ows:Abstract', namespaces).text

    operations_metadata_element = root.find('ows:OperationsMetadata', namespaces)

    urls_elements = operations_metadata_element.findall('ows:Operation/ows:DCP/ows:HTTP/ows:Get', namespaces)
    urls = []
    for item in urls_elements:
        urls.append(item.attrib.get('{' + namespaces.get('xlink') + '}href'))

    try:
        wps_server = WPS.objects.get(service_provider=provider,
                                     title=server_title)
    except WPS.DoesNotExist:
        wps_server = WPS(service_provider=provider,
                         title=server_title,
                         abstract=server_abstract,
                         capabilities_url=urls[0],
                         describe_url=urls[1],
                         execute_url=urls[2])
    return wps_server


# TODO: tests, documentation
def parse_process_info(process_element, namespaces, wps_server):
    """

    @param process_element:
    @type process_element:
    @param namespaces:
    @type namespaces:
    @param wps_server:
    @type wps_server:
    @return:
    @rtype:
    """
    process_identifier = process_element.find('ows:Identifier', namespaces).text
    process_title = process_element.find('ows:Title', namespaces).text

    process_abstract_element = process_element.find('ows:Abstract', namespaces)
    process_abstract = process_abstract_element.text if process_abstract_element is not None \
        else 'No process description available'

    try:
        process = Process.objects.get(wps=wps_server,
                                      identifier=process_identifier,
                                      title=process_title)
    except Process.DoesNotExist:
        process = Process(wps=wps_server,
                          identifier=process_identifier,
                          title=process_title,
                          abstract=process_abstract)
    return process


# TODO: tests, documentation
def parse_input_info(input_element, namespaces, process):
    """

    @param input_element:
    @type input_element:
    @param namespaces:
    @type namespaces:
    @param process:
    @type process:
    @return:
    @rtype:
    """
    input_identifier = input_element.find('ows:Identifier', namespaces).text
    input_title = input_element.find('ows:Title', namespaces).text

    input_abstract_element = input_element.find('ows:Abstract', namespaces)
    input_abstract = input_abstract_element.text if input_abstract_element is not None \
        else 'No description for input available'

    input_datatype = None
    input_format = None

    if input_element.find('LiteralData') is not None:
        input_datatype = DATATYPE[0][0]
        literal_data_element = input_element.find('LiteralData')
        input_format = literal_data_element.find('ows:DataType', namespaces).text
    elif input_element.find('ComplexData') is not None:
        input_datatype = DATATYPE[1][0]
        input_format = None
    elif input_element.find('BoundingBoxData') is not None:
        input_datatype = DATATYPE[2][0]
        input_format = None

    input_min_occurs = input_element.attrib.get('minOccurs')
    input_max_occurs = input_element.attrib.get('maxOccurs')

    try:
        input = InputOutput.objects.get(process=process,
                                        role=ROLE[0][0],
                                        identifier=input_identifier,
                                        title=input_title)
    except InputOutput.DoesNotExist:
        input = InputOutput(process=process,
                            role=ROLE[0][0],
                            identifier=input_identifier,
                            title=input_title,
                            abstract=input_abstract,
                            datatype=input_datatype,
                            format=input_format,
                            min_occurs=input_min_occurs,
                            max_occurs=input_max_occurs)
    return input


# TODO: tests, documentation
def parse_output_info(output_element, namespaces, process):
    """

    
    @param output_element:
    @type output_element:
    @param namespaces:
    @type namespaces:
    @param process:
    @type process:
    @return:
    @rtype:
    """
    output_identifier = output_element.find('ows:Identifier', namespaces).text
    output_title = output_element.find('ows:Title', namespaces).text

    output_abstract_element = output_element.find('ows:Abstract', namespaces)
    output_abstract = output_abstract_element.text if output_abstract_element is not None \
        else 'No description for output avaible'

    output_datatype = None
    output_format = None

    if output_element.find('LiteralData') is not None:
        output_datatype = DATATYPE[0][0]
        literal_data_element = output_element.find('LiteralData')
        output_format = literal_data_element.find('ows:DataType', namespaces).text
    elif output_element.find('ComplexData') is not None:
        output_datatype = DATATYPE[1][0]
        output_format = None
    elif output_element.find('BoundingBoxData') is not None:
        output_datatype = DATATYPE[2][0]
        output_format = None

    output_min_occurs = 1
    output_max_occurs = 1

    try:
        output = InputOutput.objects.get(process=process,
                                         role=ROLE[1][0],
                                         identifier=output_identifier,
                                         title=output_title)
    except InputOutput.DoesNotExist:
        output = InputOutput(process=process,
                             role=ROLE[1][0],
                             identifier=output_identifier,
                             title=output_title,
                             abstract=output_abstract,
                             datatype=output_datatype,
                             format=output_format,
                             min_occurs=output_min_occurs,
                             max_occurs=output_max_occurs)
    return output
