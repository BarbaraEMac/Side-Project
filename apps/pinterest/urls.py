#!/usr/bin/env python

from apps.pinterest.processes import *
from apps.pinterest.views import *

urlpatterns = [
    # Views
    (r'/pinterest',             Pinterest),
    (r'/p/biller',              PinterestBiller),
    (r'/p/billing_callback',    PinterestBillingCallback),
    (r'/p/billingcancelled',    PinterestBillingCancelled),
    (r'/p/welcome',             PinterestWelcome),
    (r'/p/click',               PinterestClick),

]

