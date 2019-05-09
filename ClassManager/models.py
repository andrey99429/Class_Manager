from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=6, unique=True)


class Student(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    gmail = models.CharField(max_length=100, null=True)
    folder_id = models.CharField(max_length=200, null=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField()
    file_name = models.CharField(max_length=50)
    variants = models.IntegerField()
    visible = models.BooleanField()


class Work(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    file_id = models.CharField(max_length=200, null=True)
    modified_time = models.DateTimeField(null=True)
    variant = models.IntegerField()
    mark = models.IntegerField(null=True)
    comment = models.TextField(max_length=1000, null=True)
