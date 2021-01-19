from django.contrib import admin

# Register your models here.
from .models import Bid, Comment, User, Listing

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "listing_created", "creator")

class BidAdmin(admin.ModelAdmin):
    list_display = ("bidder", "listing", "amount", "bid_timestamp")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("commenter", "listing", "comment_timestamp")

admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)