import typer
from datetime import datetime, timedelta
from ultralight_hiking import extract
from typing import Optional
import os

app = typer.Typer()


@app.command()
def main(
    user_agent: Optional[str]= typer.Argument(None),
    client_secret: Optional[str] = typer.Argument(None),
    client_id: Optional[str] = typer.Argument(None),
    after: datetime = typer.Option(
        datetime.today(), formats=["%Y-%m-%d", "%Y/%m/%d"]
    ),
    before: datetime = typer.Option(
        datetime.today() + timedelta(days=1), formats=["%Y-%m-%d", "%Y/%m/%d"]
    ),
    prefix: str = typer.Option(int(datetime.today().timestamp()))
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
    )
    if submissions_tr:
        reports, lp_contents = extract.extract_and_aggregate_submissions(submissions_tr)
        extract.write_jsonl(f"{prefix}-reports.jsonl", reports)
        extract.write_jsonl(f"{prefix}-lp_contents.jsonl", lp_contents)
    else:
        typer.echo("No submissions found.")


def run():
    app()
