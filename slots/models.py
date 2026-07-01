from django.db import models

from chargers.models import Charger


class Slot(models.Model):

    charger = models.ForeignKey(Charger, on_delete=models.CASCADE, related_name="slots")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    is_booked = models.BooleanField(
        default=False,
        db_index=True,  # ✅ checked on every booking + filtered in StationDetail
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["charger", "is_booked"]
            ),  # ✅ "available slots for this charger" query
        ]

    def __str__(self):
        return f"{self.charger.charger_name}" f" - {self.start_time}"
