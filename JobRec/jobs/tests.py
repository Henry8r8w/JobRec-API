from django.test import TestCase
from .models import JobPost
from dotenv import load_dotenv
load_dotenv()
from faker import Faker
# Create your tests here.
from django.conf import settings
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_job_description(job_title="Software Engineer"):
    prompt = f"""
    Write a job description for a {job_title} at a tech company. Include a short intro, then 5 realistic qualifications (skills or experience).
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content


class JobPostModelTest(TestCase):
    def setUp(self):
        fake = Faker()
        for _ in range(15):  # Create 15 fake job posts
            JobPost.objects.create(
                company_name=fake.company(),
                apply_link=fake.url(),
                description=generate_job_description("Backend Developer")
            )

    def test_job_post_created(self):
        count = JobPost.objects.count()
        print("Count:", count)
        self.assertEqual(count, 15)
    
   