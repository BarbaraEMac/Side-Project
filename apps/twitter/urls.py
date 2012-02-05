#!/usr/bin/env python

from apps.twitter.views import *

urlpatterns = [
    # Views
    (r'/twitter', Twitter),
]

