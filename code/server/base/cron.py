import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO
from pathlib import Path

import requests
from lxml import etree

import base.utils as utils_module
from base.models import WPS, Task, InputOutput, Artefact, Process, STATUS, Workflow, Edge
from base.utils import ns_map, possible_stats, wps_em, ows_em, xlink_em
from workflowPSE.settings import wpsLog, BASE_DIR
from pathlib import Path
from io import StringIO, BytesIO

def scheduler():
    """
    Main scheduling function. Schedules Tasks in Workflows according to their execution order, generates execution XML files and sends tasks to
    their server for execution
    @return: None
    @rtype: NoneType
    """

    # TODO: set to changeable by settings & config file

    dir_path = os.path.dirname(os.path.abspath(__file__))
    outFile = os.path.join(dir_path, 'outfile.txt')
    xmlDir = os.path.join(dir_path, 'testfiles/')

    # redirect stout to file, output logging
    orig_stdout = sys.stdout
    f = open(outFile, 'w')
    sys.stdout = f

    exec_list = []

    for current_workflow in Workflow.objects.all():
        try:
            all_tasks = Task.objects.filter(workflow=current_workflow, status='1')
        except Task.DoesNotExist:
            all_tasks = []
        for current_task in all_tasks:
            previous_tasks_finished = True
            try:
                edges_to_current_task = Edge.objects.filter(to_task=current_task)
            except Edge.DoesNotExist:
                edges_to_current_task = []
            for current_edge in edges_to_current_task:
                if current_edge.from_task.status == '4':
                    if not Artefact.objects.filter(taks=current_task, role='0'):
                        previous_tasks_finished = False
                        break
                    else:
                        for current_artefact in Artefact.objects.filter(taks=current_task, role='0'):
                            if not current_artefact.data:
                                previous_tasks_finished = False
                                break
                else:
                    previous_tasks_finished = False
                    break
            if previous_tasks_finished:
                current_task.status = '2'
                exec_list.append(current_task.id)
                current_task.save()

    # generate execute xmls for all tasks with status waiting
    xmlGenerator(xmlDir)

    # send tasks
    for tid in exec_list:
        sendTask(tid, xmlDir)

    # Reset exec list
    exec_list = []

    sys.stdout = orig_stdout
    f.close()


def xmlGenerator(xmlDir):
    """
    Traverses Database and generates execution XML files for every Task set to status WAITING
    @param xmlDir: Directory where XMLs are generated in
    @type xmlDir: string
    @return: None
    @rtype: NoneType
    """

    try:
        task_list = list(Task.objects.filter(status='2'))
    except Task.DoesNotExist:
        task_list = []

    for task in task_list:
        try:
            process = task.process
        except Process.DoesNotExist:
            # process not found
            return

        root = wps_em.Execute(ows_em.Identifier(process.identifier))
        inputs_tree = createDataDoc(task)

        if inputs_tree == 1:
            # error code, something wrong with task formatting TODO: check for better handling
            continue

        root.append(inputs_tree)
        # TODO: complete

        response_form = wps_em.ResponseForm()
        response_doc = wps_em.ResponseDocument()

        output_list = list(InputOutput.objects.filter(process_id=task.process, role='1'))
        for output in output_list:
            output_element = wps_em.Output(ows_em.Identifier(output.identifier), ows_em.Title(output.title))



def createDataDoc(task):
    inputs = list(InputOutput.objects.filter(process_id=task.process, role='0'))
    data_inputs = wps_em.DataInputs()

    for input in inputs:
        # literal data case, there is either a url or real data in the LiteralData element
        # in this case just send the data
        if input.datatype == '0':
            try:
                artefact = Artefact.objects.get(task=task, parameter=input, role='0')
            except:
                # something is wrong here if artefact has not been created yet
                return 1
            data_inputs.append(wps_em.Input(ows_em.Identifier(input.identifier), ows_em.Title(input.title),
                                            wps_em.Data(wps_em.LiteralData(artefact.data))))
        # complex data case, first try to parse xml, if successfully append to ComplexData element
        #                    second check if there is CDATA ??
        if input.datatype == '1':
            try:
                # try to parse as xml
                data = etree.parse(artefact.data)
            except:
                # if it is no xml, check if it is a file path, if so insert file path in Reference node
                if artefact.data == utils_module.getFilePath(artefact):
                    data_inputs.append(wps_em.Input(ows_em.Identifier(input.identifier), ows_em.Title(input.title),
                                                    wps_em.Reference({"method": "GET"},
                                                                     {ns_map["href"]:utils_module.getFilePath(artefact)})))
                    return data_inputs
                # else check if there is cdata
                #elif len(artefact.data.split("CDATA")) != 1:
                    # when to use cdata for requests?
                    #data = artefact.data.lstrip("<![CDATA[").rstrip("]]>")
                else:
                    try:
                        data = artefact.data
                    except:
                        return 1
            data_inputs.append(wps_em.Input(ows_em.Identifier(input.identifier), ows_em.Title(input.title),
                                            wps_em.Data(data)))
        # bounding box case there should just be lowercorner and uppercorner data
        if input.datatype == '2':
            # TODO: complete
            pass

    return data_inputs

'''
    try:
        # Traverse Task table entries with status WAITING
        task_list = list(Task.objects.filter(status='2').values())
    except Task.DoesNotExist:
        task_list = []

    for task in task_list:

        # Create root node
        root = ET.Element('wps:Execute')
        root.set('service', 'WPS')
        root.set('version', '1.0.0')
        root.set('xmlns:wps', 'http://www.opengis.net/wps/1.0.0')
        root.set('xmlns:ows', 'http://www.opengis.net/ows/1.1')
        root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation', 'http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd')

        try:
            # Traverse Process table entries with id of task
            process_list = list(Process.objects.filter(id=task["process_id"]).values())
        except Process.DoesNotExist:
            process_list = []
        for process in process_list:
            # Create Identifier node
            identifier = ET.SubElement(root, 'ows:Identifier')
            identifier.text = process["identifier"]

        # Create DataInputs node
        inputs = ET.SubElement(root, 'wps:DataInputs')

        try:
            # Traverse InputOutput table entries linked to Process
            input_list = list(InputOutput.objects.filter(process_id=task["process_id"], role='0').values())
        except InputOutput.DoesNotExist:
            input_list = []
        for input in input_list:

            # Create Input node
            inputElement = ET.SubElement(inputs, 'wps:Input')
            inputIdent = ET.SubElement(inputElement, 'ows:Identifier')
            inputTitle = ET.SubElement(inputElement, 'ows:Title')
            inputData = ET.SubElement(inputElement, 'wps:Data')
            inputIdent.text = input["identifier"]
            inputTitle.text = input["title"]

            try:
                # Traverse Artefact table entries linked to Process
                artefact_list = list(Artefact.objects.filter(task_id=task["id"], parameter=input["id"]).values())
            except Artefact.DoesNotExist:
                artefact_list = []

            for artefact in artefact_list:

                type = input["datatype"]
                if type == '0':
                    type = "LiteralData"
                elif type == '1':
                    type = "ComplexData"
                elif type == '2':
                    type = "BoundingBoxData"

                # Create Data node
                data = ET.SubElement(inputData, 'wps:' + type)
                data.text = artefact["data"]
                data.set('datatype', artefact["format"])

        # Create ResponseForm node for status url
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

        # Write XML to file
        tree = ET.ElementTree(root)
        tree.write(xmlDir + 'task' + str(task["id"]) + '.xml')
'''


def sendTask(task_id, xmlDir):
    """
    Sends a Task identified by its Database ID to its WPS Server.
    @param task_id: ID of Task in Database
    @type task_id: int
    @param xmlDir: Directory where XMLs are stored in
    @type xmlDir: string
    @return: None
    @rtype: NoneType
    """
    filepath = str(xmlDir) + 'task' + str(task_id) + '.xml'
    if Path(filepath).is_file() is False:
        print("file for task ", task_id, " does not exist, aborting...")
        return

    try:
        # This only is outsourced to extra function for better readability
        execute_url = getExecuteUrl(Task.objects.get(id=task_id))
    except Task.DoesNotExist:
        execute_url = ""

    if execute_url is "":
        print("Error, execute url is empty, but is not allowed to. Aborting...")
        return
    # TODO: validate execution url
    file = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>' + str(open(filepath, 'r').read())

    # send to url
    response = requests.post(execute_url, data=file)  # 'http://pse.rudolphrichard.de:5000/wps'

    # if the response is not in xml format
    try:
        # get response from send
        xml = ET.fromstring(response.text)
    except:
        print("xml could not be parsed")

    acceptedElement = xml.findall('wps:ProcessAccepted')
    if acceptedElement is None:
        print("An Error occured while sending Task ", task_id, " to the server, proccess not accepted")
        return

    try:
        # Update DB Entry
        p = Task.objects.get(id=task_id)
        p.status_url = xml.get('statusLocation')
        p.status = '3'
        p.started_at = datetime.now()
        print(p.started_at)
        p.save()
    except Task.DoesNotExist:
        print("task not found")
        return
    

    # Delete execution XML
    if os.path.isfile(filepath):
        os.remove(filepath)


def getExecuteUrl(task):
    """
    Extracts the Execute URL from the Database for a given task. Returns empty string on error.
    @param task: Task object from Database
    @type task: Task
    @return: Execute URL. Empty on error or empty DB field
    @rtype: string
    """
    execute_url = ""

    try:
        process = Process.objects.get(id=task.process_id)
        wps = WPS.objects.get(id=process.wps_id)
        execute_url = wps.execute_url
    except Process.DoesNotExist or WPS.DoesNotExist:
        execute_url = ""

    return execute_url


# TODO: tests
def receiver():
    """
    loops all running tasks
    parses xml on server and checks for status
    overwrites status if changed
    if task is finished, write data to db
    @return: None
    @rtype: NoneType
    """
    try:
        running_tasks = list(Task.objects.filter(status='3'))
        wpsLog.info("receiver starting")
    except Task.DoesNotExist:
        running_tasks = []
        wpsLog.info("no running tasks found")
    for task in running_tasks:
        parseExecuteResponse(task)


# TODO: tests
def parseExecuteResponse(task):
    """
    checks parameter tasks status by checking xml file found at status_url for change
    if task has finished write data to db if there is any data
    @param task: the task whose status is currently checked
    @type task: subclass of models.Model
    @return: 0 on success, error code otherwise
    @rtype: int
    """

    # try to parse document which should be returned by request
    try:
        root = etree.parse(StringIO(requests.get(task.status_url).text))
    except ValueError:
        '''
        might throw ValueError if CDATA is placed within document:
        ValueError: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
        in this case try to parse document by encoding and reading in BytesIO buffer bevore parsing
        '''
        root = etree.parse(BytesIO(requests.get(task.status_url).text.encode()))
    except:
        # otherwise just exit and return error code
        wpsLog.info(f"request for task {task.id} could not be parsed")
        return 1

    process_info = root.find(ns_map["Process"])
    try:
        process_outputs = root.find(ns_map["ProcessOutputs"])
        output_list = process_outputs.findall(ns_map["Output"])
    except:
        # no Processes in output
        output_list = []

    if process_info is None:
        wpsLog.info("Process information not found")
        return 2

    for output in output_list:
        parseOutput(output, task)
    try:
        process_status = root.find(ns_map["Status"])
    except:
        wpsLog.info("no status found")

    process_status = etree.QName(process_status[0].tag).localname
    new_status = STATUS[3][0] if process_status in possible_stats[:2] else STATUS[4][0] \
        if process_status == possible_stats[3] else STATUS[5][0]

    if task.status != new_status:
        task.status = new_status
        task.save()
    else:
        task.status = STATUS[5][0]
        task.save()
    task.workflow.percent_done = calculate_percent_done(task)
    if process_status is None:
        wpsLog.info("no status found")
        return 3

# TODO: tests
def parseOutput(output, task):
    """
    parses output node of xml and inserts respective data if found
    also updates status of task if there are any changes
    @param output the output that has to be parsed
    @type output lxmls.etree._Element
    @param task: the task that belongs to the output
    @type task: subclass of models.Model
    @return: None
    @rtype: NoneType
    """

    out_id = output.find(ns_map["Identifier"]).text

    try:
        output_db = InputOutput.objects.get(process=task.process, identifier=out_id, role='1')
        artefact = Artefact.objects.get(task=task, parameter=output_db, role='1')
        edge = Edge.objects.get(from_task=task, output=output_db)
    except BaseException as e:
        time_now = datetime.now()
        wpsLog.info("output artefact not found, creating new artefact")
        artefact = Artefact.objects.create(task=task, parameter=output_db, role='1',
                                           created_at=time_now, updated_at=time_now)
    if artefact is None:
        wpsLog.info("artefact does not match")
        return

    # everything is the same up to here for each output type
    data_elem = output.find(ns_map["Data"])
    reference = output.find(ns_map["Reference"])
    time_now = datetime.now()

    if data_elem is not None:
        try:
            # there should always be just one status!
            data_elem = data_elem.getchildren()[0]
        except:
            wpsLog.info("data has no child")
            # goto loop header
            return

        if data_elem.tag == ns_map["LiteralData"]:
            d_attribs = data_elem.attrib
            db_format = ""
            for attrib in d_attribs:
                db_format += f";{attrib}={d_attribs[attrib]}"
            db_format.strip(";")
            db_data = data_elem.text

            # if the string is less than 490 chars long write to db
            # otherwise write to file and write url to db
            if len(db_data) < 490:
                artefact.format = db_format
                artefact.data = db_data
                artefact.updated_at = time_now
                artefact.save()

            else:
                # TODO set path to file properly so user can access via url - test !
                file_name = f"outputs/wfID{task.workflow.id}_taskID{task.id}.xml"
                with open(file_name, 'w') as tmpfile:
                    tmpfile.write(db_data)
                artefact.format = db_format
                artefact.data = f"{BASE_DIR}/{file_name}"
                artefact.updated_at = time_now
                artefact.save()

        elif data_elem.tag == ns_map["BoundingBox"]:
            lower_corner = data_elem.find(ns_map["LowerCorner"])
            upper_corner = data_elem.find(ns_map["UpperCorner"])
            d_attribs = data_elem.attrib
            db_format = ""
            for attrib in d_attribs:
                db_format += f";{attrib}={d_attribs[attrib]}"
            db_format.strip(";")
            db_data = f"LowerCorner:{lower_corner.text};UpperCorner:{upper_corner.text}"

            artefact.format = db_format
            artefact.data = db_data
            artefact.updated_at = time_now
            artefact.save()

        elif data_elem.tag == ns_map["ComplexData"]:
            # TODO: test!
            d_attribs = data_elem.attrib
            db_format = ""
            for attrib in d_attribs:
                db_format += f";{attrib}={d_attribs[attrib]}"
            db_format.strip(";")
            db_data = data_elem.text
            artefact.format = db_format

            if db_data is not None:
                # if the string is less than 490 chars long write to db
                # otherwise write to file and write url to db
                if len(db_data) < 490:
                    artefact.data = db_data
                    artefact.updated_at = time_now
                    artefact.save()

                else:
                    file_name = f"outputs/wfID{task.workflow.id}_taskID{task.id}.xml"
                    with open(file_name, 'w') as tmpfile:
                        tmpfile.write(db_data)
                    artefact.data = f"{BASE_DIR}/{file_name}"
                    artefact.updated_at = time_now
                    artefact.save()

            elif "CDATA" in data_elem.text:
                # if the string is less than 490 chars long write to db
                # otherwise write to file and write url to db
                db_data = data_elem.text
                if len(db_data) < 490:
                    artefact.data = db_data
                    artefact.updated_at = time_now
                    artefact.save()

                else:
                    file_name = f"outputs/wfID{task.workflow.id}_taskID{task.id}.xml"
                    with open(file_name, 'w') as tmpfile:
                        tmpfile.write(db_data)
                    artefact.data = f"{BASE_DIR}/{file_name}"
                    artefact.updated_at = time_now
                    artefact.save()

            # if there is at least one other child, there seems to be a subtree
            elif len(data_elem.getchildren()) != 0:

                # read the subtree to string with pretty_print syntax
                db_data = etree.tostring(data_elem, pretty_print=True)

                # if the string is less than 490 chars long write to db
                # otherwise write to file and write url to db
                if len(db_data) < 490:
                    artefact.data = db_data
                    artefact.updated_at = time_now
                    artefact.save()
                else:
                    file_name = f"outputs/wfID{task.workflow.id}_taskID{task.id}.xml"
                    with open(file_name, 'w') as tmpfile:
                        tmpfile.write(db_data)
                    artefact.data = f"{BASE_DIR}/{file_name}"
                    artefact.updated_at = time_now
                    artefact.save()
            else:
                wpsLog.info("no complex data found in complexdata tree element")
    elif reference is not None:
        # complexdata found, usually gets passed by url reference which won't be 500 chars long
        # TODO: test ?!
        d_attribs = data_elem.attrib
        db_format = ""
        for attrib in d_attribs:
            db_format += f";{attrib}={d_attribs[attrib]}"
        db_format.strip(";")
        db_data = reference.text  # should be a url

        artefact.format = db_format
        artefact.data = db_data
        artefact.updated_at = time_now
        artefact.save()
    if db_data is not None:
        try:
            to_artefact = Artefact.objects.get(task=edge.to_task, parameter=edge.input, role='0')
            to_artefact.format = db_format
            to_artefact.data = db_data
            to_artefact.updated_at = time_now
            to_artefact.save()
        except Artefact.DoesNotExist:
            wpsLog.info("input artefact not found, creating new artefact")
            Artefact.objects.create(task=edge.to_task, parameter=edge.input, role='0', format=db_format,
                                    data=db_data, created_at=time_now, updated_at=time_now)

# TODO: tests
def calculate_percent_done(task):
    """
    calculates the percentage of finished tasks in the workflow of task
    @param task: task with recently changed status
    @type task: Task
    @return: percentage of finished tasks in the workflow of task
    @rtype: int
    """
    err = list(Task.objects.filter(workflow=task.workflow, status='5'))
    if len(err):
        percent_done = -1
        Task.objects.filter(workflow=task.workflow).update(status='5')
    else:
        finished = list(Task.objects.filter(workflow=task.workflow, status='4'))
        all_wf_tasks = list(Task.objects.filter(workflow=task.workflow))
        percent_done = int(len(finished) / len(all_wf_tasks))

    return percent_done



def update_wps_processes():
    """
    This method update the list of WPS processes provided by the WPS Server.
    It takes a describe_processes_url of each wps server saved in database,
    open it, and parses the xml file, that comes in request message.

    It will be checked if any object present in database.
    If no, it will be saved, else it will be overwritten with the actual
    information provided by the WPS server.

    @return: None
    @rtype: None
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
