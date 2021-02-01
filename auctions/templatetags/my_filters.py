from django import template
from django.contrib.humanize.templatetags.humanize import intcomma


# create filter for displaying currency with dollar signs and commas in templates
# https://stackoverflow.com/questions/346467/format-numbers-in-django-templates

register = template.Library()

def currency(dollars):
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

register.filter('currency', currency)