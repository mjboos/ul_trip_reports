from ultralight_hiking import extract
import os
from typing import Iterator, Tuple
from datetime import datetime, timedelta
from praw.models.reddit.submission import Submission
from praw.reddit import Reddit

# TODO: robust error/retry handling


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


def get_daily_submissions(
    r: Reddit,
    after: datetime,
    before: datetime,
    subreddit: str = "ultralight",
    search_kw: str = "trip report",
) -> Iterator[Tuple[datetime, Iterator[Submission]]]:
    return group_submissions_by_day(
        extract.get_submissions(r, after, before, subreddit, search_kw, max_cache=None)
    )


if __name__ == "__main__":
    folder = "data"
    user_agent = os.environ.get("REDDIT_USER_AGENT")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    r = extract.praw.Reddit(
        user_agent=user_agent, client_secret=client_secret, client_id=client_id
    )
    start_date = datetime(2018, 12, 6)
    end_date = datetime(2020, 8, 26)

    for date, submissions in get_daily_submissions(r, start_date, end_date):
        date_str = date.strftime("%Y-%m-%d")
        print(f"Processing {date_str}")
        reports, lp_contents = extract.extract_and_aggregate_submissions(submissions)
        extract.write_jsonl(f"{folder}/{date_str}-reports.jsonl", reports)
        extract.write_jsonl(
            f"{folder}/{date_str}-lp_contents.jsonl", lp_contents
        )