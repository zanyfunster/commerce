from django.forms import ModelForm
from django import forms
from django.forms import ValidationError

from .models import Bid
from .util import GetListingBids

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = "__all__"
        widgets = {
            'item': forms.HiddenInput(),
            'bidder': forms.HiddenInput()
        }


    # this function will be used for the validation
    # https://www.geeksforgeeks.org/python-form-validation-using-django/
    def clean(self):
 
        # data from the form is fetched using super function
        super(BidForm, self).clean()
         
        # extract the bid amount
        amount = self.cleaned_data.get('amount')

        # extract the item listing info
        item = self.cleaned_data.get('item')
        listing_id = item.id

        # get high bid and reserve for this listing
        listing_bid = GetListingBids(listing_id)
        listing = listing_bid[0]
        price = listing_bid[1]
        reserve = listing.reserve

        if price == reserve and amount < reserve:
            raise ValidationError('Your bid must at least match reserve price')

        if amount < price:
            raise ValidationError('Your bid must be higher than current highest bid')

        # return any errors if found
        return self.cleaned_data