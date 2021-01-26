from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField
from django.core.validators import URLValidator, MinValueValidator
from decimal import *


class User(AbstractUser):
    pass

class Listing(models.Model):

    title = models.CharField(max_length=50) 
    description = models.TextField(max_length=350)
    imageURL = models.URLField(max_length=250, blank=True, null=True)
    listing_created = models.DateField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    STATUS = Choices('Active', 'Closed')
    status = StatusField()
    reserve = models.DecimalField(max_digits=10, decimal_places=2, default=0.01, validators = [MinValueValidator(Decimal('0.01'))])
    bidders = models.ManyToManyField(User, blank=True, related_name="listings")

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):

    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="item", null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder} for {self.item}: {self.amount}"

class Comment(models.Model):

    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_by_user")
    topic = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments_by_topic")
    comment_timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} on {self.listing}"

# https://pypi.org/project/django-multiselectfield/
class PetType(models.Model):

    ANY = 'A'
    CAT = 'C'
    DOG = 'D'
    BIRD = 'B'
    REPTILE = 'R'
    CRITTER = 'S'
    HORSE = 'H'
    OTHER = 'O'

    PET_CHOICES = [
        (ANY, 'Any Pet'),
        (CAT, 'Cat'),
        (DOG, 'Dog'),
        (BIRD, 'Bird'),
        (REPTILE, 'Reptile'),
        (CRITTER, 'Small Critter'),
        (HORSE, 'Horse'),
        (OTHER, 'Other Pet')
    ]

    pet_type = models.CharField(
        max_length=1,
        choices=PET_CHOICES,
        default=ANY
    )

    item = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="pet_type_items")

    def __str__(self):
        return f"{self.pet_type}"


