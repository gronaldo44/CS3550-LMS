from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from . import models
import logging

# Create your views here.
def index(request):
    # collect data
    assignments = models.Assignment.objects.all()
    if not assignments.exists():
        raise Http404("No assignments found.")
    
    # call template
    assignments_dictionary = {
        "assignments": assignments
    }
    return render(request, "index.html", assignments_dictionary)

def assignment(request, assignment_id):
    # Handle submit-assignment form POSTs
    if request.method == "POST":
        _submit_assignment(request, assignment_id)
        return redirect(f"/{assignment_id}/")
    

    a = get_object_or_404(models.Assignment, id=assignment_id)
    my_user = request.user
    student_submission_file = ""
    student_submission_filename = ""
    total_submissions = None
    grader_submissions_count = None
    total_students = None
    is_ta = False
    
    if my_user.is_authenticated:
        if not is_student(my_user):
            # collect data for grader action card
            is_ta = True
            total_submissions = a.submission_set.count()
            grader_submissions_count = a.submission_set.filter(grader=my_user).count()
            total_students = models.Group.objects.get(name="Students").user_set.count()
        else:
            # collect data for student action card
            student_submission_set = a.submission_set.filter(author=my_user)
            if student_submission_set.exists():
                student_submission_file = student_submission_set[0].file.url
                student_submission_filename = student_submission_set[0].file.name.split('/')[-1]
            else:
                student_submission_file = ""
                student_submission_filename = ""

    # call template
    context = {
        "assignment": a,
        "student_submission_file": student_submission_file,
        "student_submission_filename": student_submission_filename,
        "total_submissions": total_submissions,
        "grader_submissions_count": grader_submissions_count,
        "total_students": total_students,
        "is_student": not is_ta
    }
    return render(request, "assignment.html", context)

def _submit_assignment(request, assignment_id):
    # get user's submissions to this assignment
    a = get_object_or_404(models.Assignment, id=assignment_id)
    my_grader = get_object_or_404(models.User, username="g")    # hard-coded login
    my_user = get_object_or_404(models.User, username="a")  # hard-coded login
    my_user_old_submissions = a.submission_set.filter(author=my_user)
    new_submission_file = request.FILES['assignment-submission']
    
    # Put new submission in the database
    if my_user_old_submissions.exists():
        # update existing submission
        my_user_submission = my_user_old_submissions[0]
        logging.getLogger(__name__).warning(
            f"Updating existing submission {my_user_submission.file.name.split('/')[-1]}"
            f"to {new_submission_file.name.split('/')[-1]}"
            )
        my_user_submission.file = new_submission_file
        my_user_submission.save()
    else:
        # create a new submission for this user
        logging.getLogger(__name__).warning(
            f"Creating new submission {new_submission_file.name.split('/')[-1]}"
        )
        new_submission = models.Submission.objects.create(
            assignment = a,
            author = my_user,
            grader = my_grader,
            file = request.FILES['assignment-submission'],
            score = None
        )
        new_submission.save()

def submissions(request, assignment_id):
    # Handle grade-submissions form POSTs
    errors = {}
    generic_errors = []
    if request.method == "POST":
        _update_grades(request, assignment_id, errors, generic_errors)
        if not errors and not generic_errors:
            return redirect(f"/{assignment_id}/submissions/")
    # # debug
    # errors[1] = "Testing"
    # generic_errors.append({
    #     "msg": "Testing"
    # })
    # generic_errors.append({
    #     "msg": "Testing2"
    # })
    
    # collect data
    a = get_object_or_404(models.Assignment, id=assignment_id)
    my_user = request.user
    submissions_data = []
    if my_user.is_authenticated:
        if my_user.is_superuser:
            my_submissions = a.submission_set.order_by("author__username")
        elif not is_student(my_user):
            my_submissions = a.submission_set.filter(grader=my_user).order_by("author__username")
        for s in my_submissions:
            s_error = errors[s.id] if s.id in errors else ""
            submissions_data.append({
                "student": s.author.get_full_name(),
                "file": s.file.url,
                "score": s.score,
                "id": s.id,
                "error_msg": s_error
            })

    # call template
    context = {
        "a_id": a.id,
        "a_title": a.title,
        "a_points": a.points,
        "submissions_data": submissions_data,
        "generic_errors": generic_errors
    }
    return render(request, "submissions.html", context)

def _update_grades(request, assignment_id, errors, generic_errors):
    updates = []
    for post_key in request.POST:
        # Ignore POSTs not related to grading submissions
        if not post_key.startswith("grade-"):
            logging.getLogger(__name__).warning(f"POST \"{post_key}\" was ignored when updating grades.")
            continue
        
        # Get submission id
        s_id = int(post_key.removeprefix("grade-"))
        
        # Get this submission from db
        try:
            s = get_object_or_404(models.Submission, id=s_id)
        except Http404:
            generic_errors.append({
                "msg": f"Submission {s_id} not found in db."
            })
            logging.getLogger(__name__).warning(f"Submission {s_id} not found in db.")
            continue
            
        # Check if an assignment exists for this submission
        try:
            assignment_exists = get_object_or_404(models.Assignment, id=assignment_id)
            my_user_exists = get_object_or_404(models.User, username="g")  # hard-coded login
            get_object_or_404(models.Submission, id=s_id, assignment=assignment_exists, 
                              grader=my_user_exists)
        except Http404:
            errors[s_id] = "Assignment not found for this submission."
            logging.getLogger(__name__).warning(errors[s_id])
            continue
        
        # Update this submission's score
        newScore = request.POST[post_key]
        if newScore == "":
            s.score = None
        else:
            try:
                # Make sure newScore is a valid number
                newScore = Decimal(newScore).quantize(Decimal('0.01'))
                if newScore < 0 or newScore > assignment_exists.points:
                    raise ValueError("Score must be a number between 0 and max assignment points")
                s.score = Decimal(newScore)
            except (InvalidOperation, ValueError):
                errors[s_id] = "Score must be a number between 0 and max points for this assignment."
                logging.getLogger(__name__).warning(errors[s_id])
                continue
        # Queue this update  
        updates.append(s)
    
    # Update database
    models.Submission.objects.bulk_update(updates, ['score'])

def profile(request):
    # collect data
    assignments = models.Assignment.objects.all()
    if not assignments.exists():
        raise Http404("No assignments found.")
    
    my_user = get_object_or_404(models.User, username="g")   # hard-coded login
    username = request.user.get_full_name() if request.user.is_authenticated else "Guest"

    assignments_data = []
    for a in assignments:
        my_submissions = a.submission_set.filter(grader=my_user).count()
        my_graded = a.submission_set.filter(grader=my_user, score__isnull=False).count()

        assignments_data.append({
            "assignment": a,
            "my_submissions": my_submissions,
            "my_graded": my_graded
        })

    # Call template
    context = {
        "assignments_data": assignments_data,
        "username": username
    }
    return render(request, "profile.html", context)

def login_form(request):
    if request.method == "POST":
        username = request.POST.get("username","")
        password = request.POST.get("password","")
        user = authenticate(
            request,
            username = username,
            password = password
        )
        if user is not None:
            print("login success")
            login(request, user)
            return redirect("/profile")
        else:
            print("login failed")
            return render(request, "login.html")
    return render(request, "login.html")

def logout_form(request):
    logout(request)
    return redirect("/profile/login")

def show_upload(request, filename):
    logging.getLogger(__name__).warning(f"Show Upload: {filename}")
    submission = get_object_or_404(models.Submission, file__icontains=filename)
    return HttpResponse(submission.file.open())

def is_student(user):
    return user.groups.filter(name="Students").exists()