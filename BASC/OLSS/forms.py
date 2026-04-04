from django import forms
from .models import Student
from .models import NoticeBoard
from .models import Result
from .models import Book
from .models import Document, Timeline
from .models import DownloadFile
from .models import Query



class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'phone_number', 'gender', 'dob', 'photo','password']
        labels = {
            'name': 'name',
            'email': 'email',
            'mobile_number': 'mobile_number',
            'gender': 'gender',
            'dob': 'dob',
            'photo': 'photo',
            'password': 'password',
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

class LoginForm(forms.Form):
    identifier = forms.CharField(   # email এর পরিবর্তে identifier
        label="Email or Registration ID",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Email or Registration ID'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Password'
        })
    )

class PasswordResetForm(forms.Form):
    email = forms.EmailField()
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)))

class NoticeBoardForm(forms.ModelForm):
    class Meta:
        model = NoticeBoard
        fields = ['notice_no', 'notice_subject', 'date', 'file']
        labels = {
            'notice_no': 'notice_no',
            'notice_subject': 'notice_subject',
            'data': 'data',
            'file': 'file',
        }

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'exam_name', 'total_marks', 'obtained_marks']
    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(
            is_teacher=False,
            is_librarian=False
        )
        self.fields['student'].label_from_instance = lambda obj: obj.id

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['phone_number', 'password']
        fields = ['name', 'email', 'dob', 'phone_number', 'gender', 'photo', 'password']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Name'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class TimelineForm(forms.ModelForm):
    class Meta:
        model = Timeline
        fields = ['content', 'text']

class DownloadFileForm(forms.ModelForm):
    class Meta:
        model = DownloadFile
        fields = ["name", "file"]


class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['name', 'email', 'subject', 'description']
        labels = {
            'name': 'Name',
            'email': 'Email',
            'subject': 'Subject',
            'description': 'Message',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your message'}),
        }
