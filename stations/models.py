# Create your models here.
from django.db import models
from users.models import User

class ChargingStation(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stations"
    )

    station_name = models.CharField(max_length=200)

    address = models.TextField()

    city = models.CharField(max_length=100)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    opening_time = models.TimeField()

    closing_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive")
        ],
        default="active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.station_name