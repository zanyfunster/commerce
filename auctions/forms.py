from django.forms import ModelForm
from django import forms
from django.forms import ValidationError
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import URLError
from urllib.parse import quote_plus, urlparse
import requests

from .models import Bid, Listing
from .util import GetListingBids

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = '__all__'
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

        bidder = self.cleaned_data.get('bidder')

        # extract the item listing info
        listing = self.cleaned_data.get('item')
        listing_id = listing.id

        # get high bid and reserve for this listing
        listing_bid = GetListingBids(listing_id)
        listing = listing_bid[0]
        price = listing_bid[1]
        reserve = listing.reserve

        # return validation errors if bid amount is lower than reserve price or current high bid
        if price == reserve and amount < reserve:
            raise ValidationError('Your bid must at least match reserve price!')

        if amount <= price:
            raise ValidationError('Your bid must be higher than current highest bid!')

        # return any errors if found
        return self.cleaned_data


class AddListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['bidders']
        labels = {
            'reserve': 'Reserve Price',
            'imageURL': 'Link to image'
        }
        widgets = {
            'creator': forms.HiddenInput(),
            'status': forms.HiddenInput()
        }
        
    # this function will be used for the validation
    # https://www.geeksforgeeks.org/python-form-validation-using-django/
    def clean(self):
 
        # data from the form is fetched using super function
        super(AddListingForm, self).clean()
         
        # get image URL
        imageURL = self.cleaned_data.get('imageURL')

        if imageURL is None:
            raise ValidationError('Invalid image URL. Try a different link.')
        
        # URL validation from https://docs.python.org/3/howto/urllib2.html#number-2
        req = Request(imageURL)
        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                raise ValidationError('Invalid image URL. Try a different link.')
            elif hasattr(e, 'code'):
                raise ValidationError('Invalid image URL. Try a different link.')

        # check that url links to an image
        request = requests.get(imageURL)
        # get dictionary of headers
        headers = request.headers

        # now check for image in response using urlretrieve, in case of sites like squarespace
        response = urlretrieve(imageURL)
        response_headers = response[1]

        # merge two headers dictionaries
        headers.update(response_headers)
        
        # if 'content-type' is in headers, then get value for that key
        content_key = 'content-type'
        if content_key in headers:
            content_type = headers[content_key]
            # check if content_type contains 'image'
            img_results = content_type.find('image')
            # if  'image' is not found in string, find method will return -1
            if img_results == -1:
                raise ValidationError('Image URL does not display an image. Try a different link.')

        # now check that reserve price is greater than 0
        reserve = self.cleaned_data.get('reserve')

        if reserve <= 0:
            raise ValidationError('You must set a reserve price higher than $0!')

        # return any errors if found
        return self.cleaned_data
