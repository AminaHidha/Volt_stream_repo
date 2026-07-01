# chargers/models.py

from django.db import models

from stations.models import ChargingStation


class Charger(models.Model):

    station = models.ForeignKey(
        ChargingStation, on_delete=models.CASCADE, related_name="chargers"
    )

    charger_name = models.CharField(max_length=100)

    charger_type = models.CharField(max_length=50, choices=[("AC", "AC"), ("DC", "DC")])

    power_output = models.IntegerField(help_text="kW")

    price_per_kwh = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[("available", "Available"), ("busy", "Busy"), ("offline", "Offline")],
        default="available",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.charger_name
