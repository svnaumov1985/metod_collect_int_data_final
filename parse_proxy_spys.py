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


class GetProxy():

    __log = None
    __driver_name = ""
    __driver = None

    def driver_name(self):

        return self.__driver_name

    def __initialize_spys(self):

        self.__driver.get("http://spys.one/europe-proxy/")

        select = Select(self.__driver.find_element_by_name('xpp'))
        select.select_by_visible_text("500")

    def __initialize_white_list(self):

        elems = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.NAME, "tldc")))
        elems = elems.find_elements(By.XPATH, './option')
        white_list = ['France', 'Germany', 'Netherlands', 'United Kingdom',
                      'Spain', 'Italy', 'Poland', 'Czech Republic', 'Sweden', 'Bulgaria',
                      'Hungary', 'Finland', 'Greece',
                      'Lebanon', 'Latvia', 'Lithuania', 'Switzerland', 'Portugal', 'Norway']

        country_values = []

        for egg in elems:
            text_el = str(egg.text)
            for spam in white_list:
                if spam in text_el:
                    country_values.append(text_el)

        return country_values

    def __set_country(self, country):

        for i in range(10):

            try:
                element = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.NAME, "tldc")))
                break
            except TimeoutException:
                self.__initialize_spys()
            except Exception as e:
                self.__driver.quit()
                raise NameError(f"Не удалось продолжить после {country}")

        select = Select(element)
        select.select_by_visible_text(country)

    def __get_proxy_table(self, country):

        xpath = '//tr[@class="spy1xx"] | //tr[@class="spy1x"]'

        def find_elemets():

            return self.__driver.find_elements(By.XPATH, xpath)

        def elem_counts():

            return len(find_elemets())

        # начинаем поиск с 500, потом делим пополам

        cur_elem = 500

        for i in range(11):

            sleep(1)

            try:
                if elem_counts() >= cur_elem:
                    break
            except TimeoutException:
                self.__initialize_spys()
                self.__set_country(self.__driver, country)
            except Exception as e:
                self.__driver.quit()
                raise NameError(f"Не удалось найти строки таблицы")

            cur_elem = cur_elem / 2

        return find_elemets()

    def __proxy(self):

        self.__log.write("__proxy: погнали " + str(datetime.now()) + "\r")

        opts = Options()
        opts.headless = True

        self.__driver = webdriver.Chrome(executable_path=self.__driver_name, options=opts)

        self.__initialize_spys()
        country_values = self.__initialize_white_list()

        testREstring = "^([0-9]{1,3}\.){3}[0-9]{1,3}\:[0-9]{2,5}$"
        testLanStr = "^[0-9]{1,3}\.[0-9]{1,5}$"
        testUptime = "^[0-9]{1,3}\%"

        result = []

        for egg in country_values:

            self.__log.write("__proxy: Начало обработки страны " + egg + "\r")

            self.__set_country(egg)

            self.__log.write("__proxy: " + 3 * ' ' + "__proxy: Страна установлена" + egg + 3 * " " + "\r")

            elems = self.__get_proxy_table(egg)

            for spam in elems:

                xpath = './td[position()=1]'
                cur_elems = spam.find_element(By.XPATH, xpath)

                text_proxy = cur_elems.text
                self.__log.write("__proxy: " + text_proxy + "\r")

                if re.match(testREstring, text_proxy):
                    self.__log.write("__proxy: текст предполагаемого прокси прошел проверку регуляркой: " + \
                                    text_proxy + "\r")
                else:
                    self.__log.write("__proxy: НЕ ПРОКСИ: " + \
                                    text_proxy + "\r")
                    continue

                ip = text_proxy

                try:
                    xpath = './td[position()=6]'
                    cur_elems = spam.find_element(By.XPATH, xpath)
                except Exception:
                    continue

                text_proxy = cur_elems.text

                if re.match(testLanStr, text_proxy):
                    self.__log.write("__proxy: текст lan прошелр проверку: " + \
                                    text_proxy + "\r")
                else:
                    self.__log.write("__proxy: текст lan НЕ прошелр проверку: " + \
                                    text_proxy + "\r")
                    continue

                try:
                    lantitude = float(text_proxy)
                except:
                    continue

                try:
                    xpath = './td[position()=8]'
                    cur_elems = spam.find_element(By.XPATH, xpath)
                except Exception:
                    continue

                text_proxy = str(cur_elems.text)

                if re.match(testUptime, text_proxy):
                    self.__log.write("__proxy: текст % : " + \
                                    text_proxy + "\r")
                else:
                    self.__log.write("__proxy: текст % НЕ прошелр проверку: " + \
                                    text_proxy + "\r")
                    continue

                try:
                    percent = float(text_proxy[:text_proxy.find('%')])
                except:
                    continue

                if lantitude > 1 or percent < 60:
                    continue

                result.append(ip)

        self.__driver.quit()

        return result


    def proxy(self):

        result = []

        try:

            result = self.__proxy()

            self.__log.write("proxy: " + str(datetime.now()) + "\r")
            self.__log.write("proxy: OK")
            self.__log.close()

        except Exception as e:

            self.__log.write("proxy: " + str(e) + "\r")
            self.__log.close()

        return result

    def __init__(self, driver_name):

        self.__driver_name = driver_name

        filename = "proxy_log.log"
        if os.path.exists(filename):
            os.remove(filename)

        self.__log = open(filename, "w")

    def __del__(self):

        try:
            self.__log.close()
        except Exception:
            pass


if __name__ == "__main__":

    cl = GetProxy(r"C:\Users\Sergey\Downloads\chromedriver_win32(1)\chromedriver.exe")
    print(cl.driver_name())
    list = cl.proxy()
    print(len(list))
    print(list)
