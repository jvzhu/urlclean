# urlclean

Strip tracking parameters (`utm_*`, `msclkid`, `gclid`, `fbclid`, `cm_mmc`, eBay EPN affiliate params, ...) from URLs while preserving functional parameters.

Includes:

- **`urlclean.py`** — a zero-dependency Python CLI (stdlib only)
- **`extension/`** — a Manifest V3 browser extension that cleans links on pages as you browse

## How it works

Query parameters are classified as *tracking* or *functional* using three rule sets:

1. **Prefix rules** — anything starting with `utm_`, `mtm_`, `pk_`, `vero_`, `oly_`
2. **Global exact-match rules** — ad-platform click IDs (`msclkid`, `gclid`, `fbclid`, ...), affiliate network IDs, email-marketing params, Coremetrics / IBM Analytics campaign params (`cm_mmc`, `cm_sp`, `cm_re`, ...)
3. **Domain-specific rules** — params that are tracking only on certain sites, e.g. `loc` and `campid` on eBay, `tag` on Amazon, `ref_` on Amazon-family sites (amazon.*, abebooks.*). This avoids breaking sites where the same name is functional (e.g. `?loc=` on a maps site).

Tracking params are removed; everything else is kept, in order, and the URL is rebuilt.

## CLI usage

```console
$ python urlclean.py "https://www.ebay.com/itm/398034545525?var=0&mkevt=1&campid=5338767596&msclkid=abc123"
https://www.ebay.com/itm/398034545525?var=0

$ python urlclean.py "https://www.abebooks.com/servlet/BookDetailsPL?bi=31440603497&dest=USA&ref_=ps_ms_370718797&cm_mmc=msn-_-comus_shopp_textbook-_-naa-_-naa&msclkid=d586392f"
https://www.abebooks.com/servlet/BookDetailsPL?bi=31440603497&dest=USA

# Read from stdin, one URL per line
$ cat urls.txt | python urlclean.py > cleaned.txt

# Full analysis as JSON
$ python urlclean.py --json "https://example.com/?duration=180&utm_source=bing"
[
  {
    "url": "https://example.com/?duration=180&utm_source=bing",
    "clean_url": "https://example.com/?duration=180",
    "functional": {"duration": "180"},
    "tracking": {"utm_source": "bing"},
    "removed": 1
  }
]

# Overrides (repeatable)
$ python urlclean.py --keep campid --strip ref "https://..."
```

Requires Python 3.8+. No third-party dependencies.

## Browser extension

Cleans every `<a href>` on pages you visit, including dynamically inserted links (via `MutationObserver`).

**Install (Chrome / Edge):**

1. Open `chrome://extensions` (or `edge://extensions`)
2. Enable **Developer mode**
3. Click **Load unpacked** and select the `extension/` folder

## Tests

```console
$ pip install pytest
$ python -m pytest test_urlclean.py -v
```

## Caveats

Classification is heuristic. A parameter like `ref` or `loc` is tracking on some sites and functional on others — that's what the domain rules are for. If you hit a site where cleaning breaks a link, use `--keep <param>` on the CLI, or add/adjust a domain rule.

## License

MIT
