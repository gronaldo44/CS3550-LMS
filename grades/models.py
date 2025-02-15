from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    weight = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        return (f"Assignment: {self.title} "
        f"| Description: {len(self.description)} characters "
        f"| Deadline: {self.deadline.strftime('%Y-%m-%d %H:%M:%S')} "
        f"| Points: {self.points} "
        f"| Weight: {self.weight}")

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    grader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='graded_set')
    file = models.FileField(upload_to='submissions/')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return (f"Submission for '{self.assignment.title}' by {self.author.username} "
        f"| File: {self.file.name.split('/')[-1]} "
        f"| Grader: {self.grader.username if self.grader else 'Not Assigned'} "
        f"| Score: {self.score if self.score is not None else 'Not Graded'}")
