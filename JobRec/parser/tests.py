from pathlib import Path
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from jobs.models import JobPost
from faker import Faker
import openai
from django.conf import settings
openai.api_key = settings.openai_api_key


class SeedDataMixin:
    """Create 15 JobPost rows once for all tests in classes"""
    @classmethod
    def setUpTestData(cls):
        fake = Faker()
        for _ in range(15):
            JobPost.objects.create(
                company =fake.company(),
                apply_link=fake.url(),
                description=cls.generate_job_description("Backend Developer Intern") 
            )
    @staticmethod
    def generate_job_description(job_title="Software Engineer"):
        prompt = f"""Write a job description for a {job_title} at a tech company. Include a short intro, then 5 realistic qualifications (skills or experience)."""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content


class ParserFlowTests(SeedDataMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()               # keeps the 15 JobPosts
        cls.resume_path = Path(settings.BASE_DIR) /"test_files" / "software-engineer-resume-example.pdf"
    
        if not cls.resume_path.exists():
            raise FileNotFoundError(f"Put your resume at {cls.resume_path}")

    def test_upload_resume(self):
        with self.resume_path.open("rb") as f:
            resp = self.client.post(
                reverse("upload_resume"),
                {"file": f},
                format="multipart"
            )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # store id for later assertions in the same test run
        self.resume_id = resp.data["id"]

    def test_get_analysis(self):
        resume_id = self._upload_and_get_id()
        resp = self.client.get(reverse("get_resume_analysis", args=[resume_id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("analysis", resp.data)

    def test_get_jobs(self):
        resume_id = self._upload_and_get_id()
        resp = self.client.get(reverse("get_job_matches", args=[resume_id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("jobs", resp.data)
        self.assertGreaterEqual(len(resp.data["jobs"]), 1)

    def _upload_and_get_id(self):
        with self.resume_path.open("rb") as f:
            resp = self.client.post(
                reverse("upload_resume"), {"file": f}, format="multipart"
            )
        return resp.data["id"]
