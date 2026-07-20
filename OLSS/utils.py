from django.shortcuts import redirect
from functools import wraps
from .models import Student

def student_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        student_id = request.session.get('student_id')
        if not student_id:
            return redirect('login')
        try:
            Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            request.session.flush()
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper