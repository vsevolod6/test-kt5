import time
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://demowebshop.tricentis.com/"


def generate_unique_email():
    """Генерирует уникальный email для теста регистрации."""
    timestamp = int(time.time())
    return f"student_test_{timestamp}@mail.com"


def test_user_registration(driver):
    """
    Позитивный тест:
    Проверка успешной регистрации нового пользователя.
    """
    driver.get(BASE_URL)

    # Переход на страницу регистрации
    driver.find_element(By.LINK_TEXT, "Register").click()

    # Заполнение формы
    driver.find_element(By.ID, "gender-male").click()
    driver.find_element(By.ID, "FirstName").send_keys("Ivan")
    driver.find_element(By.ID, "LastName").send_keys("Petrov")

    email = generate_unique_email()
    driver.find_element(By.ID, "Email").send_keys(email)
    driver.find_element(By.ID, "Password").send_keys("Test12345!")
    driver.find_element(By.ID, "ConfirmPassword").send_keys("Test12345!")

    driver.find_element(By.ID, "register-button").click()

    # Проверка успешной регистрации
    result = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "result"))
    )
    assert "Your registration completed" in result.text


def test_login_negative_wrong_password(driver):
    """
    Негативный тест:
    Проверка, что вход с неправильным паролем невозможен.
    Для этого используется заведомо несуществующая/невалидная пара логин-пароль.
    """
    driver.get(BASE_URL)
    driver.find_element(By.LINK_TEXT, "Log in").click()

    driver.find_element(By.ID, "Email").send_keys("wrong_user_123@mail.com")
    driver.find_element(By.ID, "Password").send_keys("WrongPassword123!")
    driver.find_element(By.CSS_SELECTOR, "input.login-button").click()

    error_block = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".validation-summary-errors"))
    )

    assert "Login was unsuccessful" in error_block.text


def test_search_product(driver):
    """
    Позитивный тест:
    Проверка поиска товара по слову 'book'.
    """
    driver.get(BASE_URL)

    search_input = driver.find_element(By.ID, "small-searchterms")
    search_input.send_keys("book")
    search_input.send_keys(Keys.ENTER)

    page_title = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".page-title h1"))
    )

    assert "Search" in page_title.text

    products = driver.find_elements(By.CSS_SELECTOR, ".product-item")
    assert len(products) > 0, "Товары по запросу 'book' не найдены"


def test_add_product_to_cart(driver):
    """
    Позитивный тест:
    Проверка добавления товара в корзину.

    Используем товар '14.1-inch Laptop', который есть среди featured products на главной.
    """
    driver.get(BASE_URL)

    # Открываем страницу товара
    driver.find_element(By.PARTIAL_LINK_TEXT, "14.1-inch Laptop").click()

    # Добавляем в корзину
    add_to_cart_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "add-to-cart-button-31"))
    )
    add_to_cart_btn.click()

    # Проверяем всплывающее уведомление
    notification = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "bar-notification"))
    )
    assert "The product has been added to your shopping cart" in notification.text


def test_remove_product_from_cart(driver):
    """
    Позитивный тест:
    Проверка удаления товара из корзины.

    Сначала добавляем товар, затем удаляем его из корзины.
    """
    driver.get(BASE_URL)

    # Добавляем товар
    driver.find_element(By.PARTIAL_LINK_TEXT, "14.1-inch Laptop").click()
    add_to_cart_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "add-to-cart-button-31"))
    )
    add_to_cart_btn.click()

    # Переход в корзину
    cart_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Shopping cart"))
    )
    cart_link.click()

    # Удаление товара
    remove_checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "removefromcart"))
    )
    remove_checkbox.click()

    update_cart_btn = driver.find_element(By.NAME, "updatecart")
    update_cart_btn.click()

    # Проверка пустой корзины
    empty_cart_msg = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".order-summary-content"))
    )
    assert "Your Shopping Cart is empty!" in empty_cart_msg.text


def test_search_nonexistent_product(driver):
    """
    Негативный тест:
    Поиск несуществующего товара.
    """
    driver.get(BASE_URL)

    search_input = driver.find_element(By.ID, "small-searchterms")
    search_input.send_keys("asdfghjkl12345")
    search_input.send_keys(Keys.ENTER)

    no_result_text = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".result"))
    )

    assert "No products were found" in no_result_text.text
