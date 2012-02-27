#!/usr/bin/env python

import logging

from django.utils           import simplejson as json
from google.appengine.api import taskqueue
from google.appengine.ext   import webapp
from google.appengine.ext   import db
from mapreduce              import control
from mapreduce              import operation as op

from apps.analytics.models  import *
from apps.email.models      import Email

class QueueWeeklyAnalytics( webapp.RequestHandler ):
    def post(self):
        return self.get( )

    def get(self):
        store = ShopifyStore.get_by_uuid( self.request.get('uuid') )
        
        logging.info("Starting weekly")
        if store.pinterest_enabled:
            # Grab total # clicks
            pinterest_total_clicks = 0

            # Grab top urls and counts
            pinterest_urls, pinterest_counts = Analytics_ThisWeek.get_weekly_count( store, 'pinterest' )

            # Store this week's data
            Analytics_PastWeek.create( store, 'pinterest', pinterest_total_clicks, pinterest_urls[:3])
        
        if store.pinterest_enabled:
            # Grab total # clicks
            pinterest_total_clicks = 0

            # Grab top urls and counts
            pinterest_urls, pinterest_counts = Analytics_ThisWeek.get_weekly_count( store, 'pinterest' )

            # Store this week's data
            Analytics_PastWeek.create( store, 'pinterest', pinterest_total_clicks, pinterest_urls[:3])

        # Send out email
        Email.weeklyAnalytics( store.email, 
                               store.full_name, 
                               pinterest_total_clicks,
                               pinterest_urls,
                               pinterest_counts )

class CronWeeklyAnalytics( webapp.RequestHandler ):
    """ Funnily enough, sometimes GET or POST is called. 
        Thanks for being consistent, mapreduce. """

    def post(self):
        return self.get( )

    def get(self):
        stores = ShopifyStore.all()
        for s in stores:
            taskqueue.add( queue_name = 'analytics', 
                           url        = '/analytics/queue/weekly',
                           params     = {'uuid' : s.uuid} )

        """
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
        """
