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
from base.utils import ns_map, wps_em, ows_em
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
    wpsLog.debug("starting schedule")
    dir_path = os.path.dirname(os.path.abspath(__file__))
    outFile = os.path.join(dir_path, 'outfile.txt')
    xmlDir = os.path.join(dir_path, 'testfiles/')

    # redirect stout to file, output logging
    # orig_stdout = sys.stdout
    # f = open(outFile, 'w')
    # sys.stdout = f

    exec_list = []

    for current_workflow in Workflow.objects.all():
        all_tasks = Task.objects.filter(workflow=current_workflow, status='1')
        wpsLog.debug(
            f"found {len(all_tasks)} tasks in workflow{current_workflow.id}")
        for current_task in all_tasks:
            previous_tasks_finished = True
            edges_to_current_task = Edge.objects.filter(to_task=current_task)
            wpsLog.debug(
                f"found {len(edges_to_current_task)} edges to task{current_task.id} in workflow{current_workflow.id}")
            for current_edge in edges_to_current_task:
                if current_edge.from_task.status == '4':
                    wpsLog.debug(
                        f"task{current_task.id}'s prior task{current_edge.from_task.id} is finished")
                    if not Artefact.objects.filter(task=current_task, role='0'):
                        wpsLog.warning(f"something is wrong here, task{current_task.id} has no artefacts,"
                                       f"but there should at least be input artefacts")
                        previous_tasks_finished = False
                        break
                    else:
                        for current_artefact in Artefact.objects.filter(task=current_task, role='0'):
                            wpsLog.debug(
                                f"checking data of artefact{current_artefact.id} of task{current_task.id}")
                            if not current_artefact.data:
                                wpsLog.warning(
                                    f"task{current_task.id} has artefact{current_artefact.id} which has no data")
                                previous_tasks_finished = False
                                break
                else:
                    wpsLog.debug(
                        f"task{current_task.id}s prior task{current_edge.from_task.id} is not finished")
                    previous_tasks_finished = False
                    break
            if previous_tasks_finished:
                wpsLog.debug(
                    f"previous task is finished, scheduling now following task{current_task.id}")
                current_task.status = '2'
                exec_list.append(current_task.id)
                current_task.save()

    # generate execute xmls for all tasks with status waiting
    xmlGenerator(xmlDir)

    wpsLog.debug(f"xmls generated for tasks: {exec_list}")

    # send tasks
    for tid in exec_list:
        print(tid)
        sendTask(tid, xmlDir)

    # sys.stdout = orig_stdout
    # f.close()


def xmlGenerator(xmlDir):
    """
    Traverses Database and generates execution XML files for every Task set to status WAITING
    @param xmlDir: Directory where XMLs are generated in
    @type xmlDir: string
    @return: None
    @rtype: NoneType
    """
    wpsLog.debug("starting xml generator")
    try:
        task_list = list(Task.objects.filter(status='2'))
    except Task.DoesNotExist:
        wpsLog.debug("no running tasks found")
        task_list = []
    wpsLog.debug(f"scheduled tasks: {[task.id for task in task_list]}")
    for task in task_list:
        try:
            process = task.process
        except Process.DoesNotExist:
            # process not found
            wpsLog.warning(f"process of task{task.id} not found")
            return
        root = wps_em.Execute(ows_em.Identifier(process.identifier))
        root.set('service', 'WPS')
        root.set('version', '1.0.0')
        inputs_tree = createDataDoc(task)
        if inputs_tree == 1:
            # error code, something wrong with task TODO: check for better handling?
            wpsLog.warning(f"Error: missing input artefact for task{task.id}")
            continue
        root.append(inputs_tree)

        wpsLog.debug(
            f"successfully inserted inputs to xml document for task{task.id}")

        response_doc = wps_em.ResponseDocument()
        response_doc.set('storeExecuteResponse', 'true')
        response_doc.set('lineage', 'true')
        response_doc.set('status', 'true')

        output_list = list(InputOutput.objects.filter(
            process=task.process, role='1'))
        wpsLog.debug(
            f"list of outputs of task{task.id}: {[output.id for output in output_list]}")
        for output in output_list:
            response_doc.append(wps_em.Output(ows_em.Identifier(output.identifier), ows_em.Title(output.title),
                                              {'asReference': 'true'}))

        root.append(wps_em.ResponseForm(response_doc))

        wpsLog.debug(f"successfully created xml for task{task.id}")

        # write to file, for testing let pretty_print=True for better readability
        # TODO: rework if file path problem is solved
        try:
            with open(f"{xmlDir}/task{task.id}.xml", 'w') as xml_file:
                xml_file.write(etree.tostring(
                    root, pretty_print=True).decode())
            wpsLog.debug(
                f"successfully written xml of task{task.id} to file, ready for sending to server")
        except:
            wpsLog.warning(f"writing failed for task{task.id}")


def createDataDoc(task):
    """
    creates subtree for execute request for model.Task task
    @return: subtree on success, error code 1 otherwise
    @rtype: lxml.etree._Element/int
    """
    # returns [] if no match found
    wpsLog.debug(f"creating data subtree for task{task.id}")
    inputs = list(InputOutput.objects.filter(process=task.process, role='0'))
    data_inputs = wps_em.DataInputs()
    wpsLog.debug(f"found inputs: {[input.id for input in data_inputs]}")
    for input in inputs:
        # try to get artefact from db
        try:
            artefact = Artefact.objects.get(task=task, parameter=input)
        except:
            # something is wrong here if artefact has not been created yet
            # as execute documents for next execution are only started if previous task has finished
            # and when previous task has finished, the output data is automatically passed to next tasks input
            wpsLog.warning(
                f"Error: artefact for task{task.id}s input{input.id} has not been created yet")
            return 1

        # create identifier and title as they are used in any case
        identifier = ows_em.Identifier(input.identifier)
        title = ows_em.Title(input.title)

        # first check if it is a file path, as data with length over 490 chars will be stored in a file
        # if so insert file path in Reference node
        if artefact.data == utils_module.getFilePath(task):
            wpsLog.debug(
                f"file path found in task{task.id}s artefact{artefact.id}s data, inserting as data")
            data_inputs.append(wps_em.Input(identifier, title, wps_em.Reference({"method": "GET"},
                                                                                {ns_map["href"]: utils_module.getFilePath(artefact)})))
            # go to loop header and continue
            continue

        wpsLog.debug(
            f"no file path as data in task{task.id}s artefact{artefact.id}")
        # literal data case, there is either a url or real data in the LiteralData element
        # in this case just send the data
        if input.datatype == '0':
            wpsLog.debug(f"literal data found for task{task.id}")
            literal_data = wps_em.LiteralData(artefact.data)
            # check for attributes
            for attribute in artefact.format.split(";"):
                if "uom" in attribute:
                    literal_data.set("uom", attribute.split("=")[1])
                if "dataType" in attribute:
                    literal_data.set("dataType", attribute.split("=")[1])
            # just create subtree with identifier, title and data with nested literaldata containing the artefacts data
            data_inputs.append(wps_em.Input(
                identifier, title, wps_em.Data(literal_data)))
        # complex data case, first try to parse xml, if successfully append to ComplexData element
        #                    second check if there is CDATA ??
        elif input.datatype == '1':
            wpsLog.debug(f"complex data found for task{task.id}")
            # append format data as attributes to complex data element
            complex_data = wps_em.ComplexData()
            for attribute in artefact.format.strip("CDATA;").split(";"):
                complex_data.set(attribute.split(
                    "=")[0], attribute.split("=")[1])
            # check if there is cdata in format
            if artefact.format.split(";")[0] == "CDATA":
                wpsLog.debug(
                    f"cdata found in task{task.id} inserting cdata nested in tags into data of artefact{artefact.id}")
                complex_data.append(f"<![CDATA[{artefact.data}]]")
                # put data nested in cdata tag in complex data element
                data_inputs.append(wps_em.Input(
                    identifier, title, wps_em.Data(complex_data)))
            else:
                # just append it as if it is in xml format, it can also be inserted as text, will then not be in
                # pretty_print format, but wps server doesn't care about that
                wpsLog.debug(
                    f"just inserting complex data for task{task.id} of artefact{artefact.id} in xml")
                data_inputs.append(wps_em.Input(
                    identifier, title, wps_em.Data(artefact.data)))
        # bounding box case there should just be lowercorner and uppercorner data
        elif input.datatype == '2':
            wpsLog.debug(f"boundingbox data found for task{task.id}")
            lower_corner = ows_em.LowerCorner()
            upper_corner = ows_em.UpperCorner()
            for data in artefact.data.split(";"):
                if data.split("=")[0] == "LowerCorner":
                    lower_corner.append(data.split("=")[1])
                elif data.split("=")[0] == "UpperCorner":
                    upper_corner.append(data.split("=")[1])
            # quite strange, but this node is called BoundingBoxData for inputs, for outputs it's just BoundingBox
            # also for inputs it is used with wps namespace, for outputs the ows namespace is used
            bbox_elem = wps_em.BoundingBoxData(lower_corner, upper_corner)
            # set attributes of boundingboxdata if there were any
            for attribute in artefact.format.split(";"):
                bbox_elem.set(attribute.split("=")[0], attribute.split("=")[1])
            # finally create subtree
            data_inputs.append(wps_em.Input(identifier, title, bbox_elem))
    # TODO: check if something is missing
    wpsLog.debug(f"finished input xml generation for task{task.id}")
    return data_inputs


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
    print(filepath)
    print(os.path.isfile(filepath))
    if Path(filepath).is_file() is False:
        wpsLog.warning(f"file for task {task_id} does not exist, aborting...")
        return
    try:
        # This only is outsourced to extra function for better readability
        execute_url = getExecuteUrl(Task.objects.get(id=task_id))
    except Task.DoesNotExist:
        wpsLog.warning(
            "Error, execute url is empty, but is not allowed to. Aborting...")
        return

    # TODO: validate execution url
    file = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>' + \
        str(open(filepath, 'r').read())

    # send to url
    try:
        # 'http://pse.rudolphrichard.de:5000/wps'
        response = requests.post(execute_url, data=file)
    except:
        wpsLog.warning(
            f"request for task{task_id} could not be posted, aborting")
        return

    # if the response is not in xml format
    try:
        # get response from send
        xml = ET.fromstring(response.text)
    except:
        wpsLog.warning(f"xml could not be parsed for task{task_id}")
    acceptedElement = xml.findall('wps:ProcessAccepted')
    if acceptedElement is None:
        wpsLog.warning(
            f"An Error occured while sending task{task_id} to the server, proccess not accepted")
        return

    try:
        # TODO refactor dirty fix
        status_url = xml.get('statusLocation')
        if status_url is not None:
            status_url = "http://" + status_url.lstrip("http://")

        # Update DB Entry
        p = Task.objects.get(id=task_id)
        p.status_url = status_url
        p.status = '3'
        p.started_at = datetime.now()
        wpsLog.debug(f"task{task_id} started at {p.started_at}")
        p.save()
    except Task.DoesNotExist:
        wpsLog.warning(f"task{task_id} not found, aborting")
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
    wpsLog.debug("starting receiver")
    running_tasks = list(Task.objects.filter(status='3'))
    wpsLog.debug(f"found {len(running_tasks)} running tasks: {running_tasks}")
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
        root = etree.parse(
            BytesIO(requests.get(task.status_url).text.encode()))
    except:
        # otherwise just exit and return error code
        wpsLog.debug(
            f"request of {task.status_url} for task {task.id} could not be parsed")
        return 1

    process_info = root.find(ns_map["Process"])
    try:
        output_list = root.find(
            ns_map["ProcessOutputs"]).findall(ns_map["Output"])
    except:
        # no Processes in output
        wpsLog.warning(f"response xml for task{task.id} has no output nodes")
        output_list = []

    if process_info is None:
        wpsLog.warning(f"Process information not found for task{task.id}")
        return 2

    for output in output_list:
        parseOutput(output, task)

    try:
        process_status = root.find(ns_map["Status"])
        status_name = etree.QName(process_status[0].tag).localname
    except:
        wpsLog.warning(f"no status found in xml for task{task.id}")
        return 2

    new_status = STATUS[3][0] if status_name in ["ProcessAccepted", "ProcessStarted", "ProcessPaused"] \
        else STATUS[4][0] if status_name == "ProcessSucceeded" else STATUS[5][0]

    if task.status != new_status:
        wpsLog.debug(
            f"old status of task{task.id}: {task.status}, new status: {new_status}")
        task.status = new_status
        task.save()

    # if status failed, create error output artefacts for task
    if task.status == '5':
        try:
            err_msg = process_status[0].find(f"{ns_map['ExceptionReport']}/"
                                             f"{ns_map['Exception']/{ns_map['ExceptionText']}}").text
        except:
            err_msg = "unknown error"

        time_now = datetime.now()
        for output in list(InputOutput.objects.filter(artefact__task=task, role='1')):
            if len(list(Artefact.objects.filter(task=task, parameter=output, role='1'))) == 0:
                Artefact.objects.create(task=task, parameter=output, role='1', format='error', data=err_msg,
                                        created_at=time_now, updated_at=time_now)
            else:
                wpsLog.warning(f"task{task.id} failed due to ProcessFailed status, but there are already artefacts, "
                               f"setting artefacts to error mode")
                Artefact.objects.filter(task=task, parameter=output, role='1').update(format='error', data=err_msg,
                                                                                      updated_at=time_now)
        return 3

    # update process of workflow after every response
    calculate_percent_done(task.workflow)

    return 0


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
    wpsLog.debug(f"parsing output information for task{task.id}")
    out_id = output.find(ns_map["Identifier"]).text

    try:
        output_db = InputOutput.objects.get(
            process=task.process, identifier=out_id, role='1')
        artefact = Artefact.objects.get(
            task=task, parameter=output_db, role='1')
    except InputOutput.DoesNotExist:
        wpsLog.warning(f"output for task{task.id} not found, aborting")
        return
    except:
        time_now = datetime.now()
        wpsLog.debug(
            f"output artefact for task {task.id} not found, creating new artefact")
        artefact = Artefact.objects.create(task=task, parameter=output_db, role='1',
                                           created_at=time_now, updated_at=time_now)

    # everything is the same up to here for each output type
    data_elem = output.find(ns_map["Data"])
    reference = output.find(ns_map["Reference"])
    time_now = datetime.now()

    if data_elem is not None:
        try:
            # there should always be just one element!
            data_elem = data_elem.getchildren()[0]
        except:
            wpsLog.debug(f"data has no child for task{task.id}")
            # go back to next output
            return

        if data_elem.tag == ns_map["LiteralData"]:
            wpsLog.debug(
                f"literal data found in data for output{output_db.id} of task{task.id}")
            d_attribs = data_elem.attrib
            db_format = ""
            for attrib in d_attribs:
                if attrib == "dataType":
                    db_format += f"{attrib}={d_attribs[attrib].split(':')[-1]}"
                else:
                    db_format += f";{attrib}={d_attribs[attrib]}"
            db_format.strip(";")
            db_data = data_elem.text

            # if the string is less than 490 chars long write to db
            # otherwise write to file and write url to db
            if len(db_data) < 490:
                wpsLog.debug("writing data to db")
                artefact.format = db_format
                artefact.data = db_data
                artefact.updated_at = time_now
                artefact.save()

            else:
                wpsLog.debug("writing data to file")
                # TODO: rework if file path problem is solved!
                file_name = f"outputs/task{task.id}.xml"
                with open(file_name, 'w') as tmpfile:
                    tmpfile.write(db_data)
                artefact.format = db_format
                artefact.data = f"{BASE_DIR}/{file_name}"
                artefact.updated_at = time_now
                artefact.save()

        elif data_elem.tag == ns_map["BoundingBox"]:
            wpsLog.debug(
                f"boundingbox data found in data for output{output_db.id} of task{task.id}")
            lower_corner = data_elem.find(ns_map["LowerCorner"])
            upper_corner = data_elem.find(ns_map["UpperCorner"])
            d_attribs = data_elem.attrib
            db_format = ""
            for attrib in d_attribs:
                if attrib == "dataType":
                    db_format += f"{attrib}={d_attribs[attrib].split(':')[-1]}"
                else:
                    db_format += f";{attrib}={d_attribs[attrib]}"
            db_format.strip(";")
            db_data = f"LowerCorner={lower_corner.text};UpperCorner={upper_corner.text}"
            wpsLog.debug("writing data to db")
            artefact.format = db_format
            artefact.data = db_data
            artefact.updated_at = time_now
            artefact.save()

        elif data_elem.tag == ns_map["ComplexData"]:
            wpsLog.debug(
                f"complex data found in data for output{output_db.id} of task{task.id}")
            # TODO: test!
            d_attribs = data_elem.attrib
            db_format = ""
            for attrib in d_attribs:
                if attrib == "dataType":
                    db_format += f"{attrib}={d_attribs[attrib].split(':')[-1]}"
                else:
                    db_format += f";{attrib}={d_attribs[attrib]}"
            db_format.strip(";")
            db_data = data_elem.text
            artefact.format = db_format

            if "CDATA" in data_elem.text:
                wpsLog.debug(
                    f"cdata found in complex data for output{output_db.id} of task{task.id}!")
                db_format = "CDATA;" + db_format

                # if the string is less than 490 chars long write to db
                # otherwise write to file and write url to db
                db_data = data_elem.text
                if len(db_data) < 490:
                    artefact.data = db_data
                    artefact.updated_at = time_now
                    artefact.save()

                else:
                    wpsLog.debug("writing data to file")
                    file_name = f"outputs/task{task.id}.xml"
                    with open(file_name, 'w') as tmpfile:
                        tmpfile.write(db_data)
                    artefact.data = f"{BASE_DIR}/{file_name}"
                    artefact.updated_at = time_now
                    artefact.save()

            elif db_data is not None:
                # if the string is less than 490 chars long write to db
                # otherwise write to file and write url to db
                if len(db_data) < 490:
                    wpsLog.debug("writing data to db")
                    artefact.data = db_data
                    artefact.updated_at = time_now
                    artefact.save()

                else:
                    wpsLog.debug("writing data to file")
                    file_name = f"outputs/task{task.id}.xml"
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
                    wpsLog.debug("writing data to db")
                    artefact.data = db_data
                    artefact.updated_at = time_now
                    artefact.save()
                else:
                    wpsLog.debug("writing data to file")
                    file_name = f"outputs/task{task.id}.xml"
                    with open(file_name, 'w') as tmpfile:
                        tmpfile.write(db_data)
                    artefact.data = f"{BASE_DIR}/{file_name}"
                    artefact.updated_at = time_now
                    artefact.save()
            else:
                wpsLog.debug(
                    "no complex data found in complexdata tree element")
    elif reference is not None:
        # complexdata found, usually gets passed by url reference which won't be 500 chars long
        # TODO: test ?!
        d_attribs = data_elem.attrib
        db_format = ""
        for attrib in d_attribs:
            if attrib == "dataType":
                db_format += f"{attrib}={d_attribs[attrib].split(':')[-1]}"
            else:
                db_format += f";{attrib}={d_attribs[attrib]}"
        db_format.strip(";")
        wpsLog.debug("writing data to db")
        db_data = reference.text  # should be a url
        artefact.format = db_format
        artefact.data = db_data
        artefact.updated_at = time_now
        artefact.save()

    try:
        wpsLog.debug(
            f"trying to get edge from task{task.id}, output{output_db.id}")
        edges = Edge.objects.filter(from_task=task, output=output_db)
    except Edge.DoesNotExist:
        wpsLog.debug(f"edge does not exist")
        edges = []

    for edge in edges:
        if db_data is not None:
            try:
                to_artefact = Artefact.objects.get(
                    task=task, parameter=edge.input, role='1')
                to_artefact.format = db_format
                to_artefact.data = db_data
                to_artefact.updated_at = time_now
                to_artefact.save()
            except Artefact.DoesNotExist:
                wpsLog.debug("input artefact not found, creating new artefact")
                to_artefact = Artefact.objects.create(task=edge.to_task, parameter=edge.input, role='0', format=db_format,
                                                      data=db_data, created_at=time_now, updated_at=time_now)
                wpsLog.debug(f"artefact{to_artefact.id} has been created")


# TODO: tests
def calculate_percent_done(workflow):
    """
    calculates the percentage of finished tasks in the workflow of task
    @param task: task with recently changed status
    @type task: Task
    @return: percentage of finished tasks in the workflow of task
    @rtype: int
    """
    err = list(Task.objects.filter(workflow=workflow, status='5'))
    if len(err):
        wpsLog.warning(f"workflow{workflow.id} execution has failed due to failure of tasks"
                       f"{[task.id for task in err]}")
        percent_done = -1
        workflow.save()
        Task.objects.filter(workflow=workflow).update(status='5')
    else:
        finished = list(Task.objects.filter(workflow=workflow, status='4'))
        all_wf_tasks = list(Task.objects.filter(workflow=workflow))
        percent_done = int((len(finished) / len(all_wf_tasks)) * 100)
        wpsLog.debug(
            f"updating progress of workflow{workflow.id} to {percent_done}%")

    workflow.percent_done = percent_done
    workflow.save()


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
    wpsLog.debug("starting process update")
    for wps_server in wps_servers:
        print(wps_server.id)
        # TODO: repair hardcode
        describe_processes_url = wps_server.describe_url + \
            '?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0'

        try:
            temp_xml, headers = urllib.request.urlretrieve(
                describe_processes_url)

            tree = ET.parse(temp_xml)
        except:
            wpsLog.warning(f"something went wrong while requesting describe process url from "
                           f"{describe_processes_url} WPS{wps_server.id}")
        root = tree.getroot()
        process_elements = root.findall('ProcessDescription')
        wpsLog.debug(
            f"found {len(process_elements)} processes on WPS{wps_server.id}")
        for process_element in process_elements:
            process = utils_module.parse_process_info(
                process_element, xml_namespaces, wps_server)
            process_from_database = utils_module.search_process_in_database(
                process)
            if process_from_database is None:
                process.save()
                wpsLog.info(f"created new process: process{process.id}")
            else:
                process = utils_module.overwrite_process(
                    process_from_database, process)
            wpsLog.debug(
                f"found matching process in database: process{process.id}")

            # Save Inputs
            inputs_container_element = process_element.find('DataInputs')
            if inputs_container_element is not None:
                input_elements = inputs_container_element.findall('Input')

                for input_element in input_elements:
                    input = utils_module.parse_input_info(
                        input_element, xml_namespaces, process)
                    input_from_database = utils_module.search_input_output_in_database(
                        input)
                    if input_from_database is None:
                        input.save()
                        wpsLog.info(f"created new input: input{input.id}")
                    else:
                        input = utils_module.overwrite_input_output(
                            input_from_database, input)
                        wpsLog.debug(
                            f"found matching input in database: input{input.id}")

            # Save Outputs
            outputs_container_element = process_element.find('ProcessOutputs')
            if outputs_container_element is not None:
                output_elements = outputs_container_element.findall('Output')

                for output_element in output_elements:
                    output = utils_module.parse_output_info(
                        output_element, xml_namespaces, process)
                    output_from_database = utils_module.search_input_output_in_database(
                        output)
                    if output_from_database is None:
                        output.save()
                        wpsLog.info(f"created new output: output{output.id}")
                    else:
                        output = utils_module.overwrite_input_output(
                            output_from_database, output)
                        wpsLog.debug(
                            f"found matching output in database: output{output.id}")
