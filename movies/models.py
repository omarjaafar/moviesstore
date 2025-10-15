from django.db import models
from django.contrib.auth.models import User
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    def get_thumbs_up_count(self):
        return  self.movievote_set.filter(vote_type='up').count()
    def get_thumbs_down_count(self):
        return  self.movievote_set.filter(vote_type='down').count()
    def get_net_score(self):
        return self.get_thumbs_up_count() - self.get_thumbs_down_count()
    
    def user_vote(self, user):
        if user.is_authenticated:
            try:
                return self.movievote_set.get(user=user).vote_type
            except MovieVote.DoesNotExist:
                return None
        return None
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
class MovieVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=[
        ('up', 'Thumbs Up'),
        ('down', 'Thumbs Down')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} = {self.movie.name} - {self.vote_type}"
    