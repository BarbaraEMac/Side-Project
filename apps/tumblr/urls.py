#!/usr/bin/env python

from apps.tumblr.views import *

urlpatterns = [
    # Views
    (r'/tumblr', Tumblr),
]

