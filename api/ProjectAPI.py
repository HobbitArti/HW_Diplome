import allure
import requests
from requests import Response

class ProjectApi:
    """Класс для работы с API проектов."""

    def __init__(self, base_url: str, api_key: str) -> None:
        self.__url = "https://ru.yougile.com/api-v2"
        self.__headers = {'Authorization': f'Bearer {api_key}'}

    @allure.step('[api]. Получение проектов компании')
    def get_projects(self) -> Response:
        """Получить список проектов компании."""
        response = requests.get(self.__url, headers=self.__headers)
        response.raise_for_status()  # Генерируем исключение для кода ошибки
        return response

    @allure.step('[api]. Получение информации по проекту с id {id}')
    def get_project_by_id(self, id: str) -> Response:
        """Получить информацию о проекте по его ID."""
        response = requests.get(f'{self.__url}/{id}', headers=self.__headers)
        response.raise_for_status()  # Генерируем исключение для кода ошибки
        return response

    @allure.step('[api]. Создание проекта с названием "{title}"')
    def create_project(self, title: str, api_key: str | None = None, users_dict: dict | None = None) -> Response:
        """Создать новый проект."""
        headers = self.__headers if api_key is None else {'Authorization': f'Bearer {api_key}'}
        body = {
            'title': title,
            'users': users_dict
        }
        response = requests.post(self.__url, headers=headers, json=body)
        response.raise_for_status()  # Генерируем исключение для кода ошибки
        return response

    @allure.step('[api]. Удаление проекта с id {id}')
    def delete_project(self, id: str) -> None:
        """Удалить проект по его ID."""
        response = requests.put(f'{self.__url}/{id}', headers=self.__headers, json={"deleted": True})
        response.raise_for_status()  # Генерируем исключение для кода ошибки

# Пример использования
if __name__ == "__main__":
    base_url = "https://example.com/api"  # Замените на ваш базовый URL
    api_key = "ваш_api_ключ"  # Замените на ваш API ключ
    project_api = ProjectApi(base_url, api_key)

    try:
        # Пример получения проектов
        projects = project_api.get_projects()
        print("Список проектов:", projects.json())

        # Пример создания проекта
        new_project = project_api.create_project("Новый проект", users_dict={"user1": "user@example.com"})
        print("Созданный проект:", new_project.json())

    except Exception as e:
        print("Ошибка:", e)