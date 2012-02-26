#!/usr/bin/env python

import logging
from urlparse              import urlparse

from apps.store.models     import ShopifyStore

from util.consts     import URL
from util.helpers    import url
from util.shopify    import ShopifyAPI
from util.shopify_helpers import get_shopify_url
from util.urihandler import URIHandler


