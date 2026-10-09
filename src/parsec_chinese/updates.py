import json
import urllib.request
from . import __version__


def latest_release():
    request = urllib.request.Request("https://api.github.com/repos/hhhoratioxu/Parsec-Chinese-Localization/releases?per_page=1",
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": f"ParsecChineseLocalization/{__version__}"})
    with urllib.request.urlopen(request, timeout=10) as response:
        releases = json.loads(response.read(262144))
    if not isinstance(releases, list) or not releases:
        raise ValueError("No published release")
    data = releases[0]
    tag = data.get("tag_name", "")
    import re
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?", tag):
        raise ValueError("Invalid release metadata")
    # Never open a server-provided URL; only the fixed repository.
    return tag
