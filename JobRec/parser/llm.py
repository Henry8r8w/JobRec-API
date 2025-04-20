import os  
import openai  
from dotenv import load_dotenv
load_dotenv()
from django.conf import settings 
import PyPDF2
from jobs.models import JobPost 
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)  
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text
              

def parse_resume(file):
    text_content = extract_text_from_pdf(file)
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Extract only the following from the resume:
                1. Name
                2. Email
                3. Technical skills (programming languages, frameworks, tools)
                
                Return as JSON:
                {
                    "name": " ",
                    "email": " ",
                    "skills": {
                        "programming_languages": [],
                        "frameworks": [],
                        "tools": []
                    }
                }
                """
            },
            {
                "role": "user",
                "content": text_content
            }
        ],
        temperature=0.1 # logical
    )
        
    content = response.choices[0].message.content
    
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip() 
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    parsed_content = json.loads(content)
    return parsed_content


def review_resume(parsed_resume):
    prompt_resume = json.dumps(parsed_resume, indent=2)

    analysis_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional resume reviewer. Respond only in JSON.\n"
                    "Given a resume, return the following keys:\n\n"
                    "- score: integer (0–100)\n"
                    "- comment: a 1–2 sentence summary of the score\n"
                    "- skills: a list of objects {name, relevance (0–10), reason}\n"
                    "- improvements: a dictionary with 'high', 'medium', 'low' priorities, each a list of bullet points\n"
                    "- summary: final summary paragraph (1–3 sentences)\n\n"
                    "Only respond with a valid JSON object. Do not include Markdown or explanation."
                )
                
            },
            {
                "role": "user",
                "content": f"Resume data:\n{prompt_resume}",}
        ],
        temperature = 0.5
    )

    return analysis_response.choices[0].message.content

def load_jobs(parsed_resume):
     jobs = JobPost.objects.all()
     job_matches = []
     for job in jobs:
        skills = parsed_resume.get('skills', [])

        match_score = 50
        for skill in skills:
            if skill in job.description:
                match_score += 5
                job_matches.append({
            'company': job.company,
            'apply_link': job.apply_link,
            'match_score': match_score
            })
     return job_matches
             

           
        
    