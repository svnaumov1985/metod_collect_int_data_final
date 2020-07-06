from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
from datetime import datetime
import re
import os
from parse_proxy_spys import GetProxy
from selenium.webdriver.common.proxy import Proxy, ProxyType

class GetOdds():

    __log = None
    __result = None
    __driver_name = ""
    __driver = None

    __q_proxy = None

    def driver_name(self):

        return self.__driver_name

    def __initialize_odds_portal(self):

        try:
            self.__driver.quit()
        except Exception:
            pass

        myProxy = self.__q_proxy[0]
        del(self.__q_proxy[0])
        self.__q_proxy.append(myProxy)

        print(myProxy)

        opts = Options()
        # opts.headless = True
        opts.add_argument('--proxy-server=' + myProxy)

        self.__driver = webdriver.Chrome(executable_path=self.__driver_name, options=opts)

        self.__driver.get("https://www.oddsportal.com/soccer/")

    def __ligue_data(self):

        elems = self.__driver.find_elements(By.XPATH, '//a[@foo="f"]')

        result = []
        for egg in elems:
            local_href = egg.get_attribute("href")
            self.__log.write("__ligue_data: лига " + str(local_href) + "\r")
            result.append(local_href)

        return result

    def __process_event_page(self, event_page, double):

        self.__driver.get(event_page)
        self.__log.write("  __process_ligue_page: открыто событие " + event_page + "\r")

        elems = self.__driver.find_elements(By.XPATH, '//div[@class="cms"]')

        err_text = "Unfortunately you are accessing this website from a region where the law prohibits us from offering you our full service."

        for elem in elems:
            if elem.text == err_text:
                self.__log.write("  __process_ligue_page: ошибка получения данных\r")
                return

        elem = self.__driver.find_element(By.ID, 'breadcrumb')
        head = elem.text

        elem = self.__driver.find_element(By.XPATH, '//div[@id="col-content"]/p')
        head = head + " » " + elem.text

        if double:
            head = head + " » x "

        self.__result.write(head + '\n')

        for i in range(10):

            try:
                xpath = '//table[@class="table-main detail-odds sortable"]/tbody/tr'
                elements = WebDriverWait(self.__driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
                break
            except TimeoutException:
                self.__initialize_odds_portal()
                self.__driver.get(event_page)
            except Exception as e:
                self.__driver.quit()
                raise NameError(f"Не удалось найти таблицу ставок на странице event {event_page}")

        for elem in elements:

            res = str(elem.text)
            res = res.replace('\n', ', ')
            self.__result.write(res + '\n')

        if double != True:

            self.__process_event_page(event_page + '/#double;2', True)


    def __process_ligue_page(self, ligue_page):

        self.__driver.get(ligue_page)
        self.__log.write("__odds_data: открыта " + str(ligue_page) + "\r")

        for i in range(10):

            try:
                elements = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.ID, "tournamentTable")))
                break
            except TimeoutException:
                self.__initialize_odds_portal()
                self.__driver.get(ligue_page)
            except Exception as e:
                self.__driver.quit()
                raise NameError(f"Не удалось найти таблицу матчей в лиге {ligue_page}")

        xpath = '//tr/td[@class="name table-participant"]/a[@href!="javascript:void(0);"]'
        elems = elements.find_elements(By.XPATH, xpath)

        self.__log.write("  __process_ligue_page: событий в лиге " + str(len(elems)) + "\r")

        href_list = []

        for egg in elems:

            local_href = egg.get_attribute("href")
            href_list.append(local_href)

        for egg in href_list:

            try:
                self.__process_event_page(egg, False)
            except Exception as e:
                self.__log.write("  __process_ligue_page: ошибка в событии " + str(e) + "\r")


    def odds_data(self):

        self.__log.write("__proxy: погнали " + str(datetime.now()) + "\r")

        self.__initialize_odds_portal()

        for i in range(10):

            try:
                element = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.ID, "sport_content_soccer")))
                break
            except TimeoutException:
                self.__initialize_odds_portal()
            except Exception as e:
                self.__driver.quit()
                raise NameError(f"Не удалось найти таблицу футбольных элементов")

        lig_data = self.__ligue_data()

        for egg in lig_data:

            self.__process_ligue_page(egg)


    def __init__(self, driver_name, proxy_list):

        self.__driver_name = driver_name

        filename = "odds_log.log"
        if os.path.exists(filename):
            os.remove(filename)

        self.__log = open(filename, "w")

        filename = "result.txt"
        if os.path.exists(filename):
            os.remove(filename)

        self.__result = open(filename, "w")

        self.__q_proxy = proxy_list


    def __del__(self):

        try:
            self.__result.close()
        except Exception:
            pass

        try:
            self.__log.close()
        except Exception:
            pass


if __name__ == "__main__":

    path_d = r"C:\Users\Sergey\Downloads\chromedriver_win32(1)\chromedriver.exe"

    print("start ", datetime.now())

    cl = GetProxy(path_d)
    proxy_list = cl.proxy()
    print("finish ", datetime.now())

    # proxy_list = [ '217.163.28.38:31443',
    #                 '140.82.37.12:31964',
    #                 '140.82.36.154:31321',
    #                 '45.77.54.13:8080',
    #                 '144.91.88.111:5836',
    #                 '148.251.157.89:9050',
    #                 '78.47.119.22:3129']


    print("start ", datetime.now())
    cl = GetOdds(path_d, proxy_list)
    cl.odds_data()
    print("finish ", datetime.now())
