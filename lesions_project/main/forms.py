from django import forms
from .models import Lesion


class LesionForm(forms.ModelForm):
    class Meta:
        model = Lesion
        fields = ['name', 'lesion_Img']
