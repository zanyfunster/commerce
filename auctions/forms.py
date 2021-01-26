from django.forms import ModelForm
from django import forms
from django.forms import ValidationError
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import URLError
from urllib.parse import quote_plus, urlparse
import requests

from .models import Bid, Listing, PetType
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
            'status': forms.HiddenInput(),
            'reserve': forms.NumberInput(attrs={'min': 0.00, 'step': 0.01})
        }

    # image URL validation
    def clean_imageURL(self):

        # this method returns true if a url links to an image
        # by checking headers for 'image' in the content type    
        def image_checker(url):

            # get dictionary of request headers with request
            request = requests.get(url)
            headers = request.headers

            # and get response headers from urlretrieve
            response = urlretrieve(url)
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
                    return False
                else:
                    return True

        # if image URL provided, check that it links to an image
        if self.cleaned_data.get('imageURL') is not None:
            
            try:
                url = self.cleaned_data['imageURL']
                image_found = image_checker(url)
                if image_found == False:
                    self.add_error('imageURL', 'URL does not link to an image. Try a different link.')
            except:
                self.add_error('imageURL', 'Invalid URL. Try a different link.')
       
            # return error messages or image URL
            return url

        else:        
            # return imageURL 
            return None

class SelectPetTypeForm(forms.ModelForm):
    class Meta:
        model = PetType
        fields = ['pet_type']
        labels = {
            'pet_type': 'Pet Type'
        }
