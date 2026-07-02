"""Tests for urlclean. Run with: python -m pytest test_urlclean.py -v"""
import json
import subprocess
import sys

from urlclean import analyze

EBAY_URL = (
    "https://www.ebay.com/itm/398034545525?var=0&mkevt=1&mkcid=1"
    "&mkrid=711-53200-19255-0&campid=5338767596&toolid=20006&loc=79709"
    "&customid=4582077290774889_710711913_o.2672506580e215e69cfd3a23296bc854"
    "&msclkid=2672506580e215e69cfd3a23296bc854"
)

VITALSOURCE_URL = (
    "https://www.vitalsource.com/products/"
    "japanese-literature-a-very-short-introduction-alan-tansman-v9780190933913"
    "?duration=180&utm_source=bing&utm_medium=cpc"
    "&utm_campaign=VST%20Tier%20Two%20ShoppingGoogle-US"
    "&msclkid=e3d53e381f23132f7aa7547eb6aa0380"
)


def test_ebay_affiliate_params_stripped():
    result = analyze(EBAY_URL)
    assert result["clean_url"] == "https://www.ebay.com/itm/398034545525?var=0"
    assert result["functional"] == {"var": "0"}
    assert set(result["tracking"]) == {
        "mkevt", "mkcid", "mkrid", "campid", "toolid", "loc", "customid", "msclkid",
    }
    assert result["removed"] == 8


def test_utm_and_msclkid_stripped_functional_kept():
    result = analyze(VITALSOURCE_URL)
    assert result["functional"] == {"duration": "180"}
    assert "utm_source" in result["tracking"]
    assert "utm_medium" in result["tracking"]
    assert "utm_campaign" in result["tracking"]
    assert "msclkid" in result["tracking"]
    assert result["clean_url"].endswith("?duration=180")


def test_loc_is_functional_off_ebay():
    # 'loc' is only a tracking param on eBay domains
    result = analyze("https://example.com/map?loc=79709")
    assert result["functional"] == {"loc": "79709"}
    assert result["tracking"] == {}


def test_clean_url_unchanged_when_no_tracking():
    url = "https://example.com/page?id=42&sort=asc"
    result = analyze(url)
    assert result["clean_url"] == url
    assert result["removed"] == 0


def test_keep_override():
    result = analyze(EBAY_URL, keep={"campid"})
    assert "campid" in result["functional"]
    assert "campid" not in result["tracking"]


def test_strip_override():
    result = analyze("https://example.com/page?ref=sidebar&id=1", strip={"ref"})
    assert result["functional"] == {"id": "1"}
    assert result["tracking"] == {"ref": "sidebar"}


def test_blank_values_preserved():
    result = analyze("https://example.com/page?q=&utm_source=x")
    assert result["functional"] == {"q": ""}
    assert result["tracking"] == {"utm_source": "x"}


def test_case_insensitive_matching():
    result = analyze("https://example.com/page?UTM_Source=bing&ID=7")
    assert "UTM_Source" in result["tracking"]
    assert result["functional"] == {"ID": "7"}


def test_cli_plain_output():
    proc = subprocess.run(
        [sys.executable, "urlclean.py", EBAY_URL],
        capture_output=True, text=True, check=True,
    )
    assert proc.stdout.strip() == "https://www.ebay.com/itm/398034545525?var=0"


def test_cli_stdin_and_json():
    proc = subprocess.run(
        [sys.executable, "urlclean.py", "--json"],
        input=VITALSOURCE_URL + "\n",
        capture_output=True, text=True, check=True,
    )
    data = json.loads(proc.stdout)
    assert len(data) == 1
    assert data[0]["functional"] == {"duration": "180"}
    assert data[0]["removed"] == 4
