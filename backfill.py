from ultralight_hiking import extract
import os
from typing import Iterator, Tuple
from datetime import datetime, timedelta
from praw.models.reddit.submission import Submission
from praw.reddit import Reddit

# TODO: robust error/retry handling


if __name__ == "__main__":
    folder = "data"
    user_agent = os.environ.get("REDDIT_USER_AGENT", "empty")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "empty")
    client_id = os.environ.get("REDDIT_CLIENT_ID", "empty")
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2018, 12, 6)

    for date, submissions in extract.group_submissions_by_day(
        extract.crawl_trip_reports(
            user_agent=user_agent,
            client_id=client_id,
            client_secret=client_secret,
            after=start_date,
            before=end_date,
            max_cache=None,
        )
    ):
        date_str = date.strftime("%Y-%m-%d")
        print(f"Processing {date_str}")
        reports, lp_contents = extract.extract_and_aggregate_submissions(submissions)
        extract.write_jsonl(f"{folder}/{date_str}-reports.jsonl", reports)
        extract.write_jsonl(f"{folder}/{date_str}-lp_contents.jsonl", lp_contents)
