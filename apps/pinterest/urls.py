#!/usr/bin/env python

from apps.pinterest.processes import *
from apps.pinterest.views import *

urlpatterns = [
    # Views
    (r'/pinterest',                     Pinterest),
    (r'/pinterest/biller',              PinterestBiller),
    (r'/pinterest/billing_callback',    PinterestBillingCallback),
    (r'/pinterest/billingcancelled',    PinterestBillingCancelled),
    (r'/pinterest/welcome',             PinterestWelcome),

    # Processes
    (r'/pinterest/click',               PinterestClick),

]

