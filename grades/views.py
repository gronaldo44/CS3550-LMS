from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from . import models

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
    # collect data
    a = get_object_or_404(models.Assignment, id=assignment_id)
    total_submissions = a.submission_set.count()
    my_user = get_object_or_404(models.User, username="g")   # hard-coded login
    my_submissions = a.submission_set.filter(grader=my_user).count()
    total_students = models.Group.objects.get(name="Students").user_set.count()

    # call template
    submissions_dictionary = {
        "assignment": a,
        "total_submissions": total_submissions,
        "my_submissions": my_submissions,
        "total_students": total_students
    }
    return render(request, "assignment.html", submissions_dictionary)

def submissions(request, assignment_id):
    # collect data
    a = get_object_or_404(models.Assignment, id=assignment_id)
    my_user = get_object_or_404(models.User, username="g")   # hard-coded login
    my_submissions = a.submission_set.filter(grader=my_user).order_by("author__username")

    submissions_data = []
    for s in my_submissions:
        student = s.author.get_full_name()
        file = s.file.url
        score = s.score

        submissions_data.append({
            "student": student,
            "file": file,
            "score": score
        })

    # debug
    #print("Submissions Data: ", submissions_data)
    #print("first username: ", submissions_data[0]["student"])

    # call template
    submissions_dictionary = {
        "a_id": a.id,
        "a_title": a.title,
        "a_points": a.points,
        "submissions_data": submissions_data
    }
    return render(request, "submissions.html", submissions_dictionary)

def profile(request):
    # collect data
    assignments = models.Assignment.objects.all()
    if not assignments.exists():
        raise Http404("No assignments found.")
    
    my_user = get_object_or_404(models.User, username="g")   # hard-coded login

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
    data_dictionary = {
        "assignments_data": assignments_data
    }
    return render(request, "profile.html", data_dictionary)

def login_form(request):
    return render(request, "login.html")
