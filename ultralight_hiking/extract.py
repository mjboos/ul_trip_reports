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
    after: int,
    before: int,
    subreddit: str = "ultralight",
    search_kw: str = "trip report",
    max_cache: int | None = 100,
    time_filter: str = "all",
) -> Iterator[Submission]:
    gen = reddit_obj.subreddit(subreddit).search(
        search_kw, limit=None, time_filter=time_filter
    )
    for i, c in enumerate(gen):
        if after < c.created_utc < before:
            yield c
        if max_cache and i >= max_cache:
            break


def crawl_trip_reports(
    user_agent: str,
    client_secret: str,
    client_id: str,
    after: datetime | None | int = None,
    before: datetime | None | int = None,
    max_cache: int | None = 100,
    time_filter: str = "all",
) -> Iterator[Submission]:
    reddit = praw.Reddit(
        user_agent=user_agent, client_secret=client_secret, client_id=client_id
    )
    if after is None:
        after = datetime.now() - timedelta(hours=24)
        if before is None:
            # limit time_filter
            time_filter = "day"
    if isinstance(after, datetime):
        after = int(after.timestamp())
    if before is None:
        before = datetime.now()
    if isinstance(before, datetime):
        before = int(before.timestamp())
    return get_submissions(
        reddit,
        after,
        before,
        subreddit="ultralight",
        search_kw="trip report",
        max_cache=max_cache,
        time_filter=time_filter,
    )


def write_jsonl(filename: str, data) -> None:
    with open(filename, "w+") as fl:
        json.dump(data, fl)


def group_submissions_by_day(
    submissions: Iterator[Submission],
) -> Iterator[Tuple[datetime, Iterator[Submission]]]:
    from collections import defaultdict

    submissions_by_day = defaultdict(list)

    for submission in submissions:
        submissions_by_day[
            datetime.fromtimestamp(submission.created_utc).date()
        ].append(submission)
    for day, submissions in submissions_by_day.items():
        yield day, submissions
