from django.db import models
from datetime import date
from django.utils import timezone
from django.db.models import Max


class Student(models.Model):
    id = models.CharField(max_length=20, unique=True, blank=False, null=False, primary_key=True)
    name = models.CharField(max_length=100, default='Name')
    email = models.EmailField(unique=True, default='Email')
    phone_number = models.CharField(max_length=10, unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                                  default='Other')
    photo = models.ImageField(upload_to='profile_photos/',blank=True,null=True,default='profile_photos/img_5p.png')
    password = models.CharField(max_length=28, default='Password')
    is_teacher = models.BooleanField(default=False)
    is_librarian = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.id} - {self.name}"

class NoticeBoard(models.Model):
    notice_no = models.AutoField(primary_key=True)
    notice_subject = models.TextField()
    date = models.DateField(default=date.today)
    file = models.FileField(upload_to='notices_files/', blank=True, null=True)
    def __str__(self):
        return f"Notice {self.notice_no}"

class ClassTimeTable(models.Model):
    CLASS_CHOICES = [
        ('One', 'Class 1'),
        ('Two', 'Class 2'),
        ('Three', 'Class 3'),
        ('Four', 'Class 4'),
    ]
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    class_name = models.CharField(max_length=20, choices=CLASS_CHOICES)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    subject = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    teacher_name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=20, default="Not Assigned")
    def __str__(self):
        return f"{self.class_name} - {self.day} - {self.subject}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, choices=[('Present','Present'),('Absent','Absent')], default='Absent')
    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

class Homework(models.Model):
    teacher = models.ForeignKey('Student', on_delete=models.CASCADE, limit_choices_to={'is_teacher': True})
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='homework_files/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    def __str__(self):
        return f"{self.title} ({self.subject}) - {self.teacher.name}"

class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, limit_choices_to={'is_teacher': False})
    answer_text = models.TextField(blank=True, null=True)
    answer_file = models.FileField(upload_to='homework_submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    is_graded = models.BooleanField(default=False)
    grade = models.CharField(max_length=10, blank=True, null=True)
    def __str__(self):
        return f"{self.student.name} - {self.homework.title}"

class ExamSchedule (models.Model):
    CLASS_CHOICES = [
        ('One', 'Class 1'),
        ('Two', 'Class 2'),
        ('Three', 'Class 3'),
        ('Four', 'Class 4'),
    ]
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    class_name = models.CharField(max_length=20, choices=CLASS_CHOICES)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    subject = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=20, default="Not Assigned")
    def __str__(self):
        return f"{self.class_name} - {self.day} - {self.subject}"

class Result(models.Model):
    student = models.ForeignKey(Student,to_field='id',on_delete=models.CASCADE,related_name="results")
    teacher = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True,related_name="uploaded_results", limit_choices_to={'is_teacher': True})
    exam_name = models.CharField(max_length=100)
    total_marks = models.FloatField()
    obtained_marks = models.FloatField()
    percentage = models.FloatField(blank=True, null=True)
    grade = models.CharField(max_length=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('Pass', 'Pass'), ('Fail', 'Fail')], default='Fail')
    uploaded_at = models.DateTimeField(default=timezone.now)
    def save(self, *args, **kwargs):
        if self.total_marks > 0:
            self.percentage = (self.obtained_marks / self.total_marks) * 100
            if self.percentage >= 80:
                self.grade = 'A+'
                self.status = 'Pass'
            elif self.percentage >= 60:
                self.grade = 'B'
                self.status = 'Pass'
            elif self.percentage >= 40:
                self.grade = 'C'
                self.status = 'Pass'
            else:
                self.grade = 'F'
                self.status = 'Fail'
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.student.name} - {self.exam_name}"

class Subject(models.Model):
    TYPE_CHOICES = [
        ('theory', 'Theory'),
        ('practical', 'Practical'),
    ]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    teacher = models.CharField(max_length=100)
    subject_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='theory')
    class_field = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name} - {self.code} ({self.teacher}) [{self.subject_type}]"
    class Meta:
        ordering = ['class_field', 'name']

class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return self.bus_number

class Stoppage(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="stoppages")
    stoppage_name = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    class Meta:
        ordering = ["order"]
    def __str__(self):
        return f"{self.stoppage_name} ({self.bus.bus_number})"

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)
class Hostel(models.Model):
    name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    location = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        if not self.name:
            count = Hostel.objects.filter(gender=self.gender).count() + 1
            self.name = f"{self.gender} Hostel {100 + count}"
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=50)
    room_number = models.CharField(max_length=10, blank=True)
    room_cost = models.DecimalField(max_digits=10, decimal_places=2)
    def save(self, *args, **kwargs):
        if not self.room_number:
            last_room = Room.objects.filter(hostel=self.hostel).aggregate(Max('room_number'))['room_number__max']
            if last_room and last_room.isdigit():
                self.room_number = str(int(last_room) + 1)
            else:
                self.room_number = '1'
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.room_type} - {self.room_number}"

class Book(models.Model):
    CLASS_CHOICES = [
        ("Nursery", "Nursery"),
        ("Class 1", "Class 1"),
        ("Class 2", "Class 2"),
        ("Class 3", "Class 3"),
        ("Class 4", "Class 4"),
        ("Class 5", "Class 5"),
        ("Class 6", "Class 6"),
        ("Class 7", "Class 7"),
        ("Class 8", "Class 8"),
        ("Class 9", "Class 9"),
        ("Class 10", "Class 10"),
        ("Class 11", "Class 11"),
        ("Class 12", "Class 12"),
        ("Other ", "Other ")
    ]
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    subject = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    published_year = models.IntegerField()
    available_copies = models.IntegerField(default=1)
    book_class = models.CharField(max_length=20, choices=CLASS_CHOICES, default="Class 1")

    def __str__(self):
        return f"{self.title} ({self.book_class})"

class Activity(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="activities")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=date.today)
    def __str__(self):
        return f"{self.title} - {self.student.name}"

class Certificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="certificates")
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="certificates/")
    issue_date = models.DateField(default=date.today)
    def __str__(self):
        return f"{self.name} - {self.student.name}"

class Document(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.name} - {self.student.name}"

class Timeline(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    content = models.FileField(upload_to='timeline/')
    text = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.student.name} - {self.text[:30] if self.text else 'No Caption'}"

class DownloadFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="downloads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name

class Query(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.subject

class CalendarEvent(models.Model):
    CATEGORY_CHOICES = [
        ('Vacation', 'Vacation'),
        ('Activity', 'Activity'),
    ]
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"

class Gallery(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='gallery/')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
    def is_image(self):
        return self.file.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
    def is_video(self):
        return self.file.url.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))

class News(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="news_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} ({self.date})"

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='courses/')
    def __str__(self):
        return self.title


class Payment(models.Model):
    METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('phonepe', 'PhonePe'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.student.name} - {self.method} - {self.amount}"