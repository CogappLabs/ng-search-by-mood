import os
import time

import requests
from dotenv import load_dotenv

# loads NG_API_USER/NG_API_PASS/NG_API_BASE from a local .env file if one
# exists (see .env.example) - .env is gitignored, so real credentials never
# end up in source control or the public repo
load_dotenv()

# this is a public URL, not a secret, so a default is fine here
API_BASE = os.environ.get("NG_API_BASE", "https://ng-hack-apps.cogapp.workers.dev/api")
# no defaults for these two - they're the API's HTTP basic auth credentials,
# and must come from the environment (or a local, gitignored .env file)
API_USER = os.environ.get("NG_API_USER")
API_PASS = os.environ.get("NG_API_PASS")


def api_get(path, params=None, retries=3):
    """GET one API path with HTTP basic auth, retrying on non-200 responses
    with a short backoff (the API occasionally needs a second try)."""
    if not API_USER or not API_PASS:
        raise RuntimeError(
            "NG_API_USER / NG_API_PASS are not set. Copy .env.example to .env "
            "and fill in real values, or export them as environment variables."
        )
    url = f"{API_BASE}{path}"
    for attempt in range(retries):
        resp = requests.get(url, params=params, auth=(API_USER, API_PASS), timeout=30)
        if resp.status_code == 200:
            return resp.json()
        if attempt == retries - 1:
            # last attempt failed too - raise so the caller sees it, rather
            # than silently returning nothing
            resp.raise_for_status()
        time.sleep(1.5 * (attempt + 1))


def iter_paintings(fields=None, per_page=100, **filters):
    """Yield every painting matching `filters` one at a time, walking all
    pages of /api/paintings so callers don't have to think about pagination.
    `fields` adds extra document fields to each card (e.g. swatches, subjects).
    `filters` are passed straight through as query params (e.g. has_image="true")."""
    page = 1
    params = dict(filters)
    params["per_page"] = per_page
    if fields:
        params["fields"] = ",".join(fields)
    while True:
        params["page"] = page
        data = api_get("/paintings", params=params)
        for item in data["items"]:
            yield item
        if page >= data["pages"]:
            break
        page += 1
