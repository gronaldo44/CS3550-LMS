from django.shortcuts import render
from django.http import Http404
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
    return render(request, "assignment.html")

def submissions(request, assignment_id):
    return render(request, "submissions.html")

def profile(request):
    return render(request, "profile.html")

def login_form(request):
    return render(request, "login.html")
