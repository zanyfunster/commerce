from .models import User, Listing, Bid, Comment

def GetListingBids(listing_id):
    listing = Listing.objects.get(pk=listing_id)

    # gets bids for listing_id and sorts from highest to lowest amount
    bids = Bid.objects.order_by('-amount').filter(item=listing_id)

    if len(bids) > 0:
        # gets current highest bid
        price = bids[0].amount
    else:
        price = listing.reserve

    # list stores listing, price and bids
    listing_bid = [listing, price, bids]

    return listing_bid