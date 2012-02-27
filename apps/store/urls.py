#!/usr/bin/env python

from apps.store.processes import *
from apps.store.views     import *

urlpatterns = [
    # Views
    (r'/store/select',              StoreAppSelect),
    (r'/store/billing_callback',    StoreBillingCallback),
    (r'/store/billingcancelled',    StoreBillingCancelled),
    (r'/store/welcome',             StoreWelcome),

    # Processes
    (r'/store/biller',              StoreBiller),
    (r'/store/click',               StoreClick),
    (r'/store/setup',               StoreSetup)
]
