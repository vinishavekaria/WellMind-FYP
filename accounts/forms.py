from django import forms
from .models import JournalEntry, ToDo
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['mood', 'entry']
        widgets = {
            'mood': forms.Select(choices=[('Happy', 'Happy'),('Inspired', 'Inspired'),('Grateful', 'Grateful'), ('Sad', 'Sad'), ('Angry', 'Angry'), ('Stressed', 'Stressed'), ('Neutral', 'Neutral'), ('Calm', 'Calm'), ('Reflective', 'Reflective'),]),  # Dropdown for mood
        }

class ToDoForm(forms.ModelForm):
    class Meta:
        model = ToDo
        fields = ['title', 'description', 'date_due', 'status']
        widgets = {
            'date_due': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=[('to_do', 'To Do'), ('done', 'Done')]),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = User
        fields = ("username", "email", "birthday", "password1", "password2")
    
    # Custom validation for the birthday field
    def clean_birthday(self):
        birthday = self.cleaned_data.get('birthday')
        if birthday:
            age = (date.today() - birthday).days // 365  # Calculate the age in years
            if age < 13:
                raise ValidationError("You must be at least 13 years old to sign up.")
        return birthday