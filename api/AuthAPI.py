import requests

class AuthAPI:
    """Класс предоставляет методы для отправки api-запросов на авторизацию"""

    def __init__(self, api_key, base_url="https://ru.yougile.com/api-v2"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {'Authorization': f'Bearer {self.api_key}'}

    def login(self, login, password):
        """Метод для авторизации пользователя"""
        url = f"{self.base_url}/auth/login"  # Предполагаем, что это конечная точка для логина
        data = {
            'login': login,
            'password': password
        }
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()  # Генерируем исключение для кода ошибки
            return response.json()  # Возвращаем данные пользователя или токен
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Пример: вывод ошибки
        except Exception as err:
            print(f"An error occurred: {err}")  # Пример: вывод ошибки

    def logout(self):
        """Метод для выхода пользователя из системы"""
        url = f"{self.base_url}/auth/logout"  # Предполагаем, что это конечная точка для логаута
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()  # Генерируем исключение для кода ошибки
            if response.status_code == 204:  # Успешный выход
                return True
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred during logout: {http_err}")  # Пример: вывод ошибки
        except Exception as err:
            print(f"An error occurred during logout: {err}")  # Пример: вывод ошибки

# Пример использования
if __name__ == "__main__":
    api_key = "ваш_api_ключ"
    auth_api = AuthAPI(api_key)

    try:
        user_data = auth_api.login("ваш_логин", "ваш_пароль")
        if user_data:
            print("Успешная авторизация:", user_data)  # Логика работы с авторизованным пользователем

            # Выход из системы
            if auth_api.logout():
                print("Успешный выход")
    except Exception as e:
        print("Ошибка:", e)