from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.forms import HiddenInput

from .models import User, Listing, Bid, Comment, PetType
from .forms import BidForm, AddListingForm, SelectPetTypeForm
from .util import GetListingBids, GetHighestBidder, CapitalizeTitle


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status='Active'),
        "ended": Listing.objects.filter(status='Closed')
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
    price = listing_bid[1]
    bids = listing_bid[2]
    user = request.user
    pet_type = PetType.objects.get(item=listing)

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

    return render(request, "auctions/listing.html", {
        "owner_status": owner_listing_status,
        "listing": listing,
        "category": pet_type.get_pet_type_display(),
        "bids": bids,
        "price": price,
        "bid_form": bid_form
    })


@login_required()
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
@login_required()
def new(request):

    # new listing submitted from add listing form   
    if request.method == "POST":

        # get form data
        listing_form = AddListingForm(request.POST)
        category_form = SelectPetTypeForm(request.POST)
        
        # new listing form and server-side form validation
        if listing_form.is_valid() and category_form.is_valid():

            listing = listing_form.save(commit=False)
            listing.title = CapitalizeTitle(listing.title)
            listing.save()
            listing_id = listing.id

            categories = category_form.save(commit=False)
            listing = Listing.objects.get(pk=listing_id)
            categories.item = listing
            categories.save()

            new_message = f"Successfully added {listing.title} listing!"
            messages.add_message(request, messages.SUCCESS, new_message)

            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

        # new listing fails server-side form validation
        else:
            return render(request, "auctions/new.html", {
                "new_listing_form": listing_form,
                "category_form": category_form
            })


    # reached by get
    else:

        # populate listing form with initial values for hidden fields to prevent validation errors
        # template gets customization from https://pypi.org/project/django-multiselectfield/

        new_listing_form = AddListingForm(initial={'creator': request.user.id, 'status': 'Active'})
        select_category_form = SelectPetTypeForm()

        return render(request, "auctions/new.html", {
            "new_listing_form": new_listing_form,
            "category_form": select_category_form
        })

# close a listing route and set winner
@login_required()
def close(request, listing_id):

    # if close button submitted from listing page by creator (button will only display for creator)
    if request.method == "POST":

        listing = Listing.objects.get(pk=listing_id)
        listing.status = 'Closed'
        listing.save()

        high_bidder = GetHighestBidder(listing_id)

        if high_bidder is not None:
            winner = f"The winner is {high_bidder}!"
        else:
            winner = "No one bid on this auction, so there is no winner!"
        
        ended_message = f"You ended this auction. {winner}"
        messages.add_message(request, messages.WARNING, ended_message)

        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

    # if reached by GET show error message on listing page
    else:
        error_message = f"You can't end an auction that you didn't create!"
        messages.add_message(request, messages.WARNING, error_message)
        return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))