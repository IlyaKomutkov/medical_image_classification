from django.db import models


class Lesion(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    lesion_Img = models.ImageField(upload_to='images/')
    disease = models.CharField(max_length=50, blank=True)
    lesion_Segmentation_Img = models.ImageField(upload_to='images/', blank=True)
