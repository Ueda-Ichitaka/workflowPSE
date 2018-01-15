from django_cron import CronJobBase, Schedule
import os
import random


class firstCronTask(CronJobBase):
    RUN_EVERY_MINS = 1/12

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'testCron.firstCronTask'

    def do(self):
        os.mkdir('/home/paradigmen/C/' + str(random.randrange(1, 100)) + '/')