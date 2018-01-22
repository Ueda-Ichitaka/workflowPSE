import os
import random
import xml.etree.ElementTree as ET
from base.models import WPSProvider, WPS, Task, InputOutput

#from django_cron import Schedule, CronJobBase


"""
Django crontab. Version, die bei mir sicher funktioniert hat
"""


def first_crontab_task():
    #os.mkdir('/home/paradigmen/C/' + str(random.randrange(1, 100)) + '/')
    #Testzeile
    pass


def scheduler():
    # Scheduler main function
    # check workflow list for execute flag
    # for all tasks in db do
    #    check status for execute status
    task_list = list(Task.objects.filter(status='0').values())
    for task in task_list:
        print(task["id"], task["title"], task["status"], sep=" ")
        task_id = task["id"]

        input_list = list(InputOutput.objects.filter(process=task["id"], role='0').values())
        for input in input_list:
            print(input)

    #    for all tasks to execute do
    #       traverse InputOutput table
    #           if InputOutput.process_id == Task.id
    #               select
    #       generate process xml
    #       send xml to wps server
    #
    #todo: max parallel tasks schedule policy
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


def test_capabilities_parsing(self):
    url_from_scc_vm = 'base/testfiles/getCapabilitiesFromPyWPS.xml'

    xml_namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'xlink': 'http://www.w3.org/1999/xlink',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    #Parse the xml file
    tree = ET.parse(url_from_scc_vm)
    root = tree.getroot()

    service_provider = parse_service_provider_info(root, xml_namespaces)
    service_provider.save()

    wps_server = parse_wps_server_info(root, xml_namespaces, service_provider)
    wps_server.save()



def parse_service_provider_info(root, namespaces):
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


def parse_wps_server_info(root, namespaces, provider):
    service_identification_element = root.find('ows:ServiceIdentification', namespaces)

    server_title = service_identification_element.find('ows:Title', namespaces).text
    server_abstract = service_identification_element.find('ows:Abstract', namespaces).text

    operations_metadata_element = root.find('ows:OperationsMetadata', namespaces)

    urls = operations_metadata_element.findall('ows:Operation/ows:DCP/ows:HTTP/ows:Get', namespaces)

    wps_server = WPS(service_provider=provider,
                     title=server_title,
                     abstract=server_abstract,
                     capabilities_url=urls[0],
                     describe_url=urls[1],
                     execute_url=urls[2])

    return wps_server







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