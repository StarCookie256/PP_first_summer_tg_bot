import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from web_admin import app
import threading
import time
import json
import os


# ---------- Запуск Flask-сервера в фоне для тестов ----------
def run_flask():
    app.run(debug=False, port=5000, use_reloader=False)


@pytest.fixture(scope="session", autouse=True)
def start_flask():
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    time.sleep(2)  # даём серверу время запуститься
    yield
    # очистка (необязательна, поток демонический)


@pytest.fixture
def driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # можно убрать, если хотите видеть браузер
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()


@pytest.fixture
def sample_data():
    """Создаёт тестовые данные в orders.json перед тестами и восстанавливает после."""
    test_orders = [
        {"id": 1, "company_name": "ООО Ромашка", "company_mail": "romashka@mail.ru",
         "order_price": 50000, "order_name": "CRM-система", "order_description": "Клиентская база и отчёты"},
        {"id": 2, "company_name": "ИП Иванов", "company_mail": "ivanov@bk.ru",
         "order_price": 30000, "order_name": "Интернет-магазин", "order_description": "Каталог товаров и корзина"}
    ]
    with open("orders.json", "w", encoding="utf-8") as f:
        json.dump(test_orders, f, ensure_ascii=False, indent=4)
    yield
    if os.path.exists("orders.json"):
        os.remove("orders.json")


# ---------- 5 UI-тестов ----------


def test_page_title(driver, sample_data):
    """Тест 1: проверка заголовка страницы"""
    driver.get("http://127.0.0.1:5000/")
    assert "Панель администратора" in driver.title


def test_order_display(driver, sample_data):
    """Тест 2: отображаются ли данные первой заявки"""
    driver.get("http://127.0.0.1:5000/")
    card = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "order-card"))
    )
    assert "ООО Ромашка" in card.text
    assert "romashka@mail.ru" in card.text
    assert "CRM-система" in card.text


def test_pagination_next(driver, sample_data):
    """Тест 3: работа кнопки 'Далее' (переход на вторую заявку)"""
    driver.get("http://127.0.0.1:5000/")
    next_btn = driver.find_element(By.LINK_TEXT, "Далее ➡️")
    next_btn.click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "order-card"))
    )
    page_text = driver.find_element(By.XPATH, "//span[contains(text(),'Страница')]").text
    assert "Страница 2 из 2" in page_text
    assert "ИП Иванов" in driver.page_source


def test_delete_order(driver, sample_data):
    """Тест 4: удаление заявки и проверка, что её больше нет"""
    driver.get("http://127.0.0.1:5000/")
    delete_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "delete-btn"))
    )
    delete_btn.click()
    # после удаления редирект на первую страницу
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "order-card"))
    )
    # ожидаем, что на первой странице теперь отображается вторая заявка (бывшая id=2 стала id=1)
    assert "ИП Иванов" in driver.page_source
    assert "ООО Ромашка" not in driver.page_source


def test_empty_state(driver, sample_data):
    """Тест 5: при отсутствии заявок показывается сообщение об отсутствии"""
    driver.get("http://127.0.0.1:5000/")

    # Удаляем первую заявку
    delete_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "delete-btn"))
    )
    delete_btn.click()
    # Ждём загрузки страницы с оставшейся заявкой
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "order-card"))
    )

    # Удаляем вторую заявку
    delete_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "delete-btn"))
    )
    delete_btn.click()

    # После удаления последней заявки появляется текст "Нет заявок"
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Нет заявок")
    )

    assert "Нет заявок" in driver.page_source
