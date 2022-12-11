from ultralight_hiking import extract
import os
from typing import Iterator, Tuple
from datetime import datetime, timedelta
from psaw import PushshiftAPI
from praw.models.reddit.submission import Submission

# TODO: robust error/retry handling


def daily_submissions_iterator(
    start_date: datetime, end_date: datetime, api: PushshiftAPI
) -> Iterator[Tuple[datetime, list[Submission]]]:
    curr_day = start_date
    while curr_day < end_date:
        next_day = curr_day + timedelta(days=1)
        submissions = list(
            extract.get_submissions(
                api,
                after=int(curr_day.timestamp()),
                before=int(next_day.timestamp()),
                subreddit="ultralight",
                search_kw="trip report",
                max_cache=100,
            )
        )
        if submissions:
            yield curr_day, submissions

        curr_day = next_day


if __name__ == "__main__":
    user_agent = os.environ.get("REDDIT_USER_AGENT")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    r = extract.praw.Reddit(
        user_agent=user_agent, client_secret=client_secret, client_id=client_id
    )
    api = PushshiftAPI(r)
    start_date = datetime(2010, 12, 6)
    end_date = datetime(2022, 1, 1)
    for date, submissions in daily_submissions_iterator(start_date, end_date, api):
        reports, lp_contents = extract.extract_and_aggregate_submissions(submissions)
        extract.write_jsonl(f"{date.strftime('%Y-%m-%d')}-reports.jsonl", reports)
        extract.write_jsonl(
            f"{date.strftime('%Y-%m-%d')}-lp_contents.jsonl", lp_contents
        )
