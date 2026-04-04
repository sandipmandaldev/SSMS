from django.contrib import admin
from .models import Student
from .models import NoticeBoard
from .models import ClassTimeTable
from .models import Attendance
from .models import Homework
from .models import HomeworkSubmission
from .models import ExamSchedule
from .models import Result
from .models import Subject
from .models import Bus
from .models import Stoppage
from .models import Hostel, Room
from .models import Book, Activity, Certificate,  Document, DownloadFile, Query, CalendarEvent, Gallery, News, Event, Payment, Course


admin.site.register(Student)
admin.site.register(NoticeBoard)
admin.site.register(ClassTimeTable)
admin.site.register(Attendance)
admin.site.register(Homework)
admin.site.register(HomeworkSubmission)
admin.site.register(ExamSchedule)
admin.site.register(Result)
admin.site.register(Subject)
admin.site.register(Bus)
admin.site.register(Stoppage)
class RoomInline(admin.TabularInline):
    model = Room
    extra = 1

class HostelAdmin(admin.ModelAdmin):
    inlines = [RoomInline]
    list_display = ('name', 'gender', 'location')

admin.site.register(Hostel, HostelAdmin)
admin.site.register(Book)
admin.site.register(Activity)
admin.site.register(Certificate)
admin.site.register(Document)
admin.site.register(DownloadFile)
admin.site.register(Query)
admin.site.register(CalendarEvent)
admin.site.register(Gallery)
admin.site.register(News)
admin.site.register(Event)
admin.site.register(Course)
admin.site.register(Payment)