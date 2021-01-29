from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField
from django.core.validators import URLValidator, MinValueValidator
from decimal import *


class User(AbstractUser):
    pass

class Category(models.Model):

    category = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.category}"


class Pet(models.Model):

    pet_type = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.pet_type}"


class Listing(models.Model):

    title = models.CharField(max_length=50) 
    description = models.TextField(max_length=250)
    imageURL = models.URLField(max_length=250, blank=True, null=True)
    listing_created = models.DateField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_by_creator")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="winnings")
    STATUS = Choices('Active', 'Closed')
    status = StatusField()
    current_price = models.DecimalField(max_digits=10, blank=True, null=True, decimal_places=2)
    reserve = models.DecimalField(max_digits=10, decimal_places=2, default=0.01, validators = [MinValueValidator(Decimal('0.01'))])
    # bidders = models.ManyToManyField(User, blank=True, related_name="listings")
    categories = models.ManyToManyField(Category, related_name="items_by_category")
    pet_type = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="items_by_pet")

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['-last_modified']


class Bid(models.Model):

    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="items", null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder} for {self.item}: {self.amount}"

class Comment(models.Model):

    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_by_user")
    topic = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments_by_topic")
    comment_text = models.TextField(max_length=350)
    comment_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} on {self.listing}"

class WatchedListing(models.Model):

    item = models.ForeignKey(Listing, related_name="watched", on_delete=models.CASCADE, null=True)
    watcher = models.ManyToManyField(User, related_name="watching")

    def __str__(self):
        return f"{self.item}"