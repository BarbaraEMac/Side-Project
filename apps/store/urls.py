#!/usr/bin/env python

from apps.store.processes import *
from apps.store.views     import *

urlpatterns = [
    # Views
    (r'/store/select',              StoreAppSelect),
    (r'/store/billing_callback',    StoreRecurringCallback),
    (r'/store/billingcancelled',    StoreRecurringCancelled),
    (r'/store/onetime_callback',    StoreOneTimeCallback),
    (r'/store/onetimecancelled',    StoreOneTimeCancelled),
    (r'/store/support',             StoreSupport),
    (r'/store/welcome',             StoreWelcome),

    # Processes
    (r'/store/biller',              StoreBiller),
    (r'/store/click',               StoreClick),
    (r'/store/onetime',             StoreOneTime),
    (r'/store/setup',               StoreSetup),
    (r'/store/uninstall',           StoreUninstall),
]
