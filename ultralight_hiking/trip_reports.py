from dataclasses import dataclass, fields, asdict
import pandas as pd
from typing import Optional
from praw.models.reddit.submission import Submission
import numpy as np
from .parsing import get_lp_items
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
    lp_link = get_lighterpack_link(submission.selftext)
    if lp_link:
        lp_items = get_lp_items(lp_link)
    else:
        lp_items = None
    return TripReport(
        submission.title,
        submission.selftext,
        lp_link,
        lp_items,
        datetime.fromtimestamp(submission.created),
    )


def get_lighterpack_link(
    text: str, regex_str: str = "lighterpack\.com\/[\w\/]+"
) -> Optional[str]:
    """Returns the first lighterpack link found by `lp_regex` in `text`."""
    import re

    lp_regex = re.compile(regex_str)
    lp_links = np.unique(re.findall(lp_regex, text))
    return "https://" + lp_links[0] if len(lp_links) > 0 else None
