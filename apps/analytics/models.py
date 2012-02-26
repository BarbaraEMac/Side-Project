#!/usr/bin/env python
import logging

from google.appengine.ext   import db

from util.consts            import URL
from util.helpers           import generate_uuid

# ------------------------------------------------------------------------------
# Analytics Class Definition ---------------------------------------------------
# ------------------------------------------------------------------------------
class Analytics_PastWeek(db.Model):
   # Datetime when this model was put into the DB
    created  = db.DateTimeProperty( required= True, auto_now_add=True, indexed=False )

    # Shopify Store
    store    = db.ReferenceProperty( db.Model, required=True, indexed=True, collection_name='pastweekanalytics' )
    
    app_     = db.StringProperty( required=True, indexed=True )

    # Count for that week
    count    = db.IntegerProperty( required=True, default=0, indexed=False )

    # Top 3 products for that week
    products = db.StringListProperty( indexed=False )

    def __init__(self, *args, **kwargs):
        super(Analytics_PastWeek, self).__init__(*args, **kwargs)

    @staticmethod
    def create( store, app, new_count, prods ):
        pw = Analytics_LastWeek( store = store, app_ = app, count = 0, products = prods )
        pw.put()

# ------------------------------------------------------------------------------
# Analytics Class Definition ---------------------------------------------------
# ------------------------------------------------------------------------------
class Analytics_ThisWeek(db.Model):
    # Shopify Store
    store       = db.ReferenceProperty( db.Model, required=True, indexed=True, collection_name='thisweekanalytics' )
    
    product_url = db.StringProperty( required=True, indexed=True )

    app_        = db.StringProperty( required=True, indexed=True )

    def __init__(self, *args, **kwargs):
        super(Analytics_ThisWeek, self).__init__(*args, **kwargs)

    def create( store, app, url ):
        tw = Analytics_ThisWeek( store = store, app_ = app, product_url = url )
        
        tw.put()

    @staticmethod
    def get_weekly_count( store, app ):
        tw = Analytics_ThisWeek.all().filter('store =', store).filter( 'app_ =', app )

        # Get top 5 most shared products + counts
        sort = sorted(tw, key=lambda t: t.get_clicks_count() )
        urls = counts = []
        for i in range(0, 5):
            # parallel lists
            urls   += sort.product_url
            counts += sort.get_clicks_count()
        
        # Now, delete all counters and ThisWeek's Analytics points
        for t in tw:
            tw.clear_clicks() # clear counters
            tw.delete()

        return urls, counts

    @staticmethod
    def add_new( store, app, url ):
        tw = Analytics_ThisWeek.all().filter('store = ', store )\
                                     .filter( 'app_ = ', app )\
                                     .filter( 'product_url = ', url ).get()

        if tw is None:
            tw = Analytics_ThisWeek.create( store, app, url )

        tw.increment_clicks()

    def get_clicks_count(self):
        """Count this apps sharded clicks"""
        total = memcache.get(self.uuid+"AnalyticsClickCounter")
        if total is None:
            total = 0
            for counter in AnalyticsClickCounter.all().\
            filter('app_uuid =', self.uuid).fetch(NUM_CLICK_SHARDS):
                total += counter.count
            memcache.add(key=self.uuid+"AnalyticsClickCounter", value=total)
        return total
    
    def add_clicks(self, num):
        """add num clicks to this App's click counter"""
        def txn():
            index = random.randint(0, NUM_CLICK_SHARDS-1)
            shard_name = self.uuid + str(index)
            counter = AnalyticsClickCounter.get_by_key_name(shard_name)
            if counter is None:
                counter = AnalyticsClickCounter( key_name = shard_name, 
                                                 app_uuid = self.uuid )
            counter.count += num
            counter.put()

        db.run_in_transaction(txn)
        memcache.incr(self.uuid+"AnalyticsClickCounter")

    def increment_clicks(self):
        """Increment this link's click counter"""
        self.add_clicks(1)

    def clear_clicks( self ):
        memcache.add(key=self.uuid+"AnalyticsClickCounter", value=0)

        for i in range( 0, NUM_CLICK_SHARDS ):
            shard_name = self.uuid + str(i)
            counter = AnalyticsClickCounter.get_by_key_name(shard_name)
            if counter:
                counter.count = 0;
                counter.put()

## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
class AnalyticsClickCounter(db.Model):
    """Sharded counter for clicks"""

    analytics_uuid = db.StringProperty (indexed=True, required=True)
    count          = db.IntegerProperty(indexed=False, required=True, default=0)





