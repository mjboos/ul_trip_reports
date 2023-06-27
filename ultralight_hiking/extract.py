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


# TODO: get all submissions (not only kw)
def get_submissions(
    reddit_obj: praw.reddit.Reddit,
    after: datetime,
    before: datetime,
    subreddit: str = "ultralight",
    search_kw: str = "trip report",
    max_cache: int = 100,
) -> Iterator[Submission]:
    gen = reddit_obj.subreddit(subreddit).search(search_kw, limit=None)
    for i, c in enumerate(gen):
        if after < pd.to_datetime(c.created_utc, unit="s") < before:
            yield c
        if i >= max_cache:
            break


def crawl_trip_reports(
    user_agent: str,
    client_secret: str,
    client_id: str,
    after: datetime | None | int = None,
    before: datetime | None | int = None,
    max_cache: int = 100,
) -> List[Submission]:
    r = praw.Reddit(
        user_agent=user_agent, client_secret=client_secret, client_id=client_id
    )
    if after is None:
        after = datetime.today()
    if isinstance(after, datetime):
        after = int(after.timestamp())
    if before is None:
        before = datetime.today() + timedelta(days=1)
    if isinstance(before, datetime):
        before = int(before.timestamp())
    api = PushshiftAPI(r)
    submissions = list(
        get_submissions(
            api,
            after,
            before,
            subreddit="ultralight",
            search_kw="trip report",
            max_cache=max_cache,
        )
    )
    return submissions


def write_jsonl(filename: str, data) -> None:
    with open(filename, "w+") as fl:
        json.dump(data, fl)
