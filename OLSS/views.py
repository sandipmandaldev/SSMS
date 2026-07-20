from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, PasswordResetForm, ResultForm, EditProfileForm, BookForm, DocumentForm, TimelineForm, QueryForm
from .models import Student, NoticeBoard, Attendance, ExamSchedule, Homework, HomeworkSubmission, ClassTimeTable, Result, Subject, Bus, Book, Activity, Certificate, Document, Timeline, Query, Gallery, News, Event, Course
from django.contrib import messages
import random
from django.core.mail import send_mail
from datetime import date
from .utils import student_login_required
from .models import Hostel,DownloadFile
from django.http import JsonResponse, FileResponse, HttpResponseForbidden
from django.utils.timezone import now
from django.utils.encoding import smart_str
from .models import CalendarEvent
from django.utils import timezone
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO


def home(request):
    if request.session.get('student_id'):
        return redirect('home1')
    return render(request, 'home.html')

def online_course(request):
    courses = Course.objects.all()
    return render(request, 'online_course.html', {'courses': courses})

def events(request):
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(date__gte=today).order_by('date')
    past_events = Event.objects.filter(date__lt=today).order_by('-date')
    return render(request, 'events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    })
def gallery(request):
    galleries = Gallery.objects.all().order_by('-created_at')
    return render(request, 'gallery.html', {'galleries': galleries})
def annual_calendar(request):
    vacations = CalendarEvent.objects.filter(category="Vacation").order_by("start_date")
    activities = CalendarEvent.objects.filter(category="Activity").order_by("start_date")
    return render(request, "annual_calendar.html", {
        "vacations": vacations,
        "activities": activities,
    })
def about_us(request):
    return render(request, 'about_us.html')
def facilities(request):
    return render(request, 'facilities.html')
def annual_sports(request):
    return render(request, 'annual_sports.html')
def course(request):
    return render(request, 'course.html')
def school_uniform(request):
    return render(request, 'school_uniform.html')
def principal_message(request):
    return render(request, 'principal_message.html')
def school_management(request):
    return render(request, 'school_management.html')
def know_us(request):
    return render(request, 'know_us.html')
def approach(request):
    return render(request, 'approach.html')
def pre_primary(request):
    return render(request, 'pre_primary.html')
def h_teacher(request):
    return render(request, 'h_teacher.html')
def houses(request):
    return render(request, 'houses.html')
def student_council(request):
    return render(request, 'student_council.html')
def career_counselling(request):
    return render(request, 'career_counselling.html')

def news(request):
    news_items = News.objects.all()
    return render(request, 'news.html', {'news_items': news_items})
def contact(request):
    if request.method == "POST":
        form = QueryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Your query has been submitted successfully!")
            return redirect("contact")
    else:
        form = QueryForm()
    return render(request, "contact.html", {"form": form})

def generate_registration_id():
    year = now().year
    random_number = random.randint(1000, 9999)
    return f"REG{year}{random_number}"
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        dob = request.POST.get('dob', '').strip()
        gender = request.POST.get('gender', '').strip()
        password = request.POST.get('password', '').strip()
        photo = request.FILES.get('photo')
        if not all([name, email, phone_number, dob, gender, password]):
            messages.error(request, 'Please fill all the required fields.')
            return render(request, 'register.html')
        if Student.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered!')
            return render(request, 'register.html')
        if Student.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'This phone number is already registered!')
            return render(request, 'register.html')
        reg_id = generate_registration_id()
        while Student.objects.filter(id=reg_id).exists():
            reg_id = generate_registration_id()
        student_data = {
            'name': name,
            'email': email,
            'phone_number': phone_number,
            'gender': gender,
            'dob': dob,
            'password': password,
            'id': reg_id
        }
        if photo:
            student_data['photo'] = photo
        student = Student.objects.create(**student_data)
        messages.success(
            request,
            f'Registration successful! Your Registration ID is {student.id}. You can now log in.'
        )
        return redirect('register')
    return render(request, 'register.html')

def student_login(request):
    if request.session.get('student_id'):
        return redirect('home1')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            student = Student.objects.filter(id=identifier, password=password).first()
            if not student:
                student = Student.objects.filter(email=identifier, password=password).first()
            if student:
                request.session['student_id'] = student.id
                return redirect('home1')
            else:
                return render(request, 'login.html', {
                    'form': form,
                    'error': 'Invalid Email/Registration ID or Password!'
                })
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
def logout(request):
    try:
        del request.session['student_id']
    except KeyError:
        pass
    return redirect('home')
@student_login_required
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            dob = form.cleaned_data['dob']
            try:
                student = Student.objects.get(email=email, dob=dob)
                temp_password = str(random.randint(100000, 999999))
                student.password = temp_password
                student.save()
                send_mail(
                    'Temporary Password',
                    f'Your temporary password is: {temp_password}. Please log in and change your password.',
                    'your_email@example.com',
                    [email],
                    fail_silently=False,
                )
                return render(request, 'password_reset.html',
                              {'form': form, 'success':'A temporary password has been sent to your email.'})
            except Student.DoesNotExist:
                return render(request, 'password_reset.html',
                              {'form': form, 'error': 'Invalid email or date of birth.'})
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})

@student_login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        student_id = request.session.get('student_id')
        if student_id:
            student = Student.objects.get(id=student_id)
            if student.password != old_password:
                messages.error(request, 'Old password does not match.')
                return render(request, 'change_password.html')
            if new_password != confirm_password:
                messages.error(request, 'New password and confirm password do not match.')
                return render(request, 'change_password.html')
            student.password = new_password
            student.save()
            messages.success(request, 'Password changed successfully. Please log in again.')
            return redirect('login')
        else:
            messages.error(request, 'User not logged in.')
            return redirect('login')
    return render(request, 'change_password.html')

@student_login_required
def base(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect('login')
    return render(request, 'base.html', {'student': student})

@student_login_required
def home1(request):
    student_id = request.session.get("student_id")
    student = Student.objects.get(id=student_id)
    this_month = date.today().month
    total_days = Attendance.objects.filter(student=student, date__month=this_month).count()
    present_days = Attendance.objects.filter(student=student, date__month=this_month, status='Present').count()
    attendance_percent = int((present_days / total_days) * 100) if total_days > 0 else 0
    incomplete_homework = Homework.objects.filter(deadline__gte=date.today()).count()
    pending_tasks = Homework.objects.filter(deadline__date=date.today()).count()
    notices = NoticeBoard.objects.all().order_by('-date')
    context = {
        "student_name": student.name,
        "attendance_percent": attendance_percent,
        "incomplete_homework": incomplete_homework,
        "pending_tasks": pending_tasks,
        "notices": notices
    }
    return render(request, 'home1.html', context)

@student_login_required
def profile(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect('login')
    return render(request, 'profile.html', {'student': student})

@student_login_required
def edit_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=student)
    return render(request, 'edit_profile.html', {'form': form})

@student_login_required
def time(request):
    selected_class = request.GET.get("class_name")
    if selected_class:
        time = ClassTimeTable.objects.filter(class_name=selected_class).order_by("day", "start_time")
    else:
        time = ClassTimeTable.objects.all().order_by("class_name", "day", "start_time")
    classes = ClassTimeTable.CLASS_CHOICES
    return render(request, "time.html", {
        "time": time,
        "classes": classes,
        "selected_class": selected_class,
    })

@student_login_required
def notices(request):
    notices = NoticeBoard.objects.all()
    return render(request, 'notices.html',{'notices': notices})

@student_login_required
def attendance(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')
    student = Student.objects.get(id=student_id)
    if student.is_teacher:
        if request.method == 'POST':
            for s in Student.objects.filter(is_teacher=False):
                status = request.POST.get(f'status_{s.id}', 'Absent')
                att, created = Attendance.objects.get_or_create(student=s, date=date.today())
                att.status = status
                att.save()
            messages.success(request, "Attendance updated successfully!")
        students = Student.objects.filter(is_teacher=False)
        attendance_status_list = []
        for s in students:
            att = Attendance.objects.filter(student=s, date=date.today()).first()
            status = att.status if att else 'Absent'
            attendance_status_list.append((s, status))
        return render(request, 'attendance_teacher.html', {
            'attendance_status_list': attendance_status_list,
            'today_date': date.today()
        })
    else:
        attendance_list = Attendance.objects.filter(student=student)
        attendance_by_date = {a.date: a.status for a in attendance_list}
        return render(request, 'attendance_student.html', {
            'attendance_by_date': attendance_by_date,
            'today_date': date.today()
        })

@student_login_required
def homework(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')
    student = Student.objects.get(id=student_id)
    if request.method == "POST":
        if student.is_teacher:
            title = request.POST.get("title")
            subject = request.POST.get("subject")
            description = request.POST.get("description")
            deadline = request.POST.get("deadline")
            file = request.FILES.get("file")
            Homework.objects.create(
                teacher=student,
                title=title,
                subject=subject,
                description=description,
                deadline=deadline,
                file=file
            )
        else:
            homework_id = request.POST.get("homework_id")
            homework = Homework.objects.get(id=homework_id)
            answer_text = request.POST.get("answer_text")
            answer_file = request.FILES.get("answer_file")
            HomeworkSubmission.objects.create(
                homework=homework,
                student=student,
                answer_text=answer_text,
                answer_file=answer_file
            )
        return redirect("homework")
    homeworks = Homework.objects.all().order_by("-created_at")
    homework_data = []
    for hw in homeworks:
        submissions = hw.submissions.all() if student.is_teacher else None
        is_submitted = hw.submissions.filter(student=student).exists() if not student.is_teacher else None
        homework_data.append({
            "homework": hw,
            "submissions": submissions,
            "is_submitted": is_submitted
        })
    return render(request, "homework.html", {
        "homework_data": homework_data,
        "student": student
    })

@student_login_required
def exam(request):
    schedules = ExamSchedule.objects.all().order_by("class_name", "day", "start_time")
    return render(request, "exam.html", {"schedules": schedules})

@student_login_required
def results(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')
    student = Student.objects.get(id=student_id)
    if student.is_teacher:
        if request.method == "POST":
            form = ResultForm(request.POST)
            if form.is_valid():
                result = form.save(commit=False)
                result.teacher = student
                result.save()
                return redirect("results")
        else:
            form = ResultForm()
        results = Result.objects.all().order_by('-id')
        return render(request, "results.html", {
            "form": form,
            "student": student,
            "results": results,
        })
    else:
        results = student.results.all()
        return render(request, "results.html", {
            "results": results,
            "student": student
        })

@student_login_required
def subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects
    }
    return render(request, 'subject.html', context)

@student_login_required
def teacher(request):
    teachers = Student.objects.filter(is_teacher=True)
    context = {
        'teachers': teachers
    }
    return render(request, 'teacher.html', context)

@student_login_required
def bus(request):
    query = request.GET.get("q")
    buses = Bus.objects.prefetch_related("stoppages").all()
    if query:
        buses = buses.filter(stoppages__stoppage_name__icontains=query).distinct()
    return render(request, "bus.html", {"buses": buses, "query": query})

@student_login_required
def seating(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = get_object_or_404(Student, id=student_id)
    return render(request, 'seating.html', {'student': student})

@student_login_required
def library(request):
    return render(request, 'libary.html')
@student_login_required
def hostel_list(request):
    hostels = Hostel.objects.prefetch_related('rooms').all()
    return render(request, 'hostel.html', {'hostels': hostels})

@student_login_required
def about(request):
    return render(request, 'about.html')

@student_login_required
def fees(request):
    return render(request, 'fees.html')

@student_login_required
def library(request):
    books = Book.objects.all().order_by("book_class", "subject", "title")
    form = None
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')
    student = Student.objects.get(id=student_id)
    if student.is_librarian:
        if request.method == "POST":
            if "add_book" in request.POST:
                form = BookForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Book added successfully!")
                    return redirect("library")
            elif "edit_book" in request.POST:
                book_id = request.POST.get("book_id")
                book = get_object_or_404(Book, id=book_id)
                form = BookForm(request.POST, instance=book)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Book updated successfully!")
                    return redirect("library")
            elif "delete_book" in request.POST:
                book_id = request.POST.get("book_id")
                book = get_object_or_404(Book, id=book_id)
                book.delete()
                messages.success(request, "Book deleted successfully!")
                return redirect("library")
        else:
            form = BookForm()

    return render(request, "library.html", {
        "books": books,
        "form": form,
        "student": student
    })

@student_login_required
def activities_page(request):
    student_id = request.session.get("student_id")
    student = get_object_or_404(Student, id=student_id)
    activities = Activity.objects.filter(student=student)
    return render(request, "activities.html", {"activities": activities, "student": student})
@student_login_required
def certificates_page(request):
    student_id = request.session.get("student_id")
    student = get_object_or_404(Student, id=student_id)
    certificates = Certificate.objects.filter(student=student)
    return render(request, "certificates.html", {"certificates": certificates, "student": student})

@student_login_required
def student_documents(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    documents = student.documents.all()
    form = DocumentForm()
    return render(request, 'documents.html', {
        'student': student,
        'documents': documents,
        'form': form
    })
@student_login_required
def add_document(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.student = student
            doc.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})
@student_login_required
def update_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})
@student_login_required
def delete_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    if request.method == "POST":
        doc.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@student_login_required
def timeline(request):
    if request.method == 'POST':
        form = TimelineForm(request.POST, request.FILES)
        if form.is_valid():
            status = form.save(commit=False)
            student_id = request.session.get('student_id')
            if student_id:
                student = Student.objects.get(id=student_id)
                status.student = student
                status.save()
                messages.success(request, 'Post uploaded successfully.')
                return redirect('timeline')
            else:
                messages.error(request, 'You are not logged in.')
                return redirect('timeline')
    else:
        form = TimelineForm()
    statuses = Timeline.objects.all().order_by('-timestamp')
    for s in statuses:
        if s.content:
            ext = s.content.name.split('.')[-1].lower()
            s.is_image = ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
            s.is_video = ext in ['mp4', 'mov', 'avi', 'mkv', 'webm']
        else:
            s.is_image = False
            s.is_video = False
    return render(request, 'timeline.html', {'statuses': statuses, 'form': form})
@student_login_required
def delete_timeline(request, status_id):
    timeline_obj = get_object_or_404(Timeline, id=status_id)
    student_id = request.session.get('student_id')
    if student_id and timeline_obj.student.id == student_id:
        timeline_obj.delete()
        messages.success(request, 'The timeline has been deleted.')
    else:
        messages.error(request, 'You do not have permission to delete this timeline.')
    return redirect('timeline')

def search_result(request):
    result = None
    error = None
    if request.method == "POST":
        student_id = request.POST.get("id")
        dob = request.POST.get("dob")
        try:
            student = Student.objects.get(id=student_id, dob=dob)
            result = Result.objects.filter(student=student).order_by('-uploaded_at').first()
        except Student.DoesNotExist:
            error = "❌ No student found, please try again !"

    return render(request, "search_result.html", {"result": result, "error": error})

@student_login_required
def downloads(request):
    student_id = request.session.get("student_id")
    user = get_object_or_404(Student, id=student_id)
    if request.method == "POST" and (user.is_teacher or user.is_librarian):
        name = request.POST.get("name")
        file = request.FILES.get("file")
        if name and file:
            DownloadFile.objects.create(name=name, file=file, uploaded_by=user)
            return redirect("downloads")
    files = DownloadFile.objects.all().order_by("-id")
    return render(request, "downloads.html", {"files": files, "student": user})
@student_login_required
def download_file(request, pk):
    obj = get_object_or_404(DownloadFile, pk=pk)
    f = obj.file
    return FileResponse(
        f.open("rb"),
        as_attachment=True,
        filename=smart_str(f.name.split("/")[-1])
    )
@student_login_required
def delete_file(request, pk):
    student_id = request.session.get("student_id")
    user = get_object_or_404(Student, id=student_id)
    if not (user.is_teacher or user.is_librarian):
        return HttpResponseForbidden("⚠️ You do not have permission to delete the file")
    obj = get_object_or_404(DownloadFile, pk=pk)
    obj.delete()
    return redirect("downloads")


@student_login_required
def fees(request):
    student_id = request.session.get("student_id")
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        amount_str = request.POST.get("amount", "").strip()
        method = request.POST.get("method", "").strip()
        if not amount_str:
            return render(request, "fees.html", {"error": "Please select an amount.", "student": student})
        if not method:
            return render(request, "fees.html", {"error": "Please select a payment method.", "student": student})
        try:
            amount = int(amount_str)
        except ValueError:
            return render(request, "fees.html", {"error": "Invalid amount.", "student": student})
        if method == "razorpay":
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment = client.order.create({"amount": amount*100, "currency": "INR", "payment_capture": "1"})
            request.session['payment_amount'] = amount
            request.session['payment_method'] = method
            return render(request, "payment_razorpay.html", {"payment": payment, "key_id": settings.RAZORPAY_KEY_ID, "student": student})
        elif method == "paypal":
            return redirect("/paypal_checkout/")
        elif method == "stripe":
            return redirect("/stripe_checkout/")
        elif method == "phonepe":
            return redirect("/phonepe_checkout/")
    return render(request, "fees.html", {"student": student})
@student_login_required
def payment_success(request):
    student_id = request.session.get("student_id")
    student = get_object_or_404(Student, id=student_id)
    amount = request.session.get("payment_amount", 0)
    method = request.session.get("payment_method", "N/A")
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Smart School - Payment Receipt")
    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Student: {student.name}")
    p.drawString(50, 740, f"ID: {student.id}")
    p.drawString(50, 720, f"Class: {student.student_class}")
    p.drawString(50, 700, f"Amount Paid: ₹{amount}")
    p.drawString(50, 680, f"Method: {method}")
    p.drawString(50, 660, f"Transaction ID: XXXXXXXX")
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
    return response