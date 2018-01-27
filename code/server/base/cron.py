import os, sys
import random
import base.utils as utils_module
import xml.etree.ElementTree as ET
from base.models import WPSProvider, WPS, Task, InputOutput, Artefact, Process, ROLE, DATATYPE, STATUS, Workflow, Edge
from django.http import response
import requests
import urllib.request
from datetime import datetime, timezone
from lxml import etree
from base.utils import ns_map, possible_stats
from workflowPSE.settings import wpsLog
from pathlib import Path

# TODO: naming convention, code formatting

# TODO: tests
def scheduler():
    """
 
    @return:
    @rtype:
    """
    
    # TODO: set to changeable by settings & config file
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    outFile = os.path.join(dir_path, 'outfile.txt')    
    xmlDir = os.path.join(dir_path, 'testfiles/')

    # redirect stout to file, output logging
    orig_stdout = sys.stdout
    f = open(outFile, 'w')
    sys.stdout = f

    for current_workflow in Workflow.objects.all():
        for current_task in Task.objects.filter(workflow = current_workflow, status = 1):
            previous_tasks_finished = True
            for current_edge in Edge.objects.filter(to_task = current_task):
                if current_edge.from_task.status == '4':
                    previous_tasks_finished = True
                else:
                    previous_tasks_finished = False
                    break
            if previous_tasks_finished:
                current_task.status = '2'
                current_task.save()

    




    #generate execute xmls for all tasks with status waiting
    xmlGenerator(xmlDir)

    #send task
    #sendTask(2, xmlDir)

    sys.stdout = orig_stdout
    f.close()


# TODO: tests, documentation
def xmlGenerator(xmlDir):
    """
    generates xml for every task set to ready
    @param xmlDir:
    @type xmlDir:
    @return:
    @rtype:
    """
    task_list = list(Task.objects.filter(status='2').values())
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

    @param task_id:
    @type task_id:
    @param xmlDir:
    @type xmlDir:
    @return:
    @rtype:
    """
    filepath = str(xmlDir) + 'task' + str(task_id) + '.xml'
    if Path(filepath).is_file() is False:
        print("file for task ", task_id, " does not exist, aborting...")
        return
        
    #should be changed to something without list
    task_list = list(Task.objects.filter(id=task_id).values())
    for task in task_list:

        execute_url = getExecuteUrl(task)

        #send to url
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
        acceptedElement = xml.findall('wps:ProcessAccepted')
        if acceptedElement is None:
            print("An Error occured while sending Task ", task_id, " to the server, proccess not accepted")
            return
        
        
        print(xml.get('statusLocation'))

        # write status url from response to task
        # set status to running
        # update start time
        p = Task.objects.get(id=task_id)
        p.status_url = xml.get('statusLocation')
        p.status = '3'
        p.started_at = datetime.now()
        p.save()
        # TODO: delete execute xml file
        
    if os.path.isfile(filepath):
        os.remove(filepath)
        

# TODO: tests, documentation
def getExecuteUrl(task):
    """

    @param task:
    @type task:
    @return:
    @rtype:
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

    @return:
    @rtype:
    """
    #execute policy
    pass


# TODO: tests, documentation, implement
def receiver():
    """

    @return:
    @rtype:
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

    @return:
    @rtype:
    """
    # Main fuction for combined utility functions
    pass



# TODO: remove, left here for compatibility because all other collaborators don't push their progress
def xmlParser():
    """

    @return:
    @rtype:
    """
    #parses input xml
    #checks data for changes
    #writes changes to db
    pass


# TODO: tests, documentation, implement
def listExistingFiles():
    """

    @return:
    @rtype:
    """
    #part of datenhaltung
    #generates a list of all uploaded files, their upload date, last edit, editor, etc
    pass


# TODO: tests, documentation, implement
def deleteOldFiles():
    """

    @return:
    @rtype:
    """
    #part of datenhaltung
    #deletes files with last edit date > limit or other defined rule
    pass


# TODO: tests, documentation
def parse_execute_response(xml_file):
    """

    @param root:
    @type root:
    @return:
    @rtype:
    """

    root = etree.XML(xml_file.read())

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
        wpsLog.info("no process found")
        return 2

    p_id = process.find(ns_map["Identifier"]).text

    try:
        proc = Process.objects.get(wps=wps_service, identifier=p_id)
        task = Task.objects.get(process=proc)
    except Process.DoesNotExist or Task.DoesNotExist as e:
        wpsLog.info(f"{e}:\nobject does not exist in db - maybe false identifier")
        return 2

    if process_status is None:
        wpsLog.info("no status found")
        return 4

    process_status = etree.QName(process_status[0].tag).localname

    new_status = STATUS[3][1] if process_status in possible_stats[:2] else STATUS[4][1]\
                                if process_status == possible_stats[3] else STATUS[5][1]
    # print(new_status)
    task.status = new_status
    task.save()

    if new_status != STATUS[4][1]:
        wpsLog.info("task not finished yet")
        return 4

    outputs = outputs.findall(ns_map["Output"])

    if outputs is None:
        wpsLog.info("no outputs found")
        return 3

    for output in outputs:
        out_id = output.find(ns_map["Identifier"])
        out_title = output.find(ns_map["Title"])

        try:
            inout = InputOutput.objects.get(process=proc, identifier=out_id, title=out_title)
            artefact = Artefact.objects.get(task=task, parameter=inout, role='1')
        except InputOutput.DoesNotExist or Artefact.DoesNotExist as e:
            wpsLog.info(f"{e}:\nobject does not exist in db - maybe false identifier")
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
                wpsLog.info("data has no child")
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
                    wpsLog.info("")

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

                if complex_data:
                    if len(complex_data) < 490:
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

    @return:
    @rtype:
    """
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
            process = utils_module.parse_process_info(process_element, xml_namespaces, wps_server)
            process_from_database = utils_module.search_process_in_database(process)
            if process_from_database is None:
                process.save()
            else:
                process = utils_module.overwrite_process(process_from_database, process)

    ###Save Inputs
            inputs_container_element = process_element.find('DataInputs')
            if inputs_container_element is not None:
                input_elements = inputs_container_element.findall('Input')

                for input_element in input_elements:
                    input = utils_module.parse_input_info(input_element, xml_namespaces, process)
                    input_from_database = utils_module.search_input_output_in_database(input)
                    if input_from_database is None:
                        input.save()
                    else:
                        input = utils_module.overwrite_input_output(input_from_database, input)


    ###Save Outputs
            outputs_container_element = process_element.find('ProcessOutputs')
            if outputs_container_element is not None:
                output_elements = outputs_container_element.findall('Output')

                for output_element in output_elements:
                    output = utils_module.parse_output_info(output_element, xml_namespaces, process)
                    output_from_database = utils_module.search_input_output_in_database(output)
                    if output_from_database is None:
                        output.save()
                    else:
                        output = utils_module.overwrite_input_output(output_from_database, output)