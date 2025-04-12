from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied

# Create your models here.
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    weight = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        return (f"Assignment: {self.title} "
                f"| ID: {self.id}"
                f"| Description: {len(self.description)} characters "
                f"| Deadline: {self.deadline.strftime('%Y-%m-%d %H:%M:%S')} "
                f"| Max Points: {self.points} "
                f"| Weight: {self.weight}")

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    grader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='graded_set')
    file = models.FileField()
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    def change_grade(self, user, new_score):
        if user.is_superuser or user == self.grader:
            self.score = new_score
        else:
            raise PermissionDenied("You do not have permission to change this grade")

    def __str__(self):
        return (f"Submission for '[id: {self.assignment.id}] {self.assignment.title}' by {self.author.get_full_name()} "
                f"| ID: {self.id}"
                f"| File: {self.file.name.split('/')[-1]} "
                f"| Grader: {self.grader.get_full_name() if self.grader else 'Not Assigned'} "
                f"| Score: {self.score if self.score is not None else 'Not Graded'}")
