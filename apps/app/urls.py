#!/usr/bin/env python
from apps.app.views import *
from apps.app.processes import *

urlpatterns = [
    # Views
    
    # processes
    (r'/a/webhook/uninstall', DoUninstallApp),
]
