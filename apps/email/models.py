#!/usr/bin/env python
""" 
Name: Email Class
Purpose: All emails will be in this class.
Author:  Barbara Macdonald
Date:  March 2011
"""
import logging
import os
import urllib, urllib2

from django.utils import simplejson as json
from google.appengine.api import urlfetch
from google.appengine.api.mail import EmailMessage
from google.appengine.ext.webapp import template

from util.consts import *

###################
#### Addresses ####
###################

barbara = 'z4beth@gmail.com'

info = barbara

from_addr = barbara

#####################
#### Email Class ####
#####################
class Email():

#### Dev Team Emails ####
    @staticmethod
    def emailBarbara(msg):
        to_addr = barbara
        subject = '[Appsy]'
        body    = '<p> %s </p>' % msg
 
        logging.info("Emailing Barbara")
        Email.send_email(from_addr, to_addr, subject, body)

    @staticmethod
    def goodbye( to_addr, name ):
        to_addr = to_addr
        subject = 'Sad to say goodbye'
    
        # Grab first name only
        try:
            name = name.split(' ')[0]
        except:
            pass

        body = """<p>Hiya %s,</p><p>I saw that you just uninstalled my Shopify App.
        Sorry things didn't work out for you.</p><p>I'd loe to know why you uninstalled
        so I can improve the app for future customers.</p><p>Thanks, Kurtis</p>""" % name
        
        Email.send_email(from_addr, to_addr, subject, body)

    @staticmethod
    def welcomeClient( app_name, to_addr, name, store_name ):
        to_addr = to_addr
        subject = 'Thanks!'
    
        # Grab first name only
        try:
            name = name.split(' ')[0]
        except:
            pass

        body = """<p>Hi %s,</p><p>Just wanted to drop you a line and say thanks for
        installing my Shopify App.</p><p>If you have any comments or questions, please
        email me!</p><p>--Kurtis</p>""" % name
        
        Email.send_email(from_addr, to_addr, subject, body)

    @staticmethod 
    def template_path(path):
        return os.path.join('apps/email/templates/', path)

    @staticmethod
    def send_email(from_address, to_address, subject, body):
        try:
            e = EmailMessage(
                    sender=from_address, 
                    to=to_address, 
                    subject=subject, 
                    html=body
                    )
            e.send()
        except Exception,e:
            logging.error('error sending email: %s', e)
# end class

