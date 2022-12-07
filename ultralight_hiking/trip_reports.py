from dataclasses import dataclass, fields, asdict
import pandas as pd
from typing import Optional, Iterator, Dict
from praw.models.reddit.submission import Submission
import numpy as np
from datetime import datetime

@dataclass(frozen=True)
class TripReport:
    title: str
    text: str
    lighterpack_link: Optional[str]
    lp_items: Optional[pd.DataFrame]
    created_date: datetime


def get_trip_report(submission: Submission) -> TripReport:
    """Creates a TripReport object from submission"""
    pass
#    lp_link = next(get_lighterpack_links(submission.selftext))
#    if lp_link:
##        lp_items = get_lp_items(lp_link)
#        pass
#    else:
#        lp_items = None
#    return TripReport(
#        submission.title,
#        submission.selftext,
#        lp_link,
#        lp_items,
#        datetime.fromtimestamp(submission.created),
#    )

