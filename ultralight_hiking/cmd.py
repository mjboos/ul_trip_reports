import typer
from datetime import datetime, timedelta
from ultralight_hiking import extract
from typing import Optional, Tuple
from praw.models.reddit.submission import Submission
import os
from pathlib import Path

app = typer.Typer()

# TODO: make folders and sort


def create_file_path(date: datetime, filename: str, data_path: str = "data") -> Path:
    date_str = date.strftime("%Y-%m-%d")
    path = Path(data_path) / str(date.year) / str(date.month) / str(date.day)
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{date_str}-{filename}"


def process_submissions_list(
    date: datetime, list_of_submissions: list[Submission], data_path: str = "data"
) -> Tuple[Path, Path]:
    reports, lp_contents = extract.extract_and_aggregate_submissions(
        list_of_submissions
    )
    report_path, lp_path = create_file_path(
        date, "-reports.jsonl", data_path
    ), create_file_path(date, "-lp_contents.jsonl", data_path)
    extract.write_jsonl(report_path, reports)
    extract.write_jsonl(lp_path, lp_contents)
    return report_path, lp_path


def create_files_for_upload(
    submissions_tr: list[Submission],
    backfill: bool = False,
    prefix: datetime = datetime.today(),
    data_path: str = "data",
) -> list[Path]:
    paths = []
    if backfill:
        for date, submissions in extract.group_submissions_by_day(submissions_tr):
            paths.append(process_submissions_list(date, submissions, data_path))
    else:
        paths.append(process_submissions_list(prefix, submissions_tr, data_path))
    return [pp for p in paths for pp in p]


@app.command()
def main(
    user_agent: Optional[str] = typer.Argument(None),
    client_secret: Optional[str] = typer.Argument(None),
    client_id: Optional[str] = typer.Argument(None),
    after: datetime = typer.Option(datetime.now() - timedelta(hours=24)),
    before: datetime = typer.Option(datetime.now()),
    prefix: datetime = typer.Option(datetime.today()),
    max_cache: Optional[int] = typer.Option(None),
    backfill: bool = typer.Option(False),
):
    if user_agent is None:
        user_agent = os.environ.get("REDDIT_USER_AGENT")
        if user_agent is None:
            raise ValueError(
                "Please provide a user agent or set `REDDIT_USER_AGENT` environment variable."
            )
    if client_secret is None:
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
        if client_secret is None:
            raise ValueError(
                "Please provide a client secret or set `REDDIT_CLIENT_SECRET` environment variable."
            )
    if client_id is None:
        client_id = os.environ.get("REDDIT_CLIENT_ID")
        if client_id is None:
            raise ValueError(
                "Please provide a client id or set `REDDIT_CLIENT_ID` environment variable."
            )
    submissions_tr = extract.crawl_trip_reports(
        user_agent=user_agent,
        client_id=client_id,
        client_secret=client_secret,
        after=after,
        before=before,
        max_cache=max_cache,
    )
    if submissions_tr:
        files = create_files_for_upload(submissions_tr, backfill, prefix)
    else:
        typer.echo("No submissions found.")


def run():
    app()
