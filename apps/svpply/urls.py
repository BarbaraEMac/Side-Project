#!/usr/bin/env python

from apps.svpply.views import *

urlpatterns = [
    # Views
    (r'/s', Svpply),
]

