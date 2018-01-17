import os
import random

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
    pass


def receiver():
    # Receiver main function
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


def getWPSProcesses():
    #
    #do for all entries in wps tabular
    #  get capabilities url
    #  exec capabilities url
    #  get response xml
    #  do for all process entries in xml
    #    parse
    #    create entry in processes tabular with data
    #     identifier, title, abstract
    pass


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