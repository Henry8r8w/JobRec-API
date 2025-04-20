from django.urls import path
from .views import upload_resume, get_resume_analysis, get_job_matches, dashboard


urlpatterns = [
    path("", dashboard, name="dashboard"), # routes to home.html

    # GET
    path("resume/upload/", upload_resume,  name="upload_resume"),
    # POST
    path("resume/<uuid:resume_id>/analysis/", get_resume_analysis, name="get_resume_analysis"),
    # GET
    path("resume/<uuid:resume_id>/matches/",  get_job_matches,     name="get_job_matches"),

]