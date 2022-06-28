import scrapy
import logging
import time
from itertools import product

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

job_titles = ["Data Engineer",
              "Data Scientist",
              "Data Analyst",
              "Machine Learning Engineer"]
regions = ["Île-de-France"]
villes = ["Fontenay-aux-Roses"]
urls = []

for (job_title, region, ville) in product(job_titles, regions, villes):
    urls.append(f"https://fr.indeed.com/emplois?q={' '.join(job_title.split())}&l={region}&rbl={ville}.html")


class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']
    start_urls = urls

    def __init__(self):
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument("--headless")
        self.page_driver = webdriver.Firefox(desired_capabilities=self.options.to_capabilities())


    def parse_jd(self, jd_link, **posting):
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


    def parse(self, response):
        # Use headless option and Firefox browser as the driver
        driver = webdriver.Firefox(desired_capabilities=self.options.to_capabilities())

        # driver.get("https://fr.indeed.com/jobs?q=Data%20Engineer&l=%C3%8Ele-de-France&rbl=Fontenay-aux-Roses.html&start=150&vjk=42ca2e270d024eee")
        driver.get("https://fr.indeed.com/emplois?q=Data Engineer&l=Île-de-France&rbl=Fontenay-aux-Roses.html")

        driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tapItem")))


        listings = driver.find_elements_by_class_name("tapItem")

        for item in listings:
            job_title = item.find_element_by_class_name("jobTitle")
            print("Job Title:", job_title.text)
            company = item.find_element_by_class_name("companyName")
            location = item.find_element_by_class_name("companyLocation")
            summary = item.find_element_by_class_name("job-snippet")

            jd_page = item.find_element_by_class_name("jcs-JobTitle")
            job_id = jd_page.get_attribute("data-jk")
            posting = {"job id": job_id,
                       "job_title": job_title.text,
                       "company": company.text,
                       "location": location.text,
                       "summary": summary.text}

            if jd_page is not None:
                jd_link = jd_page.get_attribute("href")
                yield response.follow(jd_link,
                                      callback=self.parse_jd,
                                      cb_kwargs=posting)

        time.sleep(5)

        xp_next = driver.find_element_by_xpath("//a[@aria-label='Suivant']")
        if xp_next is not None:
            current_page = driver.find_element_by_xpath('//b[@aria-current="true"]')
            print("Page: ", current_page.text)
            next_page_href = xp_next.get_attribute("href")
            print("Next page links:", next_page_href)
            next_page_url = response.urljoin(next_page_href)
            yield scrapy.http.Request(url=next_page_url, callback=self.parse)

        driver.quit()
