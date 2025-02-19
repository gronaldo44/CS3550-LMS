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
    grader = get_object_or_404(models.User, username="g")
    my_submissions = a.submission_set.filter(grader=grader).count()
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
    return render(request, "submissions.html")

def profile(request):
    return render(request, "profile.html")

def login_form(request):
    return render(request, "login.html")
