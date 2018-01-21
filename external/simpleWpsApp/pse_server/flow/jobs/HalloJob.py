from django_cron import CronJobBase, Schedule

class HalloJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'flow.hallo_job'    # a unique code

    def do(self):
        print('HALLO FROM CRONOON')