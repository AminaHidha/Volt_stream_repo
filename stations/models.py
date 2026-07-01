from django.db import models

from users.models import User


class Amenity(models.Model):
    """
    Represents a facility available at a charging station.
    Examples: WiFi, Parking, Restroom, CCTV, Cafe, EV Shop.

    Many to Many: One station can have many amenities,
    one amenity can belong to many stations.
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ChargingStation(models.Model):

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stations")

    station_name = models.CharField(max_length=200)
    address = models.TextField()

    city = models.CharField(
        max_length=100, db_index=True  # ✅ filtered by city on PublicStationListView
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("inactive", "Inactive")],
        default="active",
        db_index=True,  # ✅ filtered everywhere (status="active")
    )

    amenities = models.ManyToManyField(Amenity, blank=True, related_name="stations")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.station_name
