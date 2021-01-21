from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Bid, Comment
from .forms import BidForm
from .util import GetListingBids

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

    listing_bid = GetListingBids(listing_id)
    listing = listing_bid[0]
    price = listing_bid[1]
    bids = listing_bid[2]

    current_user = request.user
    bid_form = BidForm({'amount': price, 'item': listing_id, 'bidder': current_user.id})

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "price": price,
        "bid_form": bid_form
    })

def bid(request, listing_id):

    # bid submitted from listing page
    if request.method == "POST":
        
        # get query from search form
        bid = BidForm(request.POST)
        listing_bid = GetListingBids(listing_id)
        listing = listing_bid[0]
        price = listing_bid[1]
        bids = listing_bid[2]
        reserve = listing.reserve

        # bid passes server-side form validation
        if bid.is_valid():
     
            bid_amount = bid.cleaned_data["amount"]

            # bid.save()
            
            current_user = request.user
            name = current_user.username
            bid_message = f"Congrats {name}! You successfully bid ${bid_amount} on {listing.title}!"

            return render(request, "auctions/bids.html", {
                "bid_message": bid_message,
                "reserve": reserve,
                "price": price
            })

        # invalid bid form returns to listing page with django generated error messages
        else:

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bids": bids,
                "price": price,
                "bid_form": bid
            })

    return render(request, "auctions/index.html")