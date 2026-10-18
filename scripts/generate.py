"""Builds assets/profile.svg: a neofetch-style animated profile card.
Stats come from the GitHub API (GITHUB_TOKEN recommended); falls back to '--'.
"""
import html, json, os, urllib.request

USER = os.environ.get("GITHUB_USER", "NTgGamer1")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "profile.svg")

ART = [' _   _ _____      ____                           _', '| \ | |_   _|_ _ / ___| __ _ _ __ ___   ___ _ __/ |', "|  \| | | |/ _` | |  _ / _` | '_ ` _ \ / _ \ '__| |", '| |\  | | | (_| | |_| | (_| | | | | | |  __/ |  | |', '|_| \_| |_|\__, |\____|\__,_|_| |_| |_|\___|_|  |_|', '           |___/']

W = 100         # info column width in characters
LH = 20         # info line height
FS = 13         # font size
ART_X, INFO_X = 32, 32


def call(url, body=None):
    h = {"User-Agent": "profile-card", "Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    data = json.dumps(body).encode() if body else None
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=20) as r:
        return json.load(r)


def stats():
    s = {"repos": "--", "stars": "--", "commits": "--", "followers": "--"}
    try:
        u = call(f"https://api.github.com/users/{USER}")
        s["repos"], s["followers"] = u["public_repos"], u["followers"]
        stars, page = 0, 1
        while True:
            repos = call(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}")
            stars += sum(r["stargazers_count"] for r in repos if not r["fork"])
            if len(repos) < 100:
                break
            page += 1
        s["stars"] = stars
    except Exception as e:
        print("REST stats failed:", e)
    try:
        q = {"query": 'query($l:String!){user(login:$l){contributionsCollection{totalCommitContributions}}}',
             "variables": {"l": USER}}
        d = call("https://api.github.com/graphql", q)
        s["commits"] = d["data"]["user"]["contributionsCollection"]["totalCommitContributions"]
    except Exception as e:
        print("GraphQL stats failed:", e)
    return s


def rows(s):
    return [
        ("head", f"{USER.lower()}@github"),
        ("kv", "Name", "Nikhil Maurya"),
        ("kv", "Education", "B.Tech CSE (AI & ML)"),
        ("kv", "College", "Delhi Technical Campus"),
        ("kv", "Batch", "2026-2030"),
        ("kv", "Location", "Uttar Pradesh, India"),
        ("blank",),
        ("kv", "Languages", "TypeScript, JavaScript, Python, SQL"),
        ("kv", "Frontend", "React, Tailwind CSS"),
        ("kv", "Backend", "Node.js, Flask"),
        ("kv", "Databases", "MySQL, SQLite"),
        ("kv", "Tools", "Git, GitHub, Vercel"),
        ("blank",),
        ("kv", "Focus", "Full-stack, Backend, DSA, AI/ML"),
        ("blank",),
        ("sect", "Links"),
        ("kv", "Portfolio", "ntggamer1.me"),
        ("kv", "LinkedIn", "ntggamer1"),
        ("kv", "GitHub", USER),
        ("blank",),
        ("sect", "GitHub Stats"),
        ("kv", "Repos", f"{s['repos']} | Stars: {s['stars']}"),
        ("kv", "Commits (1y)", f"{s['commits']} | Followers: {s['followers']}"),
        ("prompt",),
    ]


E = html.escape


def render(s):
    rs = rows(s)
    art_lh, art_fs, art_top = 22, 18, 62
    y0 = art_top + len(ART) * art_lh + 26
    h = y0 + len(rs) * LH + 12
    out = []
    a = out.append
    a(f'<svg width="880" height="{h}" viewBox="0 0 880 {h}" xmlns="http://www.w3.org/2000/svg" '
      f'font-family="\'JetBrains Mono\',\'SFMono-Regular\',Consolas,\'Liberation Mono\',monospace" font-size="{FS}">')
    a('<defs>'
      '<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="32" y1="0" x2="590" y2="0">'
      '<stop offset="0" stop-color="#58A6FF"/><stop offset="1" stop-color="#A371F7"/></linearGradient>'
      f'<clipPath id="wipe"><rect x="0" y="0" width="880" height="0">'
      f'<animate attributeName="height" from="0" to="{h}" dur="1.6s" begin="0.2s" fill="freeze"/></rect></clipPath>'
      '</defs>')
    a(f'<rect x="0.5" y="0.5" width="879" height="{h-1}" rx="12" fill="#0D1117" stroke="#30363D"/>')
    # window dots
    for cx, c in ((26, "#FF5F56"), (46, "#FFBD2E"), (66, "#27C93F")):
        a(f'<circle cx="{cx}" cy="22" r="6" fill="{c}"/>')

    # ASCII art banner on one line, revealed with a wipe
    a('<g clip-path="url(#wipe)" fill="url(#g)">')
    for i, line in enumerate(ART):
        a(f'<text x="{ART_X}" y="{art_top + i*art_lh}" font-size="{art_fs}" xml:space="preserve" style="white-space:pre">{E(line)}</text>')
    a('</g>')

    t = 0.5
    for i, r in enumerate(rs):
        y = y0 + i * LH
        kind = r[0]
        body = ""
        if kind == "head":
            txt = r[1] + " "
            body = f'<tspan fill="#E6EDF3">{E(txt)}</tspan><tspan fill="#6E7681">{"-" * (W - len(txt))}</tspan>'
        elif kind == "sect":
            txt = f"- {r[1]} "
            body = f'<tspan fill="#E6EDF3">{E(txt)}</tspan><tspan fill="#6E7681">{"-" * (W - len(txt))}</tspan>'
        elif kind == "blank":
            body = '<tspan fill="#6E7681">.</tspan>'
        elif kind == "kv":
            label, val = r[1] + ":", str(r[2])
            dots = max(3, W - 2 - len(label) - 2 - len(val))
            body = (f'<tspan fill="#6E7681">. </tspan><tspan fill="#F0883E">{E(label)}</tspan>'
                    f'<tspan fill="#6E7681"> {"." * dots} </tspan><tspan fill="#79C0FF">{E(val)}</tspan>')
        elif kind == "prompt":
            body = ('<tspan fill="#58A6FF">$ </tspan>'
                    '<tspan fill="#58A6FF">&#9608;<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan>')
        a(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
          f'<text x="{INFO_X}" y="{y}" xml:space="preserve" style="white-space:pre">{body}</text></g>')
        t += 0.11
    a('</svg>')
    return "\n".join(out)


if __name__ == "__main__":
    svg = render(stats())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", os.path.abspath(OUT))
