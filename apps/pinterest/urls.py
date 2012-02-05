#!/usr/bin/env python

from apps.pinterest.processes import *
from apps.pinterest.views import *

urlpatterns = [
    # Views
    (r'/p',                     Pinterest),
    (r'/p/biller',              PinterestBiller),
    (r'/p/billing_callback',    PinterestBillingCallback),
    (r'/p/welcome',             PinterestWelcome),
]

