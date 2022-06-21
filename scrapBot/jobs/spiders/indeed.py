import scrapy
import logging
from bs4 import BeautifulSoup
from itertools import product
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

job_titles = ["Data Engineer", "Data Scientist", "Data Analyst", "Machine Learning Engineer"]
regions = ["Île-de-France"]
villes = ["Fontenay-aux-Roses"]
urls = []

for (job_title, region, ville) in product(job_titles, regions, villes):
    urls.append(f"https://fr.indeed.com/emplois?q={' '.join(job_title.split())}&l={region}&rbl={ville}.html")

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']
    start_urls = urls
# =============================================================================
# 
#     def parse_jd(self, response, **posting):
#         soup = BeautifulSoup(response.text, features="lxml")
#         jd = soup.find("div", {"id": "jobDescriptionText"}).get_text()
#         url = response.url
#         posting.update({"job_description": jd, "url": url}) 
#         yield posting
# 
#     def parse(self, response):
#         soup = BeautifulSoup(response.text, features="lxml")
# 
#         listings = soup.find_all("a", {"class": "tapItem"})
#         for listing in listings:
#             job_title = listing.find("h2", {"class": "jobTitle"}).get_text().strip()
#             #logging.log("Job Title:", job_title)
#             summary = listing.find("div", {"class": "job-snippet"}).get_text().strip()    # strip newlines
#             #logging.log("Job Summary:", summary)
#             company = listing.find("span", {"class": "companyName"}).get_text().strip()
#             location = listing.find("div", {"class": "companyLocation"}).get_text().strip()
# 
#             posting = {"job_title": job_title, "summary": summary, "company": company, "location": location}
#             jd_page = listing.get("href")
#             
#             print(posting)
#             if jd_page is not None:
#                 yield response.follow(jd_page, callback=self.parse_jd, cb_kwargs=posting)
# =============================================================================
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("headless")
        self.driver = webdriver.Firefox(desired_capabilities=options.to_capabilities())
        
    
    def parse_jd(self, jd_link):
        self.driver.get(jd_link)
        self.driver.implicitly_wait(10)
        
        wait = WebDriverWait(self.driver, 5)
        job_description = self.driver.find_element_by_id("jobDescriptionText")
        #print('JD: ', job_description.text)
        #self.driver.quit()
        return job_description.text
        
        
        
    def parse(self, response):
        # Use headless option and Firefox browser as the driver
# =============================================================================
#         options = webdriver.FirefoxOptions()
#         options.add_argument("headless")
#         driver = webdriver.Firefox(desired_capabilities=options.to_capabilities())
# =============================================================================
          
        self.driver.get("https://fr.indeed.com/jobs?q=Data%20Engineer&l=%C3%8Ele-de-France&rbl=Fontenay-aux-Roses.html&start=150&vjk=42ca2e270d024eee")
        
        self.driver.implicitly_wait(10)
        
        wait = WebDriverWait(self.driver, 5)
        
        job_titles = self.driver.find_elements_by_class_name("jobTitle")
        companies = self.driver.find_elements_by_class_name("companyName")
        #jd_links = self.driver.find_elements_by_class_name("jcs-JobTitle")
        # class="jcs-JobTitle" with attribute href => follow href to get detail job Description
        #descriptions = driver.find_elements_by_id("jobDescriptionText")
        
        listings = self.driver.find_elements_by_class_name("tapItem")
        
        for item in listings:
            job_title = item.find_element_by_class_name("jobTitle")
            company = item.find_element_by_class_name("companyName")
            location = item.find_element_by_class_name("companyLocation")
            summary = item.find_element_by_class_name("job-snippet")
            
            posting = {"job_title": job_title, "summary": summary, "company": company, "location": location}
        
        for i in range(len(job_titles)):
            
            yield {
                "Company" : companies[i].text,
                "Job Title" : job_titles[i].text,}
                #"Job Description" : self.parse_jd(jd_links[i].get_attribute('href'))}
            
        self.driver.quit()
        

# =============================================================================
#         next_page = soup.find("a", {"aria-label":  "Suivant"}).get("href")
#         if next_page is not None:
#             next_page = response.urljoin(next_page)
#             yield scrapy.Request(next_page, callback=self.parse)
# =============================================================================
