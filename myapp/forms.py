# forms.py
from django import forms
from .models import ExcelFile

class ExcelFileUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ['name', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError('Invalid file type. Only Excel files are supported.')
        return file
