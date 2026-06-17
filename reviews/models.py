from django.db import models
from users.models import User
from stations.models import ChargingStation


class Review(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    station = models.ForeignKey(
        ChargingStation,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.station.station_name} - {self.rating}"