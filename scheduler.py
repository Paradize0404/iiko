from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import subprocess

scheduler = BlockingScheduler(timezone="Europe/Kaliningrad")

@scheduler.scheduled_job("cron", hour="9-17", minute=0)
def update_nomenclature():
    print(f"🔄 Запуск обновления номенклатуры: {datetime.now()}")
    subprocess.run(["python", "main.py"])

update_nomenclature()

scheduler.start()