from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

class PurchaseLocation(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)

    class Meta:
        unique_together = ('city', 'state', 'country')

    def __str__(self):
        parts = [self.city]
        if self.state:
            parts.append(self.state)
        parts.append(self.country)
        return ', '.join(parts)

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(PurchaseLocation, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.id) + ' - ' + self.user.username

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
