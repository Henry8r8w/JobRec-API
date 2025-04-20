from django.db import models
import uuid
# Create your models here.
class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # ensure effective lookup; uuid4 is an automatic generated default id generator
    name = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    file = models.FileField(upload_to='uploaded-resumes/') # upload_to add to MEDIA_ROOT/
    skills = models.JSONField(default=dict)  
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_data = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Resume for {self.name}"
    
    class Meta:
        ordering = ['-uploaded_at']
