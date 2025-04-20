from django.shortcuts import render
from datetime import timedelta 
# Create your views here.
@api_view(['GET'])
def list_active_jobs(request):
    one_month_ago = timezone.now() - timedelta(days=30)
    recent_jobs = JobPost.objects.filter(created_at__gte=one_month_ago)
    jobs = [
        {
            "id": job.id,
            "company_name": job.company_name,
            "apply_link": job.apply_link,
            "description": job.description,
            "created_at": job.created_at
        }
        for job in recent_jobs
    ]

    return Response({'jobs': jobs})