from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.forms import HiddenInput
from django.http import JsonResponse

from .models import User, Listing, Bid, Comment, Pet, Category, WatchedListing
from .forms import BidForm, AddListingForm, CommentForm
from .util import GetListingBids, GetHighestBidder, CapitalizeTitle



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.order_by('-last_modified').filter(status='Active'),
        "ended": Listing.objects.order_by('-last_modified').filter(status='Closed')
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required()
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request, listing_id):

    # get listing info, high bid or reserve for price, and bid history
    listing_bid = GetListingBids(listing_id)
    listing = listing_bid[0]
    price = listing.current_price
    bids = listing_bid[2]
    user = request.user
    categories = listing.categories.all()

    # check if user is listing creator so listing status and close button are displayed if active
    if user == listing.creator:          
        owner_listing_status = listing.status
    else:
        owner_listing_status = None

    # check if user is higher bidder
    high_bidder = GetHighestBidder(listing_id)
    
    if listing.status == 'Active':
        # if user is highest bidder on active listing, show message
        if user == high_bidder:
            winning_message = f"You are currently the highest bidder!"
            messages.add_message(request, messages.SUCCESS, winning_message)
        # populate bid form with initial values based on above and current user's id
        # item and bidder are hidden fields but must be initialized or will trigger validation errors 
        bid_form = BidForm(initial={'item': listing_id, 'amount': price, 'bidder': request.user.id})
    else:
        # if user is highest bidder and auction has ended, notify winner
        if user == high_bidder:
            won_message = f"Congratulations! You won this auction!"
            messages.add_message(request, messages.SUCCESS, won_message)
        # set bid form to none so it won't display
        bid_form = None

    # check user's watchlist for item to assign true/false to watchlisted
    watchlist_check = WatchedListing.objects.filter(watcher=user,item=listing)
    watching_all = WatchedListing.objects.filter(item=listing)
    watchers = len(watching_all)

    # empty query returned so not on watchlist
    if len(watchlist_check) == 0:
        watchlisted = False
    # query had results, so already on watchlist
    else:
        watchlisted = True

    # add comment form initialized with commenter and topic
    comment_form = CommentForm(initial={'commenter': request.user.id, 'topic': listing_id})

    # populate comments section
    comments = Comment.objects.filter(topic=listing)

    return render(request, "auctions/listing.html", {
        "owner_status": owner_listing_status,
        "listing": listing,
        "bids": bids,
        "price": price,
        "bid_form": bid_form,
        "categories": categories,
        "watchlisted": watchlisted,
        "watchers": watchers,
        "comment_form": comment_form,
        "comments": comments
    })


@login_required()
def bid(request, listing_id):

    # if bid submitted from listing page
    if request.method == "POST":
        
        # get bid amount from form 
        bid_form = BidForm(request.POST)
        listing = Listing.objects.get(pk=listing_id)

        # if bid is valid
        if bid_form.is_valid():

            bid = bid_form.save()
            listing.current_price = bid.amount
            listing.save()
            listing = bid.item
            bidder = bid.bidder

            bid_message = f"Hooray {bidder.username}! You bid ${bid.amount} on {listing.title}!"
            messages.add_message(request, messages.SUCCESS, bid_message)

            return render(request, "auctions/index.html", {
                "listings": Listing.objects.filter(status='Active'),
                "ended": Listing.objects.order_by('-last_modified').filter(status='Closed')
            })

        # invalid bid form returns to listing page with django generated error messages
        else:

            listing_bid = GetListingBids(listing_id)
            listing = listing_bid[0]
            price = listing_bid[1]
            bids = listing_bid[2]

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bids": bids,
                "price": price,
                "bid_form": bid_form
            })


    # if bid route reached by GET
    else:
        bid_message = f"Select an auction listing to bid on an item!"
        messages.add_message(request, messages.WARNING, bid_message)
        
        return render(request, "auctions/index.html")

# create a new listing route
@login_required()
def new(request):

    # new listing submitted from add listing form   
    if request.method == "POST":

        # get form data
        listing_form = AddListingForm(request.POST)

        # new listing form and server-side form validation
        if listing_form.is_valid():

            listing = listing_form.save(commit=False)
            listing.title = CapitalizeTitle(listing.title)
            listing.current_price = listing.reserve
            listing.save()
            listing_form.save_m2m()
            listing_id = listing.id

            new_message = f"Successfully added {listing.title} listing!"
            messages.add_message(request, messages.SUCCESS, new_message)

            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

        # new listing fails server-side form validation
        else:
            return render(request, "auctions/new.html", {
                "new_listing_form": listing_form
            })


    # reached by get
    else:

        # populate listing form with initial values for hidden fields to prevent validation errors
        # template gets customization from https://pypi.org/project/django-multiselectfield/

        new_listing_form = AddListingForm(initial={'creator': request.user.id, 'status': 'Active'})

        return render(request, "auctions/new.html", {
            "new_listing_form": new_listing_form
        })


# close a listing route and set winner
@login_required()
def close(request, listing_id):

    # if close button submitted from listing page by creator (button will only display for creator)
    if request.method == "POST":

        listing = Listing.objects.get(pk=listing_id)
        high_bidder = GetHighestBidder(listing_id)
        listing.winner = high_bidder

        if high_bidder is not None:
            winner_message = f"Winner: {listing.winner}"
        else:
            winner_message = "No bids. No winner."

        listing.status = 'Closed'
        listing.save()
        
        ended_message = f"You ended this auction. {winner_message}"
        messages.add_message(request, messages.WARNING, ended_message)

        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

    # if reached by GET show error message on listing page
    else:
        error_message = f"You can't end an auction that you didn't create!"
        messages.add_message(request, messages.WARNING, error_message)
        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))


def browse(request):

    # get pet type listings and add to dicts
    # pet type name as key and listings as value

    # get all pet categories
    pet_types = Pet.objects.all()

    # create an empty list to hold dictionaries, which will contain pet type and corresponding listings
    all_pet_listings = []

    # iterate through listings and get corresponding pet type
    for i in range(len(pet_types)):
        # store pet_type name for dict
        pet_type = pet_types[i].pet_type
        # store listings for dict
        listings = pet_types[i].items_by_pet.filter(status='Active')
        # add above to dict as key and value respectively
        pet_dict = {pet_type : listings}
        # add each dict to a list of dicts
        all_pet_listings.append(pet_dict)


    # get categories with listings and put in dicts
    # category name as key and listings as value

    # get all categories
    categories = Category.objects.all()

    # create empty list to store category/listing dicts
    categorized_listings = []
    category_slugs = []

    # iterate through categories and get all listings in that category
    for i in range(len(categories)):
        # get name to stash in dict as key
        category_name = categories[i].category

        # get category and look up all active listings in that category, based on many-to-many related name in listing
        category = categories[i]
        category_listings = category.items_by_category.filter(status='Active')

        # add name and listings to dict for displaying in template
        category_dict = {category_name:category_listings}

        # add dict to categorized listings list
        categorized_listings.append(category_dict)

    return render(request, "auctions/browse.html", {
        "listings": Listing.objects.filter(status='Active'),
        "pet_listings": all_pet_listings,
        "categorized_listings": categorized_listings
    })


def category(request, slug):

    # determine if slug is a pet type or category
    pet_types = Pet.objects.all()
    is_pet = False

    for pet_type in pet_types:
        if slug == pet_type.slug:
            is_pet = True
            
    if is_pet:
        # get pet for that slug
        pet = Pet.objects.get(slug=slug)
        # get all listings for that pet, using related name in listing 
        listings = pet.items_by_pet.filter(status='Active')
        category = pet.pet_type
    else:
        category = Category.objects.get(slug=slug)
        listings = category.items_by_category.filter(status='Active')

    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings
    })



@login_required()
def watchlist_edit(request, listing_id):
    
    listing = Listing.objects.get(pk=listing_id)
    user = request.user
    
    # check if listing is on watchlist
    watchlist_check = WatchedListing.objects.filter(watcher=user,item=listing)

    # if watchlist_check is zero and item is not on watchlist, add to watchlist
    if len(watchlist_check) == 0:
        watched_listing = WatchedListing()
        watched_listing.item = listing
        watched_listing.save()
        watched_listing.watcher.add(user)

        watched_message = f"Added {watched_listing.item} to your watchlist!"
        messages.add_message(request, messages.SUCCESS, watched_message)

        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

    # else if check returns one listing, remove from watchlist
    elif len(watchlist_check) == 1:

        watchlist_check.delete()

        deleted_message = f"Removed {listing} from your watchlist!"
        messages.add_message(request, messages.WARNING, deleted_message)

        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

    # if anything else happens, something screwy happened
    else:
        error_message = f"There was an error editing your watchlist."
        messages.add_message(request, messages.WARNING, error_message)

        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))



@login_required()
def watchlist(request):

    user = request.user
    listings = user.watching.all()

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required()
def comment_edit(request, listing_id):

    # comment submitted from listing form   
    if request.method == "POST":

        # get form data
        comment_form = CommentForm(request.POST)

        # new listing form and server-side form validation
        if comment_form.is_valid():

            comment = comment_form.save()

            comment_msg = f"Your comment was submitted."
            messages.add_message(request, messages.SUCCESS, comment_msg)

            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

        # new listing fails server-side form validation
        else:

            error_message = f"There was an error processing your comment."
            messages.add_message(request, messages.WARNING, error_message)  
            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))
    
    else:
        error_message = f"Comments can only be submitted on a listing page."
        messages.add_message(request, messages.WARNING, error_message)  
        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

    

    