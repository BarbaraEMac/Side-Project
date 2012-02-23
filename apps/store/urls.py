#!/usr/bin/env python

from apps.store.processes import *
from apps.store.views     import *

urlpatterns = [
    # Views
    (r'/biller',              Biller),
    (r'/billing_callback',    BillingCallback),
    (r'/billingcancelled',    BillingCancelled),
    (r'/welcome',             Welcome),

    # Processes
    (r'/click',               Click)
]
