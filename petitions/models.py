from django.db import models
from django.contrib.auth.models import User


class Petition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="petitions")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def votes_count(self):
        return self.votes.count()


class Vote(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("petition", "user")  # prevents double-voting

    def __str__(self):
        return f"{self.user.username} voted on {self.petition.title}"
