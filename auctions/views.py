from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages



from .models import User, Listing, Bid, Comment
from .forms import BidForm, AddListingForm
from .util import GetListingBids, GetHighestBidder

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status='Active')
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
    price = listing_bid[1]
    bids = listing_bid[2]

    # display message if bidder is already highest bidder
    high_bidder = GetHighestBidder(listing_id)
    user = request.user

    if user == high_bidder:
        new_message = f"You are currently the highest bidder!"
        messages.add_message(request, messages.SUCCESS, new_message)

    # populate bid form with initial values based on above and current user's id
    # item and bidder are hidden fields but must be initialized or will trigger validation errors 
    bid_form = BidForm(initial={'item': listing_id, 'amount': price, 'bidder': request.user.id})

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "price": price,
        "bid_form": bid_form
    })

def bid(request, listing_id):

    # if bid submitted from listing page
    if request.method == "POST":
        
        # get bid amount from form 
        bid_form = BidForm(request.POST)

        # if bid is valid
        if bid_form.is_valid():

            bid = bid_form.save()
            listing = bid.item
            bidder = bid.bidder

            bid_message = f"Hooray {bidder.username}! You bid ${bid.amount} on {listing.title}!"
            messages.add_message(request, messages.SUCCESS, bid_message)

            return render(request, "auctions/index.html", {
                "listings": Listing.objects.filter(status='Active')
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
def new(request):

    # new listing submitted from add listing form   
    if request.method == "POST":

        # get form data
        listing_form = AddListingForm(request.POST)
        
        # new listing form passes server-side form validation
        if listing_form.is_valid():

            listing = listing_form.save()
            listing_id = listing.id
            title = listing.title

            new_message = f"Your listing for {title} is now active!"
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
        new_listing_form = AddListingForm(initial={'creator': request.user.id, 'status': 'Active'})

        return render(request, "auctions/new.html", {
            "new_listing_form": new_listing_form
        })