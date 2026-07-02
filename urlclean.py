#!/usr/bin/env python3
"""urlclean — strip tracking parameters from URLs.

Usage:
  urlclean.py URL [URL ...]        # print cleaned URLs
  cat urls.txt | urlclean.py       # read URLs from stdin (one per line)
  urlclean.py --json URL           # full analysis as JSON
  urlclean.py --keep loc URL       # force-keep a param
  urlclean.py --strip ref URL      # strip an extra param
"""
import argparse
import json
import sys
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

# Tracking by prefix (utm_source, pk_campaign, ...)
TRACKING_PREFIXES = ("utm_", "mtm_", "pk_", "vero_", "oly_")

# Tracking everywhere, regardless of site
TRACKING_PARAMS = {
    # Ad-platform click IDs
    "msclkid", "gclid", "gbraid", "wbraid", "dclid", "fbclid",
    "ttclid", "twclid", "li_fat_id", "igshid", "yclid", "epik",
    # Affiliate networks
    "irclickid", "clickid", "afid", "ranmid", "ranealid", "ransiteid",
    # Email marketing
    "mc_cid", "mc_eid", "_hsenc", "_hsmi", "mkt_tok",
    # Misc analytics
    "ref_src", "spm", "scm",
}

# Tracking only on matching domains (handles the "loc is functional elsewhere" problem)
DOMAIN_RULES = {
    "ebay.":   {"mkevt", "mkcid", "mkrid", "campid", "toolid", "customid",
                "loc", "amdata", "hash"},
    "amazon.": {"tag", "linkcode", "ref_", "pd_rd_r", "pd_rd_w", "pd_rd_wg",
                "pf_rd_p", "pf_rd_r", "crid", "sprefix", "qid", "sr", "keywords"},
    "aliexpress.": {"spm", "scm", "aff_fcid", "aff_fsk", "aff_platform",
                    "aff_trace_key", "terminal_id"},
}


def _domain_extra(host: str) -> set:
    extra = set()
    for fragment, params in DOMAIN_RULES.items():
        if fragment in host:
            extra |= params
    return extra


def _is_tracking(key: str, domain_extra: set, keep: set, strip: set) -> bool:
    k = key.lower()
    if k in keep:
        return False
    if k in strip:
        return True
    return (k in TRACKING_PARAMS or k in domain_extra
            or k.startswith(TRACKING_PREFIXES))


def analyze(url: str, keep: set = frozenset(), strip: set = frozenset()) -> dict:
    """Split a URL's query params into functional vs tracking and build a clean URL."""
    parts = urlparse(url)
    domain_extra = _domain_extra(parts.netloc.lower())
    params = parse_qsl(parts.query, keep_blank_values=True)
    tracking = [(k, v) for k, v in params if _is_tracking(k, domain_extra, keep, strip)]
    functional = [(k, v) for k, v in params if not _is_tracking(k, domain_extra, keep, strip)]
    return {
        "url": url,
        "clean_url": urlunparse(parts._replace(query=urlencode(functional))),
        "functional": dict(functional),
        "tracking": dict(tracking),
        "removed": len(tracking),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="urlclean",
                                 description="Strip tracking parameters from URLs.")
    ap.add_argument("urls", nargs="*", help="URLs to clean (reads stdin if omitted)")
    ap.add_argument("--json", action="store_true", help="output full analysis as JSON")
    ap.add_argument("--keep", action="append", default=[], metavar="PARAM",
                    help="never strip this param (repeatable)")
    ap.add_argument("--strip", action="append", default=[], metavar="PARAM",
                    help="always strip this param (repeatable)")
    args = ap.parse_args(argv)

    urls = args.urls or [line.strip() for line in sys.stdin if line.strip()]
    if not urls:
        ap.error("no URLs given (pass as arguments or pipe via stdin)")

    keep = {p.lower() for p in args.keep}
    strip = {p.lower() for p in args.strip}
    results = [analyze(u, keep, strip) for u in urls]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(r["clean_url"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
