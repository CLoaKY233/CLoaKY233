import os
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
FEATURE_FILE = ROOT / "featured-repos.txt"
README_FILE = ROOT / "README.md"

token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {token}"} if token else {}


def read_featured_repos():
    repos = []
    if not FEATURE_FILE.exists():
        return repos
    for line in FEATURE_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        repos.append(line)
    return repos


def fetch_repo(full_name: str):
    url = f"https://api.github.com/repos/{full_name}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def build_table():
    featured = read_featured_repos()
    if not featured:
        return "| Repo | Description | Stars |\n| --- | --- | --- |\n| _No repositories configured yet_ |  |  |"
    rows = []
    for full in featured:
        data = fetch_repo(full)
        name = data["name"]
        url = data["html_url"]
        desc = (data.get("description") or "").replace("|", "\\|")
        stars = data.get("stargazers_count", 0)
        rows.append(f"| [{name}]({url}) | {desc} | ⭐ {stars} |")
    header = [
        "| Repo | Description | Stars |",
        "| --- | --- | --- |",
    ]
    return "\n".join(header + rows)


def replace_section(markdown: str, new_table: str) -> str:
    pattern = r"(<!-- REPO-TABLE:START -->)(.*?)(<!-- REPO-TABLE:END -->)"
    replacement = r"\\1\n" + new_table + r"\n\\3"
    return re.sub(pattern, replacement, markdown, flags=re.S)


def main():
    table_md = build_table()
    content = README_FILE.read_text(encoding="utf-8")
    new_content = replace_section(content, table_md)
    README_FILE.write_text(new_content, encoding="utf-8")


if __name__ == "__main__":
    main()
