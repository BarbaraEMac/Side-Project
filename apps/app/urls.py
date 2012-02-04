#!/usr/bin/env python
from apps.app.views import *
from apps.app.processes import *

urlpatterns = [
    # Views
    (r'/a/shopify',   ShopifyRedirect),
    (r'/a/deleteApp', DoDeleteApp),
    
    # processes
    (r'/a/webhook/uninstalled/(.*)/', DoUninstalledApp),
    (r'/a/appClicksCounter',    AppClicksCounter),
]
