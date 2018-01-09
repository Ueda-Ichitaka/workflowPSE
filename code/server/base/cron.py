import os
import random

from django_cron import Schedule, CronJobBase


"""
Django crontab. Version, die bei mir sicher funktioniert hat
"""


def first_crontab_task():
    os.mkdir('/home/paradigmen/C/' + str(random.randrange(1, 100)) + '/')


"""
Django cron. Das geht bei mir immer noch nicht :(
"""


class FirstCronTask(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'testCron.firstCronTask'

    def do(self):
        os.mkdir('/home/paradigmen/C/' + str(random.randrange(1, 100)) + '/')
        