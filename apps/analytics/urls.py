#!/usr/bin/env python

from apps.analytics.processes import *
from apps.analytics.views import *

urlpatterns = [
    # Views

    # Processes
    (r'/analytics/cron/weekly',            CronWeeklyAnalytics),
    (r'/analytics/queue/weekly',           QueueWeeklyAnalytics),

]

