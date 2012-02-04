#!/usr/bin/python

# consts.py
# constants for referrals

import os
import logging

from urlparse import urlunsplit

USING_DEV_SERVER    = True if 'Development' in os.environ.get('SERVER_SOFTWARE', "") else False
PROTOCOL            = 'http' 
SECURE_PROTOCOL     = 'https'
APP_DOMAIN          = 'None' if USING_DEV_SERVER else 'appsy-daisy.appspot.com'
DOMAIN              = os.environ['HTTP_HOST'] if USING_DEV_SERVER else APP_DOMAIN 
SECURE_URL          = urlunsplit((SECURE_PROTOCOL, DOMAIN, '', '', '')) 
URL                 = urlunsplit((PROTOCOL, DOMAIN, '', '', '')) 


