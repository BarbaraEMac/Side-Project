#!/usr/bin/env python

from apps.feedback.processes import *
from apps.feedback.views import *

urlpatterns = [
    # Views
    (r'/feedback',      Feedback),
    # Processes
    (r'/feedback/post', FeedbackPost),
]

