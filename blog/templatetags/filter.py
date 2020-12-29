import hashlib
import urllib
import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import linebreaks
import markdown
 
register = template.Library()
 
# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=40):
  default = "https://bulma.io/images/placeholders/128x128.png"
  return "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(email.encode("utf-8").lower()).hexdigest(), urllib.parse.urlencode({'d':default, 's':str(size)}))
 
# return an image tag with the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def gravatar(email, size=40):
    url = gravatar_url(email, size)
    return mark_safe('<img src="%s" height="%d" width="%d">' % (url, size, size))

# -----------------------------------------------------------------------------------

@register.filter(name='markdown')
def markdown_filter(text):
  return mark_safe(markdown.markdown(text))