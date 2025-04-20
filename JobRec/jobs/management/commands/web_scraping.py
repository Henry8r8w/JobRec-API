from jobs.models import JobPost
import requests
from bs4 import BeautifulSoup

def scrape_dummy_jobs():
    #TODO: implementation of the scraper
    JobPost.objects.create(
        company_name="FakeCompany",
        apply_link="https://fakecompany.com/apply",
        description="Qualified Python developer with Django experience"
    )
