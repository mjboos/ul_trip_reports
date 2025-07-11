# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --group dev
```

### Running the Application
```bash
# Run the main scraper command
uv run ul-scraper

# Run with environment variables
REDDIT_USER_AGENT="your-agent" REDDIT_CLIENT_SECRET="secret" REDDIT_CLIENT_ID="id" uv run ul-scraper

# Run backfill script
uv run python backfill.py
```

### Testing
```bash
# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_ultralight_hiking.py
```

### Code Quality
```bash
# Type checking
uv run mypy ultralight_hiking/

# Code formatting
uv run black ultralight_hiking/ tests/

# Linting (not explicitly configured, but mypy serves as static analysis)
uv run mypy ultralight_hiking/
```

## Architecture

This is a Python project that scrapes ultralight hiking trip reports from Reddit and extracts lighterpack.com gear lists. The architecture consists of:

### Core Components

1. **extract.py** - Main extraction logic
   - `crawl_trip_reports()` - Scrapes Reddit using PRAW API
   - `extract_submission()` - Processes individual Reddit posts
   - `get_lighterpack_links()` - Finds lighterpack URLs in post text
   - `group_submissions_by_day()` - Groups submissions by date for backfill

2. **parsing.py** - Lighterpack content parsing
   - `parse_item()` - Extracts individual gear items from HTML
   - `parse_category()` - Processes gear categories
   - `extract_lp_categories()` - Scrapes full lighterpack lists using BeautifulSoup
   - `serialize_lp_content()` - Converts parsed data to JSON format

3. **cmd.py** - CLI interface using Typer
   - Main entry point with argument parsing
   - Handles Reddit API credentials via environment variables or arguments
   - Supports date range filtering and backfill mode

4. **trip_reports.py** - Data models (currently contains placeholder TripReport dataclass)

### Data Flow

1. Reddit API authentication using PRAW
2. Search for "trip report" posts in r/ultralight subreddit
3. Extract text content and find lighterpack.com links
4. Scrape lighterpack pages for gear lists
5. Output structured data as JSONL files organized by date

### Environment Variables

Required for Reddit API access:
- `REDDIT_USER_AGENT` - User agent string for Reddit API
- `REDDIT_CLIENT_SECRET` - OAuth client secret
- `REDDIT_CLIENT_ID` - OAuth client ID

### Output Structure

Data is saved to `data/` directory with date-based organization:
- `YYYY-MM-DD-reports.jsonl` - Trip report metadata
- `YYYY-MM-DD-lp_contents.jsonl` - Lighterpack gear data

The backfill script processes historical data from 2015-2018 by default.