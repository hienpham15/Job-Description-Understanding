import scrapy
import logging
import time
import os
import sys
from itertools import product

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']

    def __init__(self,
                 name=None,
                 starting_page=0,
                 language='fr',
                 job_title='Data Engineer',
                 region='Île-de-France',
                 **kwargs):
        super(IndeedSpider, self).__init__(name, **kwargs)
        
        # self.driver_path = r"./vendor/geckodriver"
        self.options = webdriver.FirefoxOptions()
        # self.options.binary_location = r"./vendor/firefox/firefox"
        self.options.add_argument("--headless")
# =============================================================================
#         self.page_driver = webdriver.Firefox(executable_path=self.driver_path,
#                                              desired_capabilities=self.options.to_capabilities(),
#                                              options=self.options)
# =============================================================================
        self.page_driver = webdriver.Firefox(desired_capabilities=self.options.to_capabilities())
        self.s_page = int(starting_page)
        self.start_urls = []
        if language == 'fr':
            self.start_urls.append(f"https://fr.indeed.com/emplois?q={job_title}&l={region}")
        elif language == 'en':
            self.start_urls.append(f"https://www.indeed.com/jobs?q={job_title}&l={region}")

    def start_requests(self):
        for url in self.start_urls:
            for i in range(self.s_page, self.s_page + 3):
                print("starting at page: ", i)
                url_page = url + '&start=' + str(i*10) + ".html"
                yield scrapy.Request(url_page,
                                     callback=self.parse)

    def parse_jd(self,
                 jd_link,
                 **posting):
# =============================================================================
#         driver_cb = webdriver.Firefox(executable_path=self.driver_path,
#                                       desired_capabilities=self.options.to_capabilities(),
#                                       options=self.options)
# =============================================================================
        driver_cb = webdriver.Firefox(desired_capabilities=self.options.to_capabilities())
        driver_cb.get(jd_link.url)
        # print("jd link:", jd_link.url)

        driver_cb.implicitly_wait(10)
        wait = WebDriverWait(driver_cb, 5)
        wait.until(EC.presence_of_element_located((By.ID, "jobDescriptionText")))

        job_description = driver_cb.find_element_by_id("jobDescriptionText")
        posting_duration = driver_cb.find_element_by_css_selector(".jobsearch-HiringInsights-entry--text")
        # print('Job Description: ', job_description.text)
        posting.update({"job description": job_description.text,
                        "posting duration": posting_duration.text})
        # print("posting_final:", posting)
        yield posting
        driver_cb.quit()

    def parse(self, page_link):
        # Use headless option and Firefox browser as the driver
# =============================================================================
#         driver = webdriver.Firefox(executable_path=self.driver_path,
#                                    desired_capabilities=self.options.to_capabilities(),
#                                    options=self.options)
# =============================================================================
        driver = webdriver.Firefox(desired_capabilities=self.options.to_capabilities())
        driver.get(page_link.url)

        driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tapItem")))

        current_page = driver.find_element_by_xpath('//b[@aria-current="true"]')
        print("Page: ", current_page.text)

        listings = driver.find_elements_by_class_name("tapItem")

        for item in listings:
            job_title = item.find_element_by_class_name("jobTitle")
            print("Job Title:", job_title.text)
            company = item.find_element_by_class_name("companyName")
            location = item.find_element_by_class_name("companyLocation")
            summary = item.find_element_by_class_name("job-snippet")

            jd_page = item.find_element_by_class_name("jcs-JobTitle")
            job_id = jd_page.get_attribute("data-jk")
            posting = {"url": page_link.url,
                       "page": current_page.text,
                       "job id": job_id,
                       "job_title": job_title.text,
                       "company": company.text,
                       "location": location.text,
                       "summary": summary.text}

            if jd_page is not None:
                jd_link = jd_page.get_attribute("href")
                yield scrapy.http.Request(jd_link,
                                          callback=self.parse_jd,
                                          cb_kwargs=posting)
        time.sleep(5)
        driver.quit()

"""
TODO:
    - Create a scheduler
    - Configure the scrap bot to avoid timeout/blocking:
        + Proxies
        + IP Rotation
        + User-agent
        + Make scraping slower, change patterrn
        + Captcha solving services
"""     
