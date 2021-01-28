from django.contrib import admin

# Register your models here.
from .models import Bid, Comment, User, Listing, Category, Pet

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "listing_created", "creator", "status")

class BidAdmin(admin.ModelAdmin):
    list_display = ("bidder", "item", "amount", "bid_timestamp")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("commenter", "topic", "comment_timestamp")

admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Pet)
admin.site.register(Listing, ListingAdmin)