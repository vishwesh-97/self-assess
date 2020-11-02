from django.db import models

# Create your models here.


class BaseModel(models.Model):
    """
    Abstract base class for basic db fields
    """
    is_active = models.BooleanField(default=True)
    created_by = models.IntegerField(blank=True, null=True)
    updated_by = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        abstract = True
