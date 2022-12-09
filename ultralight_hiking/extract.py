import pandas as pd
from typing import Iterator, Dict, Tuple, List
from praw.models.reddit.submission import Submission
import numpy as np
from datetime import datetime, timedelta
from ultralight_hiking.parsing import serialize_lp_content
import praw

from psaw import PushshiftAPI
import json


def get_lighterpack_links(
    text: str, regex_str: str = "lighterpack\.com\/[\w\/]+"
) -> Iterator[str]:
    """Yield all lighterpack links found by `lp_regex` in `text`."""
    import re

    lp_regex = re.compile(regex_str)
    lp_links = np.unique(re.findall(lp_regex, text))
    for link in lp_links:
        yield f"https://{link}"


def extract_submission(submission: Submission) -> Tuple[Dict, List[Dict]]:
    lp_contents = [
        serialize_lp_content(link)
        for link in get_lighterpack_links(submission.selftext)
    ]
    submission_content = {
        "title": submission.title,
        "text": submission.selftext,
        "links": [cont["url"] for cont in lp_contents],
        "ts": str(datetime.fromtimestamp(submission.created)),
    }
    return submission_content, lp_contents


def extract_and_aggregate_submissions(
    submissions: List[Submission],
) -> Tuple[List[Dict], List[Dict]]:
    data = [extract_submission(submission) for submission in submissions]
    reports, lp_contents = list(zip(*data))
    return reports, [cnt for subl in lp_contents for cnt in subl]


def crawl_trip_reports(
    user_agent: str,
    client_secret: str,
    client_id: str,
    after: datetime | None = None,
    before: datetime | None = None,
    max_cache: int = 100,
) -> List[Submission]:
    r = praw.Reddit(
        user_agent=user_agent, client_secret=client_secret, client_id=client_id
    )
    if after is None:
        after = datetime.today()
    if before is None:
        before = datetime.today() + timedelta(days=1)
    api = PushshiftAPI(r)
    gen = api.search_submissions(
        title="trip report", subreddit="ultralight", after=int(after.timestamp()), before=int(before.timestamp())
    )
    submissions = []
    for c in gen:
        submissions.append(c)

        # Omit this test to actually return all results. Wouldn't recommend it though: could take a while, but you do you.
        if len(submissions) >= max_cache:
            break
    return submissions


def write_jsonl(filename: str, data) -> None:
    with open(filename, "w+") as fl:
        json.dump(data, fl)
