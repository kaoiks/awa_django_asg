from django.db import models
from django.conf import settings


class Genre(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Image(models.Model):
    image_url = models.CharField(max_length=1000)


class Movie(models.Model):
    title = models.CharField(max_length=1000)
    genres = models.ManyToManyField(Genre)
    image = models.ManyToManyField(Image)


class Rating(models.Model):
    value = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)


class Comment(models.Model):
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)
    text = models.CharField(max_length=1000)
    date = models.DateTimeField()
