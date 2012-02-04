#!/usr/bin/python

# consts.py
# constants for referrals

import os
import logging

from urlparse import urlunsplit

# Domain Stuff
USING_DEV_SERVER    = True if 'Development' in os.environ.get('SERVER_SOFTWARE', "") else False
PROTOCOL            = 'http' 
SECURE_PROTOCOL     = 'https'
APP_DOMAIN          = 'None' if USING_DEV_SERVER else 'appsy-daisy.appspot.com'
DOMAIN              = os.environ['HTTP_HOST'] if USING_DEV_SERVER else APP_DOMAIN 
URL                 = urlunsplit((PROTOCOL, DOMAIN, '', '', '')) 
SECURE_URL          = urlunsplit((SECURE_PROTOCOL, DOMAIN, '', '', '')) 
KEYS                = os.environ['HTTP_HOST']

# Our BS P3P Header
P3P_HEADER = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'

# LilCookies (secure cookies) Stuff
COOKIE_SECRET = 'f54eb793d727492e99601446aa9b06bab504c3d37bc54c8391f385f0dde03732'

SHOPIFY_APPS = {
    'Pinterest': {
        'api_key': '',
        'api_secret': '',
        'class_name': 'Pinterest',
    }
}

# List of root template directories
# to import templates from
TEMPLATE_DIRS = (
    'apps/homepage/templates',        
)

# the apps we are using
INSTALLED_APPS = [
    'admin',
    'app',
    'email',
    'gae_bingo',
    'gae_bingo.tests',
    'homepage',
    'pinterest',
    'store',
]

# Overide settings with local_consts
#try:
#    from local_consts import *
#except Exception, e:
#    logging.info('no local_consts.py: %s' % e, exc_info=True)
#    pass

