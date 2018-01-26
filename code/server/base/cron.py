import os, sys
import random
import xml.etree.ElementTree as ET
from base.models import WPSProvider, WPS, Task, InputOutput, Artefact, Process, ROLE, DATATYPE, STATUS
from django.http import response
import requests
import urllib.request
from datetime import datetime
from pywps import OGCTYPE, NAMESPACES as ns
from lxml import etree

# TODO: naming convention, code formatting

ns_map = {
    # wps namespaced tags
    "Capabilities"	        :	"{{{}}}Capabilities".format(ns["wps"]),
    "ProcessDescriptions"   :	"{{{}}}ProcessDescriptions".format(ns["wps"]),
    "ExecuteResponse"	    :	"{{{}}}ExecuteResponse".format(ns["wps"]),
    "Process"			    :	"{{{}}}Process".format(ns["wps"]),
    "Status"			    :	"{{{}}}Status".format(ns["wps"]),
    "Data"				    :	"{{{}}}Data".format(ns["wps"]),
    "LiteralData"		    :	"{{{}}}LiteralData".format(ns["wps"]),
    "ComplexData"		    :	"{{{}}}ComplexData".format(ns["wps"]),
    "Output"			    :	"{{{}}}Output".format(ns["wps"]),
    "ProcessOutputs"	    :	"{{{}}}ProcessOutputs".format(ns["wps"]),
    "Input"				    :	"{{{}}}Input".format(ns["wps"]),
    "DataInput"			    :	"{{{}}}DataInput".format(ns["wps"]),
    "Default"			    :	"{{{}}}Default".format(ns["wps"]),
    "Format"			    :	"{{{}}}Format".format(ns["wps"]),
    "MimeType"			    :	"{{{}}}MimeType".format(ns["wps"]),
    "Supported"			    :	"{{{}}}Supported".format(ns["wps"]),
    "CRS"				    :	"{{{}}}CRS".format(ns["wps"]),
    "Reference"			    :	"{{{}}}Reference".format(ns["wps"]),

    # ows namespaced tags
    "Identifier"		    :	"{{{}}}Identifier".format(ns["ows"]),
    "Title"				    :	"{{{}}}Title".format(ns["ows"]),
    "Abstract"			    :	"{{{}}}Abstract".format(ns["ows"]),
    "BoundingBox"		    :	"{{{}}}BoundingBox".format(ns["wps"]),
    "DataType"			    :	"{{{}}}DataType".format(ns["ows"]),
    "AllowedValues"		    :	"{{{}}}AllowedValues".format(ns["ows"]),
    "Value"				    :	"{{{}}}Value".format(ns["ows"]),
    "Range"				    :	"{{{}}}Range".format(ns["ows"]),
    "MinimumValue"		    :	"{{{}}}MinimumValue".format(ns["ows"]),
    "MaximumValue"		    :	"{{{}}}MaximumValue".format(ns["ows"]),
    "LowerCorner"		    :	"{{{}}}LowerCorner".format(ns["ows"]),
    "UpperCorner"		    :	"{{{}}}UpperCorner".format(ns["ows"]),
    "Spacing"			    :	"{{{}}}Spacing".format(ns["ows"]),
    "AnyValue"			    :	"{{{}}}AnyValue".format(ns["ows"]),
    "Metadata"			    :	"{{{}}}Metadata".format(ns["ows"]),

    # xlink namespaced tags
    "href"                  :   "{{{}}}href".format(ns["xlink"])
}

possible_stats = ["ProcessAccepted", "ProcessStarted", "ProcessPaused", "ProcessSucceeded", "ProcessFailed"]

# TODO: tests
def scheduler():
    """
    Scheduler main function
    :return:
    :rtype:
    """


    # TODO: set to changeable by settings & config file
    outFile = '/home/ueda/workspace/PSE/code/server/outfile.txt'
    xmlDir = '/home/ueda/workspace/PSE/code/server/base/testfiles/'

    # redirect stout to file, output logging
    orig_stdout  = sys.stdout
    f = open(outFile, 'w')
    sys.stdout = f

    #generate execute xmls for all tasks with status ready
    xmlGenerator(xmlDir)

    #send task
    sendTask(2, xmlDir)

    sys.stdout = orig_stdout
    f.close()


# TODO: tests, documentation
def xmlGenerator(xmlDir):
    """
    generates xml for every task set to ready
    :param xmlDir:
    :type xmlDir:
    :return:
    :rtype:
    """


    task_list = list(Task.objects.filter(status='1').values())
    for task in task_list:

        #print("")

        root = ET.Element('wps:Execute')
        root.set('service', 'WPS')
        root.set('version', '1.0.0')
        root.set('xmlns:wps', 'http://www.opengis.net/wps/1.0.0')
        root.set('xmlns:ows', 'http://www.opengis.net/ows/1.1')
        root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation', 'http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd')


        process_list = list(Process.objects.filter(id=task["process_id"]).values())
        for process in process_list:

            identifier = ET.SubElement(root, 'ows:Identifier')
            identifier.text = process["identifier"]

        inputs = ET.SubElement(root, 'wps:DataInputs')

        input_list = list(InputOutput.objects.filter(process_id=task["process_id"], role='0').values())
        for input in input_list:

            inputElement = ET.SubElement(inputs, 'wps:Input')
            inputIdent = ET.SubElement(inputElement, 'ows:Identifier')
            inputTitle = ET.SubElement(inputElement, 'ows:Title')
            inputData = ET.SubElement(inputElement, 'wps:Data')
            inputIdent.text = input["identifier"]
            inputTitle.text = input["title"]


            artefact_list = list(Artefact.objects.filter(task_id=task["id"], parameter=input["id"]).values())
            for artefact in artefact_list:

                type = input["datatype"]
                if type == '0':
                    type = "LiteralData"
                elif type == '1':
                    type = "ComplexData"
                elif type == '2':
                    type = "BoundingBoxData"

                data = ET.SubElement(inputData, 'wps:' + type)
                data.text = artefact["data"]
                data.set('datatype', artefact["format"])

                #print("datatype: ", input["datatype"], " ", dict(DATATYPE).get(input["datatype"]))

        responseForm = ET.SubElement(root, 'wps:ResponseForm')
        responseDoc = ET.SubElement(responseForm, 'wps:ResponseDocument')
        responseDoc.set('storeExecuteResponse', 'true')
        responseDoc.set('lineage', 'true')
        responseDoc.set('status', 'true')

        output_list = list(InputOutput.objects.filter(process_id=task["process_id"], role='1').values())
        for out in output_list:

            outputElement = ET.SubElement(responseDoc, 'wps:Output')
            outputElement.set('asReference', 'true')
            outIdent = ET.SubElement(outputElement, 'ows:Identifier')
            outTitle = ET.SubElement(outputElement, 'ows:Title')
            outIdent.text = out["identifier"]
            outTitle.text = out["title"]


        #print(xmlDir + 'task' + str(task["id"]) + '.xml')

        tree = ET.ElementTree(root)
        tree.write(xmlDir + 'task' + str(task["id"]) + '.xml')
        #print(ET.tostring(root, 'unicode', 'xml'))


# TODO: tests, documentation
def sendTask(task_id, xmlDir):
    """

    :param task_id:
    :type task_id:
    :param xmlDir:
    :type xmlDir:
    :return:
    :rtype:
    """
    #should be changed to something without list
    task_list = list(Task.objects.filter(id=task_id).values())
    for task in task_list:

        execute_url = getExecuteUrl(task)

        #send to url
        filepath = str(xmlDir) + 'task' + str(task_id) + '.xml'
        file = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>' + str(open(filepath, 'r').read()) #'<?xml version="1.0" encoding="utf-8" standalone="yes"?>' +
        response = requests.post('http://pse.rudolphrichard.de:5000/wps', data=file) # TODO: replace with variable

        #print("")
        print("post response: ")
        print(response.text)
        print("")

        #get response from send
        xml = ET.fromstring(response.text)

        # TODO: check response for errors
        # response should be 

        print(xml.get('statusLocation'))

        #write status url from response to task
        #set status to running
        # update start time
        p = Task.objects.get(id=task_id)
        p.status_url = xml.get('statusLocation')
        p.status = '3'
        p.started_at = datetime.now()
        p.save()
        # TODO: delete execute xml file


# TODO: tests, documentation
def getExecuteUrl(task):
    """

    :param task:
    :type task:
    :return:
    :rtype:
    """
    execute_url = ""

    #traverse db tables task -> process -> wps -> url
    process_list = list(Process.objects.filter(id=task["process_id"]).values())
    for process in process_list:
        wps_list = list(WPS.objects.filter(id=process["wps_id"]).values())
        for wps in wps_list:
            execute_url = wps["execute_url"]

    return execute_url


# TODO: tests, documentation, implement
def scheduler_execute():
    #sends task to execution
    #receives response url
    pass


# TODO: tests, documentation, implement
def scheduler_check_execute():
    """

    :return:
    :rtype:
    """
    #execute policy
    pass


# TODO: tests, documentation, implement
def receiver():
    """

    :return:
    :rtype:
    """
    # Receiver main function
    # check output urls from servers
    # for workflow in executing list do
    #   for task in workflow do
    #      check response url
    #        check for changes to db 
    #        update db data
    pass


# TODO: tests, documentation, implement
def utils():
    """

    :return:
    :rtype:
    """
    # Main fuction for combined utility functions
    pass



# TODO: remove, left here for compatibility because all other collaborators don't push their progress
def xmlParser():
    """

    :return:
    :rtype:
    """
    #parses input xml
    #checks data for changes
    #writes changes to db
    pass


# TODO: tests, documentation, implement
def listExistingFiles():
    """

    :return:
    :rtype:
    """
    #part of datenhaltung
    #generates a list of all uploaded files, their upload date, last edit, editor, etc
    pass


# TODO: tests, documentation, implement
def deleteOldFiles():
    """

    :return:
    :rtype:
    """
    #part of datenhaltung
    #deletes files with last edit date > limit or other defined rule
    pass


# TODO: tests, documentation
def add_wps_server(server_urls):
    """
    :param server_urls: List of urls given by admin on admin page
    :return:
    :rtype:
    """

    #Parse the xml file
    get_capabilities_tree = ET.parse(get_cap_url_from_scc_vm)
    get_capabilities_root = get_capabilities_tree.getroot()

    service_provider = parse_service_provider_info(get_capabilities_root, xml_namespaces)
    service_provider_from_database = search_provider_in_database(service_provider)
    if service_provider_from_database is None:
        service_provider.save()
    else:
        service_provider = service_provider_from_database


    # TODO: use? else remove
    os.mkdir('/home/denis/Documents/prov' + str(random.randrange(1, 100)) + '/')

    wps_server = parse_wps_server_info(get_capabilities_root, xml_namespaces, service_provider)
    wps_server_from_database = search_server_in_database(wps_server)
    if wps_server_from_database is None:
        wps_server.save()
    else:
        wps_server = overwrite_server(wps_server_from_database, wps_server)
    # TODO: use? else remove
    os.mkdir('/home/denis/Documents/serv' + str(random.randrange(1, 100)) + '/')

    describe_processes_parsing(wps_server)
    # TODO: use? else remove
    os.mkdir('/home/denis/Documents/proc' + str(random.randrange(1, 100)) + '/')
    #server_urls = ['http://pse.rudolphrichard.de:5000/wps?request=GetCapabilities&service=WPS']
    for server_url in server_urls:
        if server_url[-1] != '/':
            server_url = server_url + '/'

        server_url = server_url + 'wps?request=GetCapabilities&service=WPS'
        temp_xml, headers = urllib.request.urlretrieve(server_url)

        #TODO: method, that parse xml namespaces
        xml_namespaces = {
            'gml': 'http://www.opengis.net/gml',
            'xlink': 'http://www.w3.org/1999/xlink',
            'wps': 'http://www.opengis.net/wps/1.0.0',
            'ows': 'http://www.opengis.net/ows/1.1',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        #Parse the xml file
        get_capabilities_tree = ET.parse(temp_xml)
        get_capabilities_root = get_capabilities_tree.getroot()

    #Parse and save informations about server provider
        service_provider = parse_service_provider_info(get_capabilities_root, xml_namespaces)
        service_provider_from_database = search_provider_in_database(service_provider)
        if service_provider_from_database is None:
            service_provider.save()
        else:
            service_provider = service_provider_from_database
    #Parse and save informations about wps server
        wps_server = parse_wps_server_info(get_capabilities_root, xml_namespaces, service_provider)
        wps_server_from_database = search_server_in_database(wps_server)
        if wps_server_from_database is None:
            wps_server.save()
        else:
            wps_server = overwrite_server(wps_server_from_database, wps_server)

    update_wps_processes()


# TODO: tests, documentation
def search_provider_in_database(service_provider):
    """

    :param service_provider:
    :type service_provider:
    :return:
    :rtype:
    """
    for provider in WPSProvider.objects.all():
        if service_provider.provider_name == provider.provider_name \
                and service_provider.provider_site == provider.provider_site:
            return provider

    return None


# TODO: tests, documentation
def search_server_in_database(wps_server):
    """

    :param wps_server:
    :type wps_server:
    :return:
    :rtype:
    """
    for server in WPS.objects.all():
        if server.title == wps_server.title:
            return server

    return None


# TODO: tests, documentation
def overwrite_server(old_entry, new_entry):
    """

    :param old_entry:
    :type old_entry:
    :param new_entry:
    :type new_entry:
    :return:
    :rtype:
    """
    old_entry.abstract = new_entry.abstract
    old_entry.capabilities_url = new_entry.capabilities_url
    old_entry.describe_url = new_entry.describe_url
    old_entry.execute_url = new_entry.execute_url

    old_entry.save()
    return old_entry


# TODO: tests, documentation
def parse_service_provider_info(root, namespaces):
    """

    :param root:
    :type root:
    :param namespaces:
    :type namespaces:
    :return:
    :rtype:
    """
    service_provider_element = root.find('ows:ServiceProvider', namespaces)
    provider_name = service_provider_element.find('ows:ProviderName', namespaces).text
    provider_site = service_provider_element.find('ows:ProviderSite', namespaces).attrib.get(
        '{' + namespaces.get('xlink') + '}href')

    service_contact_element = service_provider_element.find('ows:ServiceContact', namespaces)

    individual_name = service_contact_element.find('ows:IndividualName', namespaces).text
    position_name = service_contact_element.find('ows:PositionName', namespaces).text

    service_provider = WPSProvider(provider_name=provider_name,
                                   provider_site=provider_site,
                                   individual_name=individual_name,
                                   position_name=position_name)
    return service_provider


# TODO: tests, documentation
def parse_wps_server_info(root, namespaces, provider):
    """

    :param root:
    :type root:
    :param namespaces:
    :type namespaces:
    :param provider:
    :type provider:
    :return:
    :rtype:
    """
    service_identification_element = root.find('ows:ServiceIdentification', namespaces)

    server_title = service_identification_element.find('ows:Title', namespaces).text
    server_abstract = service_identification_element.find('ows:Abstract', namespaces).text

    operations_metadata_element = root.find('ows:OperationsMetadata', namespaces)

    urls_elements = operations_metadata_element.findall('ows:Operation/ows:DCP/ows:HTTP/ows:Get', namespaces)
    urls = []
    for item in urls_elements:
        urls.append(item.attrib.get('{' + namespaces.get('xlink') + '}href'))

    wps_server = WPS(service_provider=provider,
                     title=server_title,
                     abstract=server_abstract,
                     capabilities_url=urls[0],
                     describe_url=urls[1],
                     execute_url=urls[2])

    return wps_server

# TODO: tests, documentation
def parse_execute_response(root):
    """

    :param root:
    :type root:
    :return:
    :rtype:
    """
    if root.tag != ns_map["ExecuteResponse"]:
        print(f"false document format - required: ExecuteResponse, found: {root.tag}")
        return 1

    process = root.find(ns_map["Process"])
    process_status = root.find(ns_map["Status"])
    outputs = root.find(ns_map["ProcessOutputs"])

    # TODO get process from db as foreign key for outputs
    try:
        provider = WPSProvider.objects.get(provider_site=root.get('serviceInstance'))
        wps_service = WPS.objects.get(service_provider=provider)
    except WPS.DoesNotExist or WPSProvider.DoesNotExist:
        provider = None
        wps = None

    if process is None:
        print("no process found")
        return 2

    p_id = process.find(ns_map["Identifier"]).text

    try:
        proc = Process.objects.get(wps=wps_service, identifier=p_id)
        task = Task.objects.get(process=proc)
    except Process.DoesNotExist or Task.DoesNotExist as e:
        print(f"{e}:\nobject does not exist in db - maybe false identifier")
        return 2

    if process_status is None:
        print("no status found")
        return 4

    process_status = etree.QName(process_status[0].tag).localname

    new_status = STATUS[3][1] if process_status in possible_stats[:2] else STATUS[4][1]\
                                if process_status == possible_stats[3] else STATUS[5][1]
    # print(new_status)
    task.status = new_status
    task.save()

    if new_status != STATUS[4][1]:
        print("task not finished yet")
        return 4

    outputs = outputs.findall(ns_map["Output"])

    if outputs is None:
        print("no outputs found")
        return 3

    for output in outputs:
        out_id = output.find(ns_map["Identifier"])
        out_title = output.find(ns_map["Title"])

        try:
            inout = InputOutput.objects.get(process=proc, identifier=out_id, title=out_title)
            artefact = Artefact.objects.get(task=task, parameter=inout, role='1')
        except InputOutput.DoesNotExist or Artefact.DoesNotExist as e:
            print(f"{e}:\nobject does not exist in db - maybe false identifier")
            # goto loop header
            continue

        # everything the same up to here for each output type

        data_elem = output.find(ns_map["Data"])
        reference = output.find(ns_map["Reference"])

        if data_elem is not None:
            # normal case, if status is finished

            # as there is always only 1 child, just take the first
            try:
                data_elem = data_elem.getchildren()[0]
            except:
                print("data has no child")
                # goto loop header
                continue

            if data_elem.tag == ns_map["LiteralData"]:
                literal_format = ";".join(("dataType=" + data_elem.get("dataType"), "uom=" + data_elem.get("uom")))
                literal_data = data_elem.text

                if len(literal_data) < 490:
                    artefact.format = literal_format
                    artefact.data = literal_data
                    artefact.save()
                else:
                    # TODO save data to file if length is >= 490, because db only takes 500 chars
                    print()

            if data_elem.tag == ns_map["BoundingBox"]:
                lower_corner = data_elem.find(ns_map["LowerCorner"])
                upper_corner = data_elem.find(ns_map["UpperCorner"])
                lower_corner_info = ";".join(("LowerCorner", "crs:" + lower_corner.get("crs"),
                                              "dimensions" + lower_corner.get("dimensions")))
                upper_corner_info = ";".join(("UpperCorner", "crs:" + upper_corner.get("crs"),
                                              "dimensions" + upper_corner.get("dimensions")))
                bbox_format = "%".join((lower_corner_info, upper_corner_info))

                bbox_data = ";".join(("LowerCorner:" + lower_corner.text, "UpperCorner:" + upper_corner.text))

                artefact.format = bbox_format
                artefact.data = bbox_data
                artefact.save()

            if data_elem.tag == ns_map["ComplexData"]:
                # complex_format = "mimeType:{};encoding:{};schema:{}".format(data_elem.get("mimeType"),
                #                                     data_elem.get("encoding"), data_elem.get("schema"))
                complex_format = ";".join(("mimeType:" + data_elem.get("mimeType"), "encoding:" + data_elem.get("encoding"),
                                              "schema:" + data_elem.get("schema")))
                complex_data = None
                complex_child = data_elem.getchildren()
                if len(complex_child) == 0:
                    complex_data = data_elem.text
                elif data_elem.find(ns_map["CData"]) is not None:
                    # cdata is base64 encoded
                    complex_data = data_elem.find(ns_map["CData"]).text

                if complex_data and len(complex_data) < 490:
                    artefact.format = complex_format
                    artefact.data = complex_data
                    artefact.save()

        if reference is not None:
            # complexdata found, usually gets passed by url reference
            # TODO test ?!
            reference_format = "href:{};mimeType:{};encoding:{};schema:{}".format(reference.get(ns_map["href"]),
                                        reference.get("mimeType"), reference.get("encoding"), reference.get("schema"))
            reference_url = reference.text

            artefact.format = reference_format
            artefact.data = reference_url
            artefact.save()




# TODO: tests, documentation
def update_wps_processes():
    """

    :param wps_server:
    :type wps_server:
    :return:
    :rtype:
    """
    # Works only with absolute path.
    # In future will work with url
    # TODO: change to http request

    #desc_proc_url_from_scc_vm = '/home/denis/Projects/Python/Django/workflowPSE/code/server/base/testfiles/wpsDescribeProcesses.xml'

    xml_namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'xlink': 'http://www.w3.org/1999/xlink',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    wps_servers = WPS.objects.all()
    for wps_server in wps_servers:
        # TODO: repair hardcode
        describe_processes_url = wps_server.describe_url + '?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0'

        temp_xml, headers = urllib.request.urlretrieve(describe_processes_url)

        tree = ET.parse(temp_xml)
        root = tree.getroot()
        process_elements = root.findall('ProcessDescription')
        for process_element in process_elements:
            process = parse_process_info(process_element, xml_namespaces, wps_server)
            process.save()

    ###Save Inputs
            inputs_container_element = process_element.find('DataInputs')
            if inputs_container_element is not None:
                input_elements = inputs_container_element.findall('Input')

                for input_element in input_elements:
                    input = parse_input_info(input_element, xml_namespaces, process)
                    input.save()


    ###Save Outputs
            outputs_container_element = process_element.find('ProcessOutputs')
            if outputs_container_element is not None:
                output_elements = outputs_container_element.findall('Output')

                for output_element in output_elements:
                    output = parse_output_info(output_element, xml_namespaces, process)
                    output.save()


# TODO: tests, documentation
def parse_process_info(process_element, namespaces, wps_server):
    """

    :param process_element:
    :type process_element:
    :param namespaces:
    :type namespaces:
    :param wps_server:
    :type wps_server:
    :return:
    :rtype:
    """
    process_identifier = process_element.find('ows:Identifier', namespaces).text
    process_title = process_element.find('ows:Title', namespaces).text

    process_abstract_element = process_element.find('ows:Abstract', namespaces)
    process_abstract = process_abstract_element.text if process_abstract_element is not None \
        else 'No process description available'

    process = Process(wps=wps_server,
                      identifier=process_identifier,
                      title=process_title,
                      abstract=process_abstract)
    return process


# TODO: tests, documentation
def parse_input_info(input_element, namespaces, process):
    """

    :param input_element:
    :type input_element:
    :param namespaces:
    :type namespaces:
    :param process:
    :type process:
    :return:
    :rtype:
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

    :param output_element:
    :type output_element:
    :param namespaces:
    :type namespaces:
    :param process:
    :type process:
    :return:
    :rtype:
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
    output_abstract = output_abstract_element.text if output_abstract_element is not None else 'No description for output avaible'

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



