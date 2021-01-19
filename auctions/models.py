from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField


class User(AbstractUser):
    pass

class Listing(models.Model):

    title = models.CharField(max_length=50) 
    description = models.TextField(max_length=300)
    imageURL = models.URLField()
    listing_created = models.DateField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    bidders = models.ManyToManyField(User, blank=True, related_name="listings")
    STATUS = Choices('Active', 'Closed')
    status = StatusField()

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):

    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_on_item")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder} for {self.listing}: {self.amount}"

class Comment(models.Model):

    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="regarding_listing")
    comment_timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} on {self.listing}"