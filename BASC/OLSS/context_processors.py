from .models import Student
from .models import News


def student(request):
    student_id = request.session.get('student_id')
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            return {'student': student}
        except Student.DoesNotExist:
            pass
    return {'student': None}

def latest_news_processor(request):
    latest_news = News.objects.order_by('-created_at')[:5]  # শেষ ৫টা নিউজ
    return {'latest_news': latest_news}
