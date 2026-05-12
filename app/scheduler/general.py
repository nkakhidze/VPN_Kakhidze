from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from sqlalchemy.orm import Session
import requests
from app.db.database import engine
from app.services.subscription_service import check_needing_rescadular_for_user

from app.db.models import User

with Session(engine) as session:
    print(check_needing_rescadular_for_user(session, 1337))
    print(check_needing_rescadular_for_user(session, 228))
    print(check_needing_rescadular_for_user(session, 1001))
    print(check_needing_rescadular_for_user(session, 1515))

spisok_users_for_remind = [1337, 228, 1337]

# Функция, которую нужно запускать
def my_daily_job():
    with Session(engine) as session:
        users_stream = session.query(User).yield_per(100)

        for user in users_stream:
            try:
                # Делаем запрос к эндпоинту, используя данные юзера
                response = requests.get(f"http://127.0.0.1:8000/users/{user.telegram_id}")
                if check_needing_rescadular_for_user(session, user.telegram_id):
                    spisok_users_for_remind.append(user.telegram_id)
                    print(spisok_users_for_remind)


                if response.status_code == 200:
                    print(f"Обработан юзер {user.telegram_id}")

            except Exception as e:
                print(f"Ошибка при обработке {user.telegram_id}: {e}")


def reminder():
    for i in spisok_users_for_remind:
        

scheduler = BlockingScheduler()

# Запуск каждый день в 08:30:00 (время сервера)
# scheduler.add_job(my_daily_job, 'cron', hour=11, minute=53, second=10)
scheduler.add_job(my_daily_job, 'cron', second=10)
scheduler.add_job(my_daily_job, 'cron', second=20)
scheduler.add_job(my_daily_job, 'cron', second=30)
scheduler.add_job(my_daily_job, 'cron', second=40)
scheduler.add_job(my_daily_job, 'cron', second=50)
scheduler.add_job(my_daily_job, 'cron', second=0)

print("Планировщик запущен. Нажмите Ctrl+C для выхода.")
try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass

# функция должна
# 1) пройтись по всем пользователям, и собрать всех, кому нужно отправить напоминания сегодня
# 2) каждый час проходить по списку пользователей и если у пользователя 10 утра: отправить ему сообщение, что ему необходимо оплатить ВПН





