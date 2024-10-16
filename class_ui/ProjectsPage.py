import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from configuration.ConfigProvider import ConfigProvider

class ProjectPage:
    """Класс предоставляет методы для выполнения UI-тестов на странице проектов"""
    
    __driver: WebDriver
    __timeout: int

    def __init__(self, driver: WebDriver) -> None:
        """
            Создание экземпляра класса ProjectPage
            
            :param driver: WebDriver: веб-драйвер браузера
            
            :return: None
        """
        
        self.__driver = driver
        self.__timeout = ConfigProvider().get_int('ui', 'timeout')
        
    @allure.step('[UI]. Получение списка названий задач для колонки {column_title}')           
    def get_task_titles(self, column_title: str) -> list[str]:
        """
            Получить список наименований задач для определенной колонки
            
            :param column_title: str: название колонки
            
            :return: list[str]: список названий задач
        """
        
        titles = []
        for column in self.__driver.find_elements(By.CSS_SELECTOR, 'div[data-test="board-columns"]'):
            if column_title in column.text:
                for task_cont in column.find_elements(By.CSS_SELECTOR, 'div[data-test="TwTaskContainer"].group'):
                    titles.append(task_cont.text)            
        return titles 
    
    @allure.step('[UI]. Ввести название задачи - {task_title}')  
    def add_task(self, task_title: str) -> None:
        """
            Заполнить поле Название задачи и нажать Enter
            
            :param task_title: str: название задачи
            
            :return: None
        """
        task_locator = 'textarea[data-test="board-task-input-name"]'
        new_task_locator = f'//span[normalize-space()="{task_title}"]'
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, task_locator)))
                
        self.__driver.find_element(By.CSS_SELECTOR, task_locator).send_keys(task_title)         
        self.__driver.find_element(By.CSS_SELECTOR, task_locator).send_keys(Keys.RETURN)
        
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, new_task_locator)))
        
    @allure.step('[UI]. Нажатие на вкладку Доски "{board_title}"')      
    def click_board(self, board_title: str) -> None:
        """
            Нажать на вкладку Доски
            
            :param board_title: str: название доски
            
            :return: None
        """
        
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'div[title="{board_title}"]')))
        self.__driver.find_element(By.CSS_SELECTOR, f'div[title="{board_title}"]').click() 
        
    @allure.step('[UI]. Нажатие на кнопку Добавить задачу в колонке "{column_title}"')    
    def click_add_task(self, column_title: str) -> None:
        """
            Нажать на кнопку Добавить задачу в заданной колонке
            
            :param column_title: str: название колонки
            
            :return: None
        """
        column_locator = 'div[data-test="board-columns"]'
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, column_locator)))
        for column in self.__driver.find_elements(By.CSS_SELECTOR, column_locator):
            if column.find_element(By.CSS_SELECTOR, 'div[data-test="board-columns"] span').text == column_title:
                column.find_element(By.CSS_SELECTOR, 'div[data-test="link-button-new"]').click()

    @allure.step('[UI]. Нажатие на иконку Три точки у задачи "{task_title}"') 
    def click_three_dot(self, column_title: str, task_title: str) -> None:
        """
            Нажать на кнопку на иконку Три точки
            :param column_title: str: название колонки
            :param task_title: str: название задачи
            
            :return: None
        """
        column_locator = 'div[data-test="board-columns"]'
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, column_locator)))
        for column in self.__driver.find_elements(By.CSS_SELECTOR, column_locator):
            if column_title in column.text:
                for task_cont in column.find_elements(By.CSS_SELECTOR, 'div[data-test="TwTaskContainer"].group'):
                    if task_title in task_cont.text:
                        task_cont.find_element(By.CSS_SELECTOR, 'div[data-test="board-task-menu"]').click()
    
    @allure.step('[UI]. Нажатие на кнопку Отметить выполненной')                     
    def click_mark_completed(self) -> None:
        """
            Нажать на кнопку Отметить выполненной
                        
            :return: None
        """
        
        menu_locator = 'div[class="tippy-content"][data-state="visible"]'
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, menu_locator)))                
        self.__driver.find_elements(By.CSS_SELECTOR, 'div[class="tippy-content"][data-state="visible"] .group')[2].click() 

    @allure.step('[UI]. Получение цвета текста и скриншота для выполненной задачи "{task_title}"') 
    def get_title_status_color(self, column_title: str, task_title: str) -> str:
        """
            Получить CSS-атрибут цвет текста у названия задачи. Сделать скриншот экрана.
            
            :param column_title: str: название колонки
            :param task_title: str: название задачи
            
            :return: str: CSS-атрибут цвет текста у названия задачи
        """
        
        column_locator = 'div[data-test="board-columns"]'
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, column_locator)))
        title_status_color = ''
        for column in self.__driver.find_elements(By.CSS_SELECTOR, column_locator):
            if column_title in column.text:
                for task_cont in column.find_elements(By.CSS_SELECTOR, 'div[data-test="TwTaskContainer"].group'):
                    if task_title in task_cont.text:
                        self.__driver.save_screenshot(f'./screenshots/done_task({task_title}).png') 
                        xpath_locator = f"//span[contains(text(),'{task_title}')]"
                        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.text-placeholder-new')))
                        title_status_color = self.__driver.find_element(By.XPATH, xpath_locator).value_of_css_property('color')
        return title_status_color
        