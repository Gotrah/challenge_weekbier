from enum import Enum
from datetime import timedelta

from django.db import models


class Player(models.Model):
    """A player participating in the challenge."""
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def num_checkins(self):
        """Return the score of the player."""
        return self.checkin_set.count()

    def num_weeks_scored(self):
        week_numbers = set()
        valid_checkins = [checkin for checkin in self.checkin_set.all() if checkin.is_valid()]
        for checkin in valid_checkins:
            # Add one day to start the new week on Sunday
            week_numbers.add((checkin.date + timedelta(days=1)).isocalendar()[1])

        return len(week_numbers)

    def score(self):
        """Return the score of the player."""
        valid_checkins = [checkin for checkin in self.checkin_set.all() if checkin.is_valid()]
        return self.num_weeks_scored() * 2 + len(valid_checkins)

    def __str__(self):
        """Return a string representation of the model."""
        return self.name


class Checkin(models.Model):
    """A checkin for a player."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date = models.DateField()
    place = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def status(self):
        if Checkin.objects.filter(player=self.player, date__lt=self.date, city=self.city).count() > 0:
            return self.Status.DUPLICATE_CITY
        elif Checkin.objects.filter(player=self.player, date=self.date, date_added__lt=self.date_added).count() > 0:
            return self.Status.DOUBLE_CHECKIN_ON_DATE
        else:
            return self.Status.OK

    def is_valid(self):
        return self.status() == self.Status.OK

    def __str__(self):
        """Return a string representation of the model."""
        return f"{self.player.name} checked in for {self.date} at {self.place} in {self.city} at {self.date_added}"

    class Status(Enum):
        OK = "OK"
        DUPLICATE_CITY = "Duplicate city"
        DOUBLE_CHECKIN_ON_DATE = "Double checkin on date"
