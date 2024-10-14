import allure
import random
from selenium.webdriver.remote.webdriver import WebDriver
from ui.MainPage import IndexPage
from ui.CompanuPage import TeamPage
from ui.ProjectPage import ProjectPage
from api.UserAPI import UserApi
from api.ProjectAPI import ProjectApi
from api.BoardAPI import BoardApi
from api.ColumnAPI import ColumnApi
from api.TaskAPI import TaskApi
from datatest.Data import DataProvider


@allure.epic('Тестирование интерфейса сервиса YouGile')
@allure.severity(allure.severity_level.BLOCKER)
@allure.suite('ui-тесты на авторизацию, управлению проектами и задачами')
class UITest:

    @allure.id('AR-1')
    @allure.story('Позитивные проверки авторизации')
    @allure.title('Авторизация ранее зарегистрированного пользователя')
    @allure.description('Выполнить авторизацию ранее зарегистрированного пользователя')
    @allure.feature('AUTHORIZE')
    def auth_test(self, browser: WebDriver, test_data: DataProvider):
        # Шаг 1: Открыть главную страницу
        index_page = IndexPage(browser)
        index_page.open()

        # Шаг 2: Перейти к странице входа
        index_page.click_sign_in()

        # Шаг 3: Заполнить форму авторизации
        team_page = TeamPage(browser)
        team_page.set_email(test_data.get('email'))
        team_page.set_password(test_data.get('password'))

        # Шаг 4: Выполнить вход
        team_page.login()

        # Шаг 5: Проверка результата авторизации
        with allure.step('Проверка:'):
            with allure.step('Email пользователя отображается в секции Сотрудники компании'):
                # Предполагается, что метод для получения отображаемого email реализован
                displayed_email = team_page.get_displayed_email()  # Метод для получения отображаемого email
                assert displayed_email == test_data.get(
                    'email'), f"Ожидаемый email: {test_data.get('email')}, но получен: {displayed_email}"

    def add_project_test(self, auth_browser: WebDriver, test_data: dict, project_api: ProjectApi,
                         delete_utility_project: dict):
        # Шаг 1: Открыть страницу команды
        team_page = TeamPage(auth_browser)
        team_page.open()
        team_page.click_add_project()

        # Шаг 2: Генерировать уникальный префикс id для задач в проекте
        with allure.step('Генерирование уникального префикса id для задач в проекте'):
            prefix_id = str(random.randint(0, 99999))

        # Шаг 3: Генерировать уникальное название проекта
        with allure.step('Генерирование уникального названия проекта'):
            project_title = test_data.get('project_title') + ' ' + prefix_id
            team_page.set_project_title(project_title)
            team_page.set_prefix_id_task(prefix_id)

        # Шаг 4: Получить цвет кнопки создания проекта
        ui_btn_bg_color = team_page.get_bg_action_color()

        # Шаг 5: Создать проект
        team_page.click_create_project(project_title)

        # Шаг 6: Получить информацию о созданном проекте
        ui_title = team_page.get_project_title()
        ui_prefix = team_page.get_prefix_id_task()

        # Шаг 7: Получить список проектов из API
        api_projects = project_api.get_projects().json()
        project_titles = []
        project_id = ''

        for proj in api_projects['content']:
            project_titles.append(proj['title'])
            if proj['title'] == project_title:
                project_id = proj['id']

        api_project_titles = ''.join(project_titles)
        delete_utility_project['project_id'] = project_id

        # Шаг 8: Проверки
        with allure.step('Проверка:'):
            with allure.step('Кнопка Создать проект перешла в состояние enable'):
                assert test_data.get(
                    'bg_active_color') == ui_btn_bg_color, "Цвет кнопки создания проекта не соответствует ожидаемому"

            with allure.step('В секции проекты отображается добавленный проект с введенным названием'):
                assert project_title == ui_title, f"Ожидаемое название проекта: {project_title}, полученное: {ui_title}"

            with allure.step('В секции проекты отображается добавленный проект с введенным префиксом id'):
                assert prefix_id == ui_prefix, f"Ожидаемый префикс id: {prefix_id}, полученный: {ui_prefix}"

            with allure.step('В запросе списка проектов содержится добавленный проект'):
                assert project_title in api_project_titles, f"Проект '{project_title}' не найден в списке проектов API"

    @allure.id('AR-5')
    @allure.story('Позитивные проверки по управлению проектами')
    @allure.title('Удаление проекта компании')
    @allure.description('Удалить проект компании через кнопку Удалить в контекстном меню проекта')
    @allure.feature('Кнопка Удалить в контекстном меню проекта')
    def delete_project_test(self, auth_browser: WebDriver, test_data: DataProvider, project_api: ProjectApi,
                            user_api: UserApi, generate_random_str: str):
        # Шаг 1: Добавление проекта администратору
        with allure.step('Добавление проекта администратору'):
            project_title = 'Проект ' + generate_random_str + ' ' + str(random.randint(0, 99999))
            admin_id = user_api.get_user_id(test_data.get('email'))
            user_dict = {admin_id: "admin"}
            project_id = project_api.create_project(project_title, users_dict=user_dict).json()['id']

        # Шаг 2: Открыть страницу команды и удалить проект
        team_page = TeamPage(auth_browser)
        team_page.open()
        team_page.click_three_dot(project_title)
        team_page.click_trash()
        team_page.click_delete(project_title)

        # Шаг 3: Получить информацию о проекте из API
        project_api_data = project_api.get_project_by_id(project_id).json()
        ui_project_card_titles = team_page.get_project_section_text()

        # Шаг 4: Проверки
        with allure.step('Проверка:'):
            with allure.step('Удаленный проект не отображается в секции Проекты'):
                assert project_title not in ui_project_card_titles, f"Проект '{project_title}' все еще отображается в секции Проекты"

            with allure.step('В ответе на api-запрос информации о проекте вернулось поле deleted: true'):
                assert project_api_data.get('deleted') is True, "Поле 'deleted' не равно True в ответе API"

    @allure.id('AR-6')
    @allure.story('Позитивные проверки по управлению задачами')
    @allure.title('Создание задачи в проекте')
    @allure.description('Создать задачу в проекте и проверить ее наличие')
    @allure.feature('Создание задач')
    def create_task_test(self, auth_browser: WebDriver, test_data: dict, user_api: UserApi, project_api: ProjectApi,
                         board_api: BoardApi, column_api: ColumnApi, task_api: TaskApi,
                         generate_random_str: str, delete_utility_project: dict,
                         delete_utility_board: dict, delete_utility_column: dict,
                         delete_utility_task: dict):

        # Шаг 1: Создание проекта
        with allure.step('Создание проекта'):
            project_title = 'Проект ' + generate_random_str + ' ' + str(random.randint(0, 99999))
            admin_id = user_api.get_user_id(test_data.get('email'))
            user_dict = {admin_id: "admin"}
            project_id = project_api.create_project(project_title, users_dict=user_dict).json()['id']
            delete_utility_project['project_id'] = project_id  # Сохраняем ID для удаления

        # Шаг 2: Создание доски
        with allure.step('Создание доски'):
            board_title = 'Доска ' + generate_random_str
            board_id = board_api.create_board(board_title, project_id).json()['id']
            delete_utility_board['board_id'] = board_id  # Сохраняем ID для удаления

        # Шаг 3: Создание колонки
        with allure.step('Создание колонки'):
            column_title = 'Колонка ' + generate_random_str
            column_id = column_api.create_column(column_title, board_id).json()['id']
            delete_utility_column['column_id'] = column_id  # Сохраняем ID для удаления

        # Шаг 4: Создание задачи
        with allure.step('Создание задачи'):
            task_title = 'Задача ' + generate_random_str
            task_description = 'Описание задачи ' + generate_random_str
            task_id = task_api.create_task(task_title, task_description, column_id).json()['id']
            delete_utility_task['task_id'] = task_id  # Сохраняем ID для удаления

        # Шаг 5: Проверка наличия созданной задачи
        with allure.step('Проверка наличия созданной задачи'):
            created_task = task_api.get_task_by_id(task_id).json()
            assert created_task[
                       'title'] == task_title, f"Ожидалось название задачи: {task_title}, получено: {created_task['title']}"
            assert created_task[
                       'description'] == task_description, f"Ожидалось описание задачи: {task_description}, получено: {created_task['description']}"

    @allure.id('AR-7')
    @allure.story('Позитивные проверки по управлению задачами')
    @allure.title('Завершение задачи в проекте')
    @allure.description('Завершить задачу в проекте и проверить ее статус')
    @allure.feature('Завершение задач')
    def complete_task_test(self, auth_browser: WebDriver, test_data: dict, user_api: UserApi, project_api: ProjectApi,
                           board_api: BoardApi, column_api: ColumnApi, task_api: TaskApi, generate_random_str: str,
                           delete_utility_project: dict, delete_utility_board: dict, delete_utility_column: dict,
                           delete_utility_task: dict):
        # Шаг 1: Создание проекта
        with allure.step('Создание проекта'):
            project_title = 'Проект ' + generate_random_str + ' ' + str(random.randint(0, 99999))
            admin_id = user_api.get_user_id(test_data.get('email'))
            user_dict = {admin_id: "admin"}
            project_id = project_api.create_project(project_title, users_dict=user_dict).json()['id']
            delete_utility_project['project_id'] = project_id  # Сохраняем ID для удаления

        # Шаг 2: Создание доски
        with allure.step('Создание доски'):
            board_title = 'Доска ' + generate_random_str
            board_id = board_api.create_board(board_title, project_id).json()['id']
            delete_utility_board['board_id'] = board_id  # Сохраняем ID для удаления

        # Шаг 3: Создание колонки
        with allure.step('Создание колонки'):
            column_title = 'Колонка ' + generate_random_str
            column_id = column_api.create_column(column_title, board_id).json()['id']
            delete_utility_column['column_id'] = column_id  # Сохраняем ID для удаления

        # Шаг 4: Создание задачи
        with allure.step('Создание задачи'):
            task_title = 'Задача ' + generate_random_str
            task_description = 'Описание задачи ' + generate_random_str
            task_id = task_api.create_task(task_title, task_description, column_id).json()['id']
            delete_utility_task['task_id'] = task_id  # Сохраняем ID для удаления

        # Шаг 5: Завершение задачи
        with allure.step('Завершение задачи'):
            task_api.complete_task(task_id)  # Предполагается, что метод завершения задачи реализован

        # Шаг 6: Проверка статуса задачи
        with allure.step('Проверка статуса завершенной задачи'):
            completed_task = task_api.get_task_by_id(task_id).json()
            assert completed_task[
                       'status'] == 'completed', f"Ожидался статус 'completed', получен: {completed_task['status']}"