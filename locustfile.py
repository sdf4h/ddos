from locust import HttpUser, task, between, events
import threading
import time
import random
from datetime import datetime

# Настройки для многопоточного тестирования
TARGET_URL = "https://yourwebsite.com"  # URL сайта для тестирования
NUM_THREADS = 50  # Количество потоков (пользователей)
REQUESTS_PER_THREAD = 100  # Количество запросов на каждый поток
REQUEST_DELAY = 1  # Задержка между запросами (в секундах)

# Статистика для многопоточного тестирования
total_requests = 0
successful_requests = 0
failed_requests = 0

# Функция для отправки запросов (многопоточная часть)
def send_requests():
    global total_requests, successful_requests, failed_requests
    for _ in range(REQUESTS_PER_THREAD):
        try:
            # Случайный выбор типа запроса
            if random.choice([True, False]):
                # GET-запрос на главную страницу
                response = requests.get(TARGET_URL)
            else:
                # POST-запрос (пример)
                headers = {"Content-Type": "application/json"}
                data = {"username": "test", "password": "test123"}
                response = requests.post(f"{TARGET_URL}/login", json=data, headers=headers)

            # Логирование результата
            if response.status_code == 200:
                successful_requests += 1
            else:
                failed_requests += 1
            total_requests += 1

            print(f"Request to {TARGET_URL} - Status: {response.status_code}")

        except Exception as e:
            print(f"Request failed: {e}")
            failed_requests += 1
            total_requests += 1

        # Задержка между запросами
        time.sleep(REQUEST_DELAY)

# Функция для запуска многопоточного теста
def run_load_test():
    global total_requests, successful_requests, failed_requests
    threads = []

    # Создание и запуск потоков
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=send_requests)
        threads.append(thread)
        thread.start()

    # Ожидание завершения всех потоков
    for thread in threads:
        thread.join()

    # Вывод итоговой статистики
    print("\n--- Multi-threaded Test Results ---")
    print(f"Total Requests: {total_requests}")
    print(f"Successful Requests: {successful_requests}")
    print(f"Failed Requests: {failed_requests}")
    print(f"Success Rate: {(successful_requests / total_requests) * 100:.2f}%")

# Класс пользователя для Locust
class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Время между запросами

    @task
    def load_homepage(self):
        self.client.get("/")

    @task(3)  # Вес задачи (выполняется в 3 раза чаще, чем load_homepage)
    def submit_form(self):
        headers = {"Content-Type": "application/json"}
        data = {"username": "test", "password": "test123"}
        self.client.post("/login", json=data, headers=headers)

    @task(2)
    def browse_website(self):
        self.client.get("/about")
        self.client.get("/contact")

# Событие для запуска многопоточного теста перед началом Locust
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    print("Running multi-threaded load test before starting Locust...")
    run_load_test()
    print("Multi-threaded test completed. Starting Locust...")
