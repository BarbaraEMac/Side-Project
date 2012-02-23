#!/usr/bin/env python

import logging

from django.utils           import simplejson as json
from google.appengine.ext   import webapp
from google.appengine.ext   import db
from mapreduce              import control
from mapreduce              import operation as op

from apps.analytics.models  import *
from apps.app.models        import App
from apps.pinterest.models  import Pinterest
from apps.email.models      import Email

def weekly_analytics( app ):
    logging.info("Starting weekly")
    # Grab total # clicks
    total_clicks = app.get_weekly_count()
    logging.info('1')

    # Grab top urls and counts
    urls, counts = Analytics_ThisWeek.get_weekly_count( app )
    logging.info('2')

    # Store this week's data
    Analytics_PastWeek.create(app, total_clicks, urls[:3])
    logging.info('3')

    # Send out email
    Email.weeklyAnalytics( app.store.email, 
                           app.store.full_name, 
                           total_clicks,
                           urls,
                           counts )
    logging.info('4')

class RunWeeklyAnalytics( webapp.RequestHandler ):
    """ Funnily enough, sometimes GET or POST is called. 
        Thanks for being consistent, mapreduce. """

    def post(self):
        return self.get( )

    def get(self):
        e_base = 'apps.analytics.models.%s'
        f_base = 'apps.analytics.processes.%s'
        
        opts =  {
            'name': 'Compute Weekly Analytics',
            'func': f_base % 'weekly_analytics',
            'entity': 'apps.app.models.App',
            'reader': 'mapreduce.input_readers.DatastoreInputReader'
        } 
        
        mapreduce_parameters = {}
        mapreduce_id = control.start_map(
            opts['name'],
            opts['func'],
            opts['reader'], {
                'entity_kind': opts['entity'],
                'batch_size': 25
            },
            mapreduce_parameters = mapreduce_parameters,
            shard_count=20
        )
        data = {'success': True, 'mapreduce_id': mapreduce_id}
        self.response.out.write(json.dumps(data))
