from django.shortcuts import render
# DB and API key Imports
from .models import Resume
from jobs.models import JobPost
from django.conf import settings
from .forms import ResumeForm
from dotenv import load_dotenv
load_dotenv()
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# REST Syntax
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIRequestFactory

# Call on the llm.py
from .llm import parse_resume , review_resume, load_jobs
import json


@api_view(['POST'])
def upload_resume(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    # before closing, any update of resume instance would be overwrite; one thing to create the instance and later update instead of making direct entry is to obtain id, which you can use it when something fail
    resume = Resume.objects.create(
        name = request.data.get('name', 'Unknown'),
        email = request.data.get('email', 'Unknown'),
        file = file_obj
    )

    parsed_data = parse_resume(file_obj)
    

    skills_raw = parsed_data.get("skills", {})
    if isinstance(skills_raw, dict):
        flat_skills = [s for subs in skills_raw.values() for s in subs]
        parsed_data["skills"] = flat_skills
    else:
        flat_skills = skills_raw
    print("Skills being passed to LLMs:", parsed_data["skills"])
    resume.name = parsed_data.get("name", resume.name)
    resume.email = parsed_data.get("email", resume.email)
    resume.parsed_data = parsed_data
    resume.save()

    return Response({     # Django REST Framework; return the json-like http response
        "id": str(resume.id),
        "name": resume.name,
        "file": resume.file.url,
        "skills": resume.skills,
        "uploaded_at": resume.uploaded_at
    }, status=status.HTTP_201_CREATED)
    

@api_view(['GET'])
def get_resume_analysis(request, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        return Response({'error': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)
    
    parsed_data = resume.parsed_data
    skills = parsed_data.get("skills", {})
    if isinstance(skills, dict):
        flat_skills = [s for subs in skills.values() for s in subs]
        parsed_data["skills"] = flat_skills

    analysis = review_resume(parsed_data)  # ✅ use the modified one
    return Response({"analysis": analysis}, status=status.HTTP_200_OK)

# note: request can have http request attributes such as .header, .data, .FILES
@api_view(['GET'])
def get_job_matches(request, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        return Response({'error': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)
    
    parsed_data = resume.parsed_data
    skills = parsed_data.get("skills", {})
    if isinstance(skills, dict):
        flat_skills = [s for subs in skills.values() for s in subs]
        parsed_data["skills"] = flat_skills

    job_matches = load_jobs(parsed_data)  # ✅ use the flattened one

    # temporary fake matches override:
    job_matches = [
        {
            "title": "Backend Engineer",
            "description": "We want Python and Docker",
            "match_score": 92
        },
        {
            "title": "Data Scientist",
            "description": "Numpy, pandas, and sklearn required",
            "match_score": 88
        }
    ]

    return Response({'jobs': job_matches}, status=status.HTTP_200_OK)


def dashboard(request):
    form = ResumeForm(request.POST or None, request.FILES or None)
    analysis, matches , error_msg = None, None, None

    if request.method == "POST" and form.is_valid():
        api_response = upload_resume(request)
        if api_response.status_code != status.HTTP_201_CREATED:
            error_msg = api_response.data.get("error", "Upload failed")
        else:
            resume_id = api_response.data["id"]
            # fake GET request to not get bottleneck by POST; need to change during prod
            factory = APIRequestFactory()
            get_request = factory.get(f'/resume/{resume_id}/analysis/')
            analysis_resp = get_resume_analysis(get_request, resume_id)
            get_request = factory.get(f'/resume/{resume_id}/matches/')

            matches_resp = get_job_matches(get_request, resume_id)
            analysis_resp = get_resume_analysis(get_request, resume_id)
            analysis_raw = analysis_resp.data.get("analysis") or {}
            analysis = json.loads(analysis_raw) if isinstance(analysis_raw, str) else analysis_raw
            matches  = matches_resp.data.get("jobs") or []
            print("raw analysis response:", analysis_resp.data)
    
    print("Analysis:", analysis)
    print("Matches:", matches)
    

    return render(request, "dashboard.html", { # note: render takes html response and return an html file to utilize the response
        "form":      form,
        "error_msg": error_msg,
        "analysis":  analysis,
        "matches":   matches,
    })
