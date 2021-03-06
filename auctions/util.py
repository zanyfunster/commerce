from .models import User, Listing, Bid, Comment

def GetListingBids(listing_id):
    listing = Listing.objects.get(pk=listing_id)

    # gets bids for listing_id and sorts from highest to lowest amount
    bids = Bid.objects.order_by('-amount').filter(item=listing_id)

    # if there are any existing bids
    if len(bids) > 0:
        # set price to current highest bid
        price = listing.current_price
    # if no bids yet, set price to reserve
    else:
        price = listing.reserve

    # list stores listing, price and bids
    listing_bid = [listing, price, bids]

    return listing_bid

def GetHighestBidder(listing_id):

    # gets bids for listing_id and sorts from highest to lowest amount
    bids = Bid.objects.order_by('-amount').filter(item=listing_id)

    if len(bids) > 0:
        # if there are bids, return highest bidder
        high_bidder = bids[0].bidder
    else:
        high_bidder = None
    
    return high_bidder

# capitalize words in a title
def CapitalizeTitle(title):

    words = title.split(" ")
    capitalized_words = []
    for word in words:
        capitalized_words.append(word.capitalize())
    title = " ".join(capitalized_words)
    return title