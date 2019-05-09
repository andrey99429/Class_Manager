from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler


class ClassmanagerConfig(AppConfig):
    name = 'ClassManager'

    def ready(self):
        from ClassManager.common import find_works
        print('ClassManager ready')

        scheduler = BackgroundScheduler()
        scheduler.add_job(find_works, 'interval', minutes=1)
        scheduler.start()
