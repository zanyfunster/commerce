from django.contrib import admin

# Register your models here.
from .models import Bid, Comment, User, Listing, Category, Pet, WatchedListing

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "current_price", "last_modified", "listing_created", "creator")
    list_filter = ("categories", "pet_type")
    filter_horizontal = ("categories", )

class BidAdmin(admin.ModelAdmin):
    list_display = ("bidder", "item", "amount", "bid_timestamp")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("commenter", "topic", "comment_timestamp")

class WatchedListingAdmin(admin.ModelAdmin):
    filter_horizontal = ("watcher",)


admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Pet)
admin.site.register(WatchedListing, WatchedListingAdmin)
admin.site.register(Listing, ListingAdmin)