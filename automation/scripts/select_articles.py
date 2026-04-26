#!/usr/bin/env python3
"""Weekly OSCP-oriented security articles bot.

Fetches articles from security blogs, selects 3 best ones via keyword scoring
aligned with OSCP preparation, matches practice machines, and sends to Telegram.
Also handles spaced repetition reminders (2 weeks and 3 months).
"""

import json
import logging
import os
import random
import re
from datetime import date, timedelta
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.parent
HISTORY_PATH = REPO_ROOT / "automation" / "data" / "sent_articles.json"
LOG_PATH = REPO_ROOT / "100 - Inbox" / "reading_log.md"

# ---------------------------------------------------------------------------
# OSCP Machine Map
# ---------------------------------------------------------------------------
OSCP_MACHINE_MAP: dict = {
    "active_directory": {
        "label": "Active Directory Attacks",
        "techniques": ["Kerberoasting", "AS-REP Roasting", "Pass-the-Hash", "DCSync", "BloodHound"],
        "htb": [
            {"name": "Forest",   "url": "https://app.hackthebox.com/machines/Forest",   "writeup": "https://0xdf.gitlab.io/2020/03/21/htb-forest.html"},
            {"name": "Active",   "url": "https://app.hackthebox.com/machines/Active",   "writeup": "https://0xdf.gitlab.io/2018/12/08/htb-active.html"},
            {"name": "Resolute", "url": "https://app.hackthebox.com/machines/Resolute", "writeup": "https://0xdf.gitlab.io/2020/05/30/htb-resolute.html"},
            {"name": "Sauna",    "url": "https://app.hackthebox.com/machines/Sauna",    "writeup": "https://0xdf.gitlab.io/2020/07/18/htb-sauna.html"},
            {"name": "Cascade",  "url": "https://app.hackthebox.com/machines/Cascade",  "writeup": "https://0xdf.gitlab.io/2020/07/25/htb-cascade.html"},
        ],
        "vulnhub": [
            {"name": "MicroVuln",       "url": "https://www.vulnhub.com/entry/microvuln,816/"},
            {"name": "Razorback: 1",    "url": "https://www.vulnhub.com/entry/razorback-1,698/"},
            {"name": "HackLAB: Vulnix", "url": "https://www.vulnhub.com/entry/hacklab-vulnix,48/"},
        ],
    },
    "privesc_linux": {
        "label": "Linux Privilege Escalation",
        "techniques": ["SUID", "sudo misconfiguration", "cron jobs", "capabilities", "writable paths"],
        "htb": [
            {"name": "Nibbles",      "url": "https://app.hackthebox.com/machines/Nibbles",      "writeup": "https://0xdf.gitlab.io/2018/06/30/htb-nibbles.html"},
            {"name": "Shocker",      "url": "https://app.hackthebox.com/machines/Shocker",      "writeup": "https://0xdf.gitlab.io/2021/05/15/htb-shocker.html"},
            {"name": "Beep",         "url": "https://app.hackthebox.com/machines/Beep",         "writeup": "https://0xdf.gitlab.io/2021/02/23/htb-beep.html"},
            {"name": "ScriptKiddie", "url": "https://app.hackthebox.com/machines/ScriptKiddie", "writeup": "https://0xdf.gitlab.io/2021/06/05/htb-scriptkiddie.html"},
            {"name": "Curling",      "url": "https://app.hackthebox.com/machines/Curling",      "writeup": "https://0xdf.gitlab.io/2019/03/30/htb-curling.html"},
        ],
        "vulnhub": [
            {"name": "Kioptrix Level 1.2 (#3)", "url": "https://www.vulnhub.com/entry/kioptrix-level-12-3,24/"},
            {"name": "InfoSec Prep: OSCP",      "url": "https://www.vulnhub.com/entry/infosec-prep-oscp,508/"},
            {"name": "FristiLeaks 1.3",         "url": "https://www.vulnhub.com/entry/fristileaks-13,133/"},
        ],
    },
    "privesc_windows": {
        "label": "Windows Privilege Escalation",
        "techniques": ["SeImpersonatePrivilege", "JuicyPotato", "unquoted service paths", "registry", "AlwaysInstallElevated"],
        "htb": [
            {"name": "Jeeves",   "url": "https://app.hackthebox.com/machines/Jeeves",   "writeup": "https://0xdf.gitlab.io/2022/04/14/htb-jeeves.html"},
            {"name": "Bastion",  "url": "https://app.hackthebox.com/machines/Bastion",  "writeup": "https://0xdf.gitlab.io/2019/09/07/htb-bastion.html"},
            {"name": "Conceal",  "url": "https://app.hackthebox.com/machines/Conceal",  "writeup": "https://0xdf.gitlab.io/2019/05/18/htb-conceal.html"},
            {"name": "SecNotes", "url": "https://app.hackthebox.com/machines/SecNotes", "writeup": "https://0xdf.gitlab.io/2019/01/19/htb-secnotes.html"},
        ],
        "vulnhub": [
            {"name": "HackLAB: Vulnix", "url": "https://www.vulnhub.com/entry/hacklab-vulnix,48/"},
            {"name": "pWnOS 2.0",       "url": "https://www.vulnhub.com/entry/pwnos-20-pre-release,34/"},
            {"name": "Healthcare: 1",   "url": "https://www.vulnhub.com/entry/healthcare-1,522/"},
        ],
    },
    "web_attacks": {
        "label": "Web Attacks",
        "techniques": ["SQLi", "LFI", "RFI", "File Upload", "SSTI", "Command Injection"],
        "htb": [
            {"name": "Cronos",    "url": "https://app.hackthebox.com/machines/Cronos",    "writeup": "https://0xdf.gitlab.io/2020/04/14/htb-cronos.html"},
            {"name": "Doctor",    "url": "https://app.hackthebox.com/machines/Doctor",    "writeup": "https://0xdf.gitlab.io/2021/02/06/htb-doctor.html"},
            {"name": "Networked", "url": "https://app.hackthebox.com/machines/Networked", "writeup": "https://0xdf.gitlab.io/2019/11/16/htb-networked.html"},
            {"name": "Zipping",   "url": "https://app.hackthebox.com/machines/Zipping",   "writeup": "https://0xdf.gitlab.io/2024/01/13/htb-zipping.html"},
            {"name": "Magic",     "url": "https://app.hackthebox.com/machines/Magic",     "writeup": "https://0xdf.gitlab.io/2020/08/22/htb-magic.html"},
        ],
        "vulnhub": [
            {"name": "Kioptrix Level 1.3 (#4)", "url": "https://www.vulnhub.com/entry/kioptrix-level-13-4,25/"},
            {"name": "pWnOS 2.0",               "url": "https://www.vulnhub.com/entry/pwnos-20-pre-release,34/"},
            {"name": "Mr. Robot: 1",            "url": "https://www.vulnhub.com/entry/mr-robot-1,151/"},
        ],
    },
    "buffer_overflow": {
        "label": "Buffer Overflow",
        "techniques": ["stack BOF", "ret2libc", "ROP chains", "offset finding", "bad char analysis"],
        "htb": [
            {"name": "Safe",      "url": "https://app.hackthebox.com/machines/Safe",      "writeup": "https://0xdf.gitlab.io/2019/10/26/htb-safe.html"},
            {"name": "October",   "url": "https://app.hackthebox.com/machines/October",   "writeup": "https://0xdf.gitlab.io/2018/08/04/htb-october.html"},
            {"name": "Ellingson", "url": "https://app.hackthebox.com/machines/Ellingson", "writeup": "https://0xdf.gitlab.io/2019/10/19/htb-ellingson.html"},
        ],
        "vulnhub": [
            {"name": "Brainpan: 1",    "url": "https://www.vulnhub.com/entry/brainpan-1,51/"},
            {"name": "Brainpan: 2",    "url": "https://www.vulnhub.com/entry/brainpan-2,56/"},
            {"name": "Kioptrix: 2014", "url": "https://www.vulnhub.com/entry/kioptrix-2014-5,62/"},
        ],
    },
    "tunneling_pivoting": {
        "label": "Tunneling / Pivoting",
        "techniques": ["chisel SOCKS proxy", "SSH dynamic forwarding", "proxychains", "sshuttle"],
        "htb": [
            {"name": "Vault",   "url": "https://app.hackthebox.com/machines/Vault",   "writeup": "https://0xdf.gitlab.io/2019/04/06/htb-vault.html"},
            {"name": "Reddish", "url": "https://app.hackthebox.com/machines/Reddish", "writeup": "https://0xdf.gitlab.io/2019/01/26/htb-reddish.html"},
            {"name": "Sniper",  "url": "https://app.hackthebox.com/machines/Sniper",  "writeup": "https://0xdf.gitlab.io/2020/02/01/htb-sniper.html"},
        ],
        "vulnhub": [
            {"name": "SkyTower: 1", "url": "https://www.vulnhub.com/entry/skytower-1,96/"},
            {"name": "Stapler: 1",  "url": "https://www.vulnhub.com/entry/stapler-1,150/"},
            {"name": "VulnOS: 2",   "url": "https://www.vulnhub.com/entry/vulnos-2,147/"},
        ],
    },
    "password_attacks": {
        "label": "Password Attacks",
        "techniques": ["hashcat", "john the ripper", "credential reuse", "password spraying", "SAM/NTDS dumping"],
        "htb": [
            {"name": "Resolute", "url": "https://app.hackthebox.com/machines/Resolute", "writeup": "https://0xdf.gitlab.io/2020/05/30/htb-resolute.html"},
            {"name": "Bastion",  "url": "https://app.hackthebox.com/machines/Bastion",  "writeup": "https://0xdf.gitlab.io/2019/09/07/htb-bastion.html"},
            {"name": "Safe",     "url": "https://app.hackthebox.com/machines/Safe",     "writeup": "https://0xdf.gitlab.io/2019/10/26/htb-safe.html"},
        ],
        "vulnhub": [
            {"name": "Kioptrix Level 1.1 (#2)", "url": "https://www.vulnhub.com/entry/kioptrix-level-11-2,23/"},
            {"name": "FristiLeaks 1.3",          "url": "https://www.vulnhub.com/entry/fristileaks-13,133/"},
            {"name": "Stapler: 1",               "url": "https://www.vulnhub.com/entry/stapler-1,150/"},
        ],
    },
}

# ---------------------------------------------------------------------------
# RSS Sources
# ---------------------------------------------------------------------------
RSS_FEEDS = [
    {"name": "hackware.ru",      "url": "https://hackware.ru/?feed=rss2"},
    {"name": "en.hackndo.com",   "url": "https://en.hackndo.com/feed.xml"},
    {"name": "timcore.ru",       "url": "https://timcore.ru/feed/"},
    {"name": "specterops.io",    "url": "https://posts.specterops.io/feed"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ---------------------------------------------------------------------------
# Keyword scoring (no Claude API needed)
# ---------------------------------------------------------------------------

# Priority order: lower number = higher priority
DOMAIN_PRIORITY = [
    "buffer_overflow",
    "tunneling_pivoting",
    "active_directory",
    "web_attacks",
    "privesc_linux",
    "privesc_windows",
    "password_attacks",
]

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "buffer_overflow": [
        "buffer overflow", "bof", "stack overflow", "ret2libc", "rop chain",
        "shellcode", "exploit development", "eip", "esp", "immunity debugger",
        "mona", "offset", "bad chars", "win32", "stack buffer",
    ],
    "tunneling_pivoting": [
        "pivot", "tunnel", "chisel", "proxychains", "sshuttle", "port forward",
        "lateral movement", "double pivot", "socks proxy", "dynamic port",
        "ssh tunnel", "network pivoting", "internal network",
    ],
    "active_directory": [
        "active directory", "kerberos", "kerberoasting", "as-rep", "asreproast",
        "pass the hash", "pass-the-hash", "dcsync", "bloodhound", "ldap",
        "domain controller", "spn", "golden ticket", "silver ticket",
        "mimikatz", "rubeus", "impacket", "smb relay", "ntlm", "winrm",
        "powerview", "sharphound", "delegation", "acl abuse",
    ],
    "web_attacks": [
        "sql injection", "sqli", "lfi", "rfi", "local file inclusion",
        "remote file inclusion", "file upload", "ssti", "server side template",
        "command injection", "xss", "ssrf", "xxe", "rce", "web shell",
        "directory traversal", "path traversal", "php", "burp suite",
        "web application", "ffuf", "gobuster", "nikto",
    ],
    "privesc_linux": [
        "linux privilege escalation", "linux privesc", "suid", "sudo",
        "cron job", "capabilities", "writable", "setuid", "linpeas",
        "linux enumeration", "sudo -l", "pspy", "/etc/passwd", "/etc/shadow",
        "nfs", "docker escape", "lxd",
    ],
    "privesc_windows": [
        "windows privilege escalation", "windows privesc", "seimpersonate",
        "juicypotato", "printspoofer", "unquoted service", "always install",
        "alwaysinstallelevated", "registry", "winpeas", "accesschk",
        "weak service", "dll hijacking", "token impersonation",
    ],
    "password_attacks": [
        "hashcat", "john the ripper", "password crack", "password spray",
        "credential", "hash", "ntlm hash", "password reuse", "rockyou",
        "wordlist", "brute force", "hydra", "medusa", "sam database",
        "lsass", "secretsdump", "ntds",
    ],
}


# ---------------------------------------------------------------------------
# Fetch articles
# ---------------------------------------------------------------------------

def fetch_rss(feed: dict) -> list[dict]:
    """Parse one RSS feed, return list of article dicts."""
    articles = []
    try:
        parsed = feedparser.parse(feed["url"])
        for entry in parsed.entries:
            articles.append({
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "source": feed["name"],
            })
        log.info("RSS %s: %d articles", feed["name"], len(articles))
    except Exception as exc:
        log.warning("RSS fetch failed for %s: %s", feed["name"], exc)
    return articles


def fetch_hackingarticles() -> list[dict]:
    """Scrape hackingarticles.in homepage for article links."""
    articles = []
    try:
        resp = requests.get("https://www.hackingarticles.in/", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select("article h2 a, .entry-title a, h2.post-title a"):
            title = a.get_text(strip=True)
            url = a.get("href", "").strip()
            if title and url and url.startswith("http"):
                articles.append({"title": title, "url": url, "source": "hackingarticles.in"})
        log.info("Scraped hackingarticles.in: %d articles", len(articles))
    except Exception as exc:
        log.warning("hackingarticles.in scrape failed: %s", exc)
    return articles


def load_history() -> dict:
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH) as f:
            return json.load(f)
    return {"sent": []}


def save_history(history: dict) -> None:
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def filter_new(articles: list[dict], history: dict) -> list[dict]:
    sent_urls = {entry["url"] for entry in history["sent"]}
    new = [a for a in articles if a["url"] not in sent_urls and a["url"]]
    log.info("New articles after filter: %d", len(new))
    return new


# ---------------------------------------------------------------------------
# Keyword-based selection (no external API)
# ---------------------------------------------------------------------------

# Noise patterns — skip articles matching these
NOISE_PATTERNS = re.compile(
    r"\b(CVE-\d{4}|patch tuesday|vulnerability roundup|weekly news|"
    r"cyber news|security news|breach|ransomware gang|data leak|"
    r"arrested|indicted|фишинг|мошенник|утечка)\b",
    re.IGNORECASE,
)


def score_article(title: str) -> tuple[str, int]:
    """Return (best_matching_domain, score). Score 0 = no match."""
    text = title.lower()
    best_domain = ""
    best_score = 0

    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_domain = domain

    return best_domain, best_score


def select_articles(articles: list[dict]) -> dict:
    """Score and select 3 articles by OSCP domain priority. No external API."""
    log.info("Scoring %d articles by keyword matching...", len(articles))

    # Filter obvious noise
    candidates = [a for a in articles if not NOISE_PATTERNS.search(a["title"])]
    log.info("After noise filter: %d candidates", len(candidates))

    # Score each article
    scored: list[tuple[int, str, dict]] = []  # (priority, domain, article)
    for article in candidates:
        domain, score = score_article(article["title"])
        if score == 0:
            continue
        priority = DOMAIN_PRIORITY.index(domain) if domain in DOMAIN_PRIORITY else 99
        scored.append((priority, domain, article))

    # Sort: lower priority index first, then higher score
    scored.sort(key=lambda x: x[0])

    # Pick 3 — one per domain when possible (variety), else same domain (deep_dive)
    selected = []
    used_domains: list[str] = []

    # First pass: one article per domain in priority order
    for priority, domain, article in scored:
        if domain not in used_domains and len(selected) < 3:
            selected.append((domain, article))
            used_domains.append(domain)

    # Second pass: fill remaining slots if needed
    if len(selected) < 3:
        for priority, domain, article in scored:
            if article not in [s[1] for s in selected] and len(selected) < 3:
                selected.append((domain, article))

    # Fallback: just take first 3 unscored articles if still empty
    if len(selected) < 3:
        log.warning("Not enough scored articles, using unscored fallback")
        for article in candidates:
            if article not in [s[1] for s in selected] and len(selected) < 3:
                domain, _ = score_article(article["title"])
                selected.append((domain or "active_directory", article))

    unique_domains = list(dict.fromkeys(d for d, _ in selected))
    session_type = "deep_dive" if len(unique_domains) == 1 else "variety"

    result_articles = []
    for domain, article in selected:
        label = DOMAIN_LABELS.get(domain, domain) if domain else "General"
        result_articles.append({
            **article,
            "oscp_domain": domain or "active_directory",
            "reason": f"Matches OSCP domain: {label}",
            "summary": f"Article covers {label} techniques relevant to OSCP certification.",
        })

    log.info("Selected %d articles. Session type: %s", len(result_articles), session_type)
    return {"session_type": session_type, "articles": result_articles}


# ---------------------------------------------------------------------------
# Machine matching
# ---------------------------------------------------------------------------

def pick_machines(domain: str) -> tuple[dict, dict]:
    """Return (htb_machine, vulnhub_machine) randomly chosen for domain."""
    domain_data = OSCP_MACHINE_MAP.get(domain, OSCP_MACHINE_MAP["active_directory"])
    htb = random.choice(domain_data["htb"])
    vulnhub = random.choice(domain_data["vulnhub"])
    return htb, vulnhub


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def tg_send(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    resp = requests.post(url, json=payload, timeout=15)
    if not resp.ok:
        log.error("Telegram send failed: %s %s", resp.status_code, resp.text)


DOMAIN_LABELS = {
    d: v["label"] for d, v in OSCP_MACHINE_MAP.items()
}


def send_article_message(token: str, chat_id: str, article: dict, htb: dict, vulnhub: dict, reason: str, domain: str) -> None:
    label = DOMAIN_LABELS.get(domain, domain)
    text = (
        f"📖 *{article['title']}*\n"
        f"🔗 {article['url']}\n"
        f"📌 Тема: {label}\n"
        f"💡 {reason}\n\n"
        f"🖥 HTB Retired: [{htb['name']}]({htb['url']})\n"
        f"📝 Writeup: {htb['writeup']}\n\n"
        f"🟢 VulnHub: [{vulnhub['name']}]({vulnhub['url']})"
    )
    tg_send(token, chat_id, text)


def send_summary_message(token: str, chat_id: str, session_type: str, domains: list[str]) -> None:
    domain_names = ", ".join(DOMAIN_LABELS.get(d, d) for d in set(domains))
    session_label = "Deep Dive 🔭" if session_type == "deep_dive" else "Variety 🎯"
    text = (
        f"✅ *Воскресная подборка готова*\n"
        f"Сессия: {session_label}\n"
        f"Тема(ы): {domain_names}\n"
        f"Повторение через 2 недели 🔁"
    )
    tg_send(token, chat_id, text)


# ---------------------------------------------------------------------------
# Spaced repetition
# ---------------------------------------------------------------------------

def check_reminders(history: dict, token: str, chat_id: str) -> bool:
    """Send due reminders. Returns True if any were sent."""
    today = date.today().isoformat()
    changed = False

    for entry in history["sent"]:
        title = entry.get("title", "")
        url = entry.get("url", "")
        summary = entry.get("summary", "")

        if not entry.get("reminded_2w") and entry.get("remind_2w_date", "") <= today:
            log.info("Sending 2-week reminder for: %s", title)
            text = (
                f"🔁 *2 недели назад ты читал:*\n\n"
                f"*{title}*\n"
                f"📌 {url}\n\n"
                f"🧠 Напоминание: {summary}"
            )
            tg_send(token, chat_id, text)
            entry["reminded_2w"] = True
            changed = True

        if not entry.get("reminded_3m") and entry.get("remind_3m_date", "") <= today:
            log.info("Sending 3-month flash for: %s", title)
            brief = summary.split(".")[0] + "." if summary else ""
            text = (
                f"⚡ *3 месяца назад:*\n\n"
                f"*{title}* — {brief}"
            )
            tg_send(token, chat_id, text)
            entry["reminded_3m"] = True
            changed = True

    return changed


# ---------------------------------------------------------------------------
# Reading log
# ---------------------------------------------------------------------------

def update_reading_log(selected_articles: list[dict], session_type: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    session_label = "Deep Dive" if session_type == "deep_dive" else "Variety"
    domains = list({a["oscp_domain"] for a in selected_articles})
    domain_names = ", ".join(DOMAIN_LABELS.get(d, d) for d in domains)

    lines = [f"\n## {today}\n", f"**Тип сессии:** {session_label}\n", f"**OSCP домен(ы):** {domain_names}\n\n"]

    for i, a in enumerate(selected_articles, 1):
        htb = a["htb"]
        vulnhub = a["vulnhub"]
        lines += [
            f"### Статья {i}: {a['title']}\n",
            f"- **Ссылка:** {a['url']}\n",
            f"- **Домен:** {DOMAIN_LABELS.get(a['oscp_domain'], a['oscp_domain'])}\n",
            f"- **HTB:** [{htb['name']}]({htb['url']}) — [Writeup]({htb['writeup']})\n",
            f"- **VulnHub:** [{vulnhub['name']}]({vulnhub['url']})\n",
            f"- **Саммари:** {a['summary']}\n\n",
        ]

    existing = LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else "# Reading Log\n"
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(existing + "".join(lines))

    log.info("reading_log.md updated")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")

    history = load_history()

    # Spaced repetition check
    reminder_sent = check_reminders(history, token, chat_id)
    if reminder_sent:
        save_history(history)

    # Fetch articles
    all_articles: list[dict] = []
    for feed in RSS_FEEDS:
        all_articles.extend(fetch_rss(feed))
    all_articles.extend(fetch_hackingarticles())

    new_articles = filter_new(all_articles, history)

    if len(new_articles) < 3:
        log.warning("Not enough new articles (%d). Skipping this week.", len(new_articles))
        tg_send(token, chat_id, "⚠️ Недостаточно новых статей на этой неделе. Подборка пропущена.")
        return

    # Keyword-based selection
    result = select_articles(new_articles)
    session_type = result["session_type"]

    today = date.today()
    remind_2w = (today + timedelta(weeks=2)).isoformat()
    remind_3m = (today + timedelta(days=91)).isoformat()

    enriched: list[dict] = []
    for sel in result["articles"]:
        htb, vulnhub = pick_machines(sel["oscp_domain"])
        enriched.append({
            **sel,
            "htb": htb,
            "vulnhub": vulnhub,
        })

    # Send Telegram messages
    for a in enriched:
        send_article_message(token, chat_id, a, a["htb"], a["vulnhub"], a["reason"], a["oscp_domain"])

    domains = [a["oscp_domain"] for a in enriched]
    send_summary_message(token, chat_id, session_type, domains)

    # Update history
    for a in enriched:
        history["sent"].append({
            "url": a["url"],
            "title": a["title"],
            "date_sent": today.isoformat(),
            "oscp_domain": a["oscp_domain"],
            "summary": a["summary"],
            "remind_2w_date": remind_2w,
            "remind_3m_date": remind_3m,
            "reminded_2w": False,
            "reminded_3m": False,
        })
    save_history(history)

    # Update reading log
    update_reading_log(enriched, session_type)

    log.info("Done. Sent %d articles.", len(enriched))


if __name__ == "__main__":
    main()
