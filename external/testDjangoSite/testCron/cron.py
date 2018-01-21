from django_crontab import crontab
from pywps import Process
import os
import random
import time


def firstCrontabTask():
    for i in range(1, 12):
        os.mkdir('/home/paradigmen/C/' + str(random.randrange(1, 100)) + '/')
        time.sleep(5)
    pass