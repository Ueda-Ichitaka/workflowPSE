import os, sys
import random
import xml.etree.ElementTree as ET
from base.models import WPSProvider, WPS, Task, InputOutput, Artefact, Process
from email import policy
from xml.dom import minidom

#from django_cron import Schedule, CronJobBase


"""
Django crontab. Version, die bei mir sicher funktioniert hat
"""



def scheduler():
    # Scheduler main function
    
    # redirect stout to file
    orig_stdout  = sys.stdout
    f = open('/home/ueda/workspace/PSE/code/server/outfile.txt', 'w')
    sys.stdout = f
        
    task_list = list(Task.objects.filter(status='0').values())
    for task in task_list:        
        
        print("")
    
        root = ET.Element('wps:Execute')
        root.set('service', 'WPS')
        root.set('version', '1.0.0')
 
        #task_id = task["id"]   # id of task
        #wf_id=task["workflow_id"]  # id of workflow of task
        #proc_id=task["process_id"]  # id of pywps process, evaluate to identifier

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
                        
            #input_identifier=input["identifier"]
            #input_title=input["title"]
            #input_datatype=input["datatype"]
            #input_data_format=input["format"]

            artefact_list = list(Artefact.objects.filter(task_id=task["id"], parameter=input["id"]).values())
            for artefact in artefact_list:
                
                data = ET.SubElement(inputData, 'wps:DataTypeComesHere')
                data.text = artefact["data"]
                
        print('/home/ueda/workspace/PSE/code/server/base/testfiles/task' + str(task["id"]) + '.xml')
        
        tree = ET.ElementTree(root)
        tree.write('/home/ueda/workspace/PSE/code/server/base/testfiles/task' + str(task["id"]) + '.xml')
                      
    sys.stdout = orig_stdout
    f.close()



def scheduler_execute():
    #sends task to execution
    #receives response url
    pass


def scheduler_check_execute():
    #execute policy
    pass


def generateExecuteXML():
    pass


def receiver():
    # Receiver main function
    # check output urls from servers
    # for workflow in executing list do
    #   for task in workflow do
    #      check response url
    #        check for changes to db 
    #        update db data
    pass


def utils():
    # Main fuction for combined utility functions
    pass


def xmlGenerator():
    #generates xml from input data
    pass


def xmlParser():
    #parses input xml
    #checks data for changes
    #writes changes to db
    pass


def readyCollector():
    #gets a list of all workflows ready to execute from db
    #returns list
    pass


def readyDataCollector():
    #gets all data for xml generation from ready workflow from ready list
    pass


def workflowSender():
    #sends generated xml to pywps server for execution
    pass


def listExistingFiles():
    #part of datenhaltung
    #generates a list of all uploaded files, their upload date, last edit, editor, etc
    pass


def deleteOldFiles():
    #part of datenhaltung
    #deletes files with last edit date > limit or other defined rule
    pass


def checkDB():
    #checks database for correct data/data corruption
    pass


def checkFiles():
    #checks uploaded files for corruption
    pass


def get_capabilities_parsing():
    #Works only with absolute path.
    #In future will work with url
<<<<<<< HEAD
    get_cap_url_from_scc_vm = '/home/denis/Projects/Python/Django/workflowPSE/code/server/base/testfiles/wpsGetCapabilities.xml'
    desc_proc_url_from_scc_vm = '/home/denis/Projects/Python/Django/workflowPSE/code/server/base/testfiles/wpsDescribeProcesses.xml'
=======
    url_from_scc_vm = '/home/ueda/workspace/PSE/code/server/base/testfiles/getCapabilitiesFromPyWPS.xml'
>>>>>>> 501ce2c75b1a8bb718d44606a1dcc861b69f0110

    xml_namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'xlink': 'http://www.w3.org/1999/xlink',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    #Parse the xml file
    tree = ET.parse(get_cap_url_from_scc_vm)
    root = tree.getroot()

    service_provider = parse_service_provider_info(root, xml_namespaces)
    service_provider.save()
    os.mkdir('/home/denis/Documents/prov' + str(random.randrange(1, 100)) + '/')

    wps_server = parse_wps_server_info(root, xml_namespaces, service_provider)
    wps_server.save()
    os.mkdir('/home/denis/Documents/serv' + str(random.randrange(1, 100)) + '/')

    describe_processes_parsing(wps_server)
    os.mkdir('/home/denis/Documents/proc' + str(random.randrange(1, 100)) + '/')


def parse_service_provider_info(root, namespaces):
    service_provider_element = root.find('ows:ServiceProvider', namespaces)
<<<<<<< HEAD
=======
    #os.mkdir('/home/denis/Documents/' + str(random.randrange(1, 100)) + '/')
>>>>>>> 501ce2c75b1a8bb718d44606a1dcc861b69f0110
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


def parse_wps_server_info(root, namespaces, provider):
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


def describe_processes_parsing(wps_server):
    desc_proc_url_from_scc_vm = '/home/denis/Projects/Python/Django/workflowPSE/code/server/base/testfiles/wpsDescribeProcesses.xml'

    xml_namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'xlink': 'http://www.w3.org/1999/xlink',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    tree = ET.parse(desc_proc_url_from_scc_vm)
    root = tree.getroot()

    process_elements = root.findall('ProcessDescription')
    for process_element in process_elements:
        process_identifier = process_element.find('ows:Identifier', xml_namespaces).text
        process_title = process_element.find('ows:Title', xml_namespaces).text
        process_abstract = process_element.find('ows:Abstract', xml_namespaces).text if process_element.find('ows:Abstract', xml_namespaces) is not None else 'Null'

        process = Process(wps=wps_server,
                          identifier=process_identifier,
                          title=process_title,
                          abstract=process_abstract)
        process.save()




"""
Django cron. Das geht bei mir immer noch nicht :(
Wenn ich richtig verstanden habe, dann muss man den Manage Befehl (also python3 manage.py runcrons) selbst in Cron eintragen.
"""

"""
class FirstCronTask(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'testCron.firstCronTask'

    def do(self):
        #os.mkdir('/home/paradigmen/C/' + str(random.randrange(1, 100)) + '/')
        #Testzeile
        pass
"""