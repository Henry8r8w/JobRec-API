from django.db import models

# Create your models here.

class JobPost(models.Model):
    company = models.CharField(max_length=255)
    apply_link = models.URLField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.apply_link}"
