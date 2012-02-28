#!/usr/bin/env python

#from apps.homepage.processes import *
from apps.homepage.views      import *

urlpatterns = [
    # The 'Shows' (aka GET)
    (r'/more',           ShowMorePage),

    (r'/()',             ShowLandingPage) # Must be last
]
