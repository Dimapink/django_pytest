from django.db import models


class Student(models.Model):
    objects = models.Manager()
    name = models.TextField()

    birth_date = models.DateField(
        null=True,
    )


class Course(models.Model):
    objects = models.Manager()
    name = models.TextField()

    students = models.ManyToManyField(
        Student,
        blank=True,
    )
