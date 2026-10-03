#!/usr/bin/env python3
"""Rebuilds profile/README.md from profile/README.template.md and the live repo list."""
import os, re, subprocess, datetime

ORG = os.environ.get("ORG", "Twittpay")

def gh(*args):
    return subprocess.check_output(["gh", "api"] + list(args), universal_newlines=True)

rows = []
out = gh("--paginate", "orgs/%s/repos?type=public&per_page=100" % ORG,
         "--jq", '.[] | [.name, (.description // ""), (.archived|tostring)] | @tsv')
for line in out.splitlines():
    name, desc, archived = (line.split("\t") + ["", "", ""])[:3]
    if not name.startswith("twittpay-") or archived == "true":
        continue
    title = re.sub(r"^TwittPay payment gateway for ", "", desc) or name[len("twittpay-"):].replace("-", " ").title()
    try:
        tag = gh("repos/%s/%s/releases/latest" % (ORG, name), "--jq", ".tag_name").strip()
    except subprocess.CalledProcessError:
        tag = "-"
    url = "https://github.com/%s/%s" % (ORG, name)
    dl = "[Download](%s/releases/latest)" % url if tag != "-" else "-"
    rows.append((title.lower(), "| %s | [%s](%s) | **%s** | %s |" % (title, name, url, tag, dl)))

rows.sort()
table = "| Platform | Repository | Latest version | Get it |\n|---|---|---|---|\n" + "\n".join(r[1] for r in rows)

here = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(here, "..", "profile", "README.template.md"), encoding="utf-8").read()
tpl = tpl.replace("{{ADDONS_TABLE}}", table)
tpl = tpl.replace("{{COUNT}}", str(len(rows)))
tpl = tpl.replace("{{UPDATED}}", datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
open(os.path.join(here, "..", "profile", "README.md"), "w", encoding="utf-8").write(tpl)
print("addons:", len(rows))
