#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║        ██╗███████╗██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗                  ║
║        ██║██╔════╝██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║                  ║
║        ██║███████╗██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║                  ║
║   ██   ██║╚════██║██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║                  ║
║   ╚█████╔╝███████║██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║                  ║
║    ╚════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝                  ║
║                                                                                  ║
║                    ░█▀▀░█░█░█▀▄░█▀▀░█▀▄░█▀▀░                                   ║
║                    ░█░░░░█░░█▀▄░█▀▀░█▀▄░█░█░                                   ║
║                    ░▀▀▀░░▀░░▀▀░░▀▀▀░▀░▀░▀▀▀░                                   ║
║                                                                                  ║
║             ── CYBORG EDITION V1 ── by Rahul Masal ──                           ║
║         Professional JavaScript Reconnaissance & Secret Hunter                  ║
║                   For Authorized Bug Bounty Use Only                            ║
╚══════════════════════════════════════════════════════════════════════════════════╝

Author  : Rahul Masal
Tool    : JSRecon - Cyborg Edition V1
Purpose : Automated JS Recon, Secret Hunting & Endpoint Extraction
Warning : Use only on authorized targets. Unauthorized use is illegal.
"""

import os
import re
import sys
import json
import time
import shutil
import hashlib
import argparse
import subprocess
import urllib.parse
import urllib.request
import urllib.error
import mimetypes
import textwrap
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────────────────────────────────────────
# ANSI COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
class C:
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"
    ORANGE  = "\033[38;5;208m"
    PURPLE  = "\033[38;5;135m"

def banner():
    print(f"""
{C.CYAN}{C.BOLD}
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║        ██╗███████╗██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗                  ║
║        ██║██╔════╝██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║                  ║
║        ██║███████╗██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║                  ║
║   ██   ██║╚════██║██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║                  ║
║   ╚█████╔╝███████║██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║                  ║
║    ╚════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝                  ║
║                                                                                  ║
║{C.ORANGE}                 ── CYBORG EDITION V1 ── by Rahul Masal ──                       {C.CYAN}║
║{C.YELLOW}             Professional JavaScript Reconnaissance & Secret Hunter              {C.CYAN}║
║{C.RED}                    ⚠  Authorized Targets Only  ⚠                               {C.CYAN}║
╚══════════════════════════════════════════════════════════════════════════════════╝
{C.RESET}""")

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%H:%M:%S")

def info(msg):    print(f"{C.DIM}[{ts()}]{C.RESET} {C.BLUE}[*]{C.RESET} {msg}")
def success(msg): print(f"{C.DIM}[{ts()}]{C.RESET} {C.GREEN}[✔]{C.RESET} {msg}")
def warn(msg):    print(f"{C.DIM}[{ts()}]{C.RESET} {C.YELLOW}[!]{C.RESET} {msg}")
def error(msg):   print(f"{C.DIM}[{ts()}]{C.RESET} {C.RED}[✘]{C.RESET} {msg}")
def phase(msg):   print(f"\n{C.CYAN}{C.BOLD}{'─'*70}\n  ► {msg}\n{'─'*70}{C.RESET}")
def finding(msg): print(f"{C.DIM}[{ts()}]{C.RESET} {C.MAGENTA}[★]{C.RESET} {C.BOLD}{msg}{C.RESET}")

# ─────────────────────────────────────────────────────────────────────────────
# DEPENDENCY CHECKER
# ─────────────────────────────────────────────────────────────────────────────
REQUIRED_TOOLS = {
    "subfinder":   "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "httpx":       "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "waybackurls": "go install github.com/tomnomnom/waybackurls@latest",
    "gospider":    "go install github.com/jaeles-project/gospider@latest",
    "katana":      "go install github.com/projectdiscovery/katana/cmd/katana@latest",
    "gowitness":   "go install github.com/sensepost/gowitness@latest",
    "aquatone":    "go install github.com/michenriksen/aquatone@latest",
    "curl":        "apt install curl",
}

# Screenshot tools — if both missing we skip screenshots gracefully
SCREENSHOT_TOOLS = {"gowitness", "aquatone"}

def check_tools():
    phase("Checking Required Tools")
    missing = []
    for tool, install_cmd in REQUIRED_TOOLS.items():
        if shutil.which(tool):
            success(f"{tool:15s} found")
        else:
            if tool in SCREENSHOT_TOOLS:
                warn(f"{tool:15s} not found  (screenshot fallback available)")
            else:
                warn(f"{tool:15s} NOT FOUND  →  {C.DIM}{install_cmd}{C.RESET}")
            missing.append(tool)

    # Screenshots: warn only if BOTH gowitness and aquatone are missing
    both_missing = all(t in missing for t in SCREENSHOT_TOOLS)
    if both_missing:
        warn("No screenshot tool found. Install at least one:")
        warn("  gowitness : go install github.com/sensepost/gowitness@latest")
        warn("  aquatone  : go install github.com/michenriksen/aquatone@latest")

    core_missing = [t for t in missing if t not in SCREENSHOT_TOOLS]
    if core_missing:
        warn(f"Missing core tools: {', '.join(core_missing)} — those phases will be skipped.")
    return missing

# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT DIRECTORY SETUP
# ─────────────────────────────────────────────────────────────────────────────
def setup_output(target_name: str) -> dict:
    base = Path("jsrecon") / "output" / target_name.replace(".", "_")
    dirs = {
        "base":        base,
        "subdomains":  base / "01_subdomains",
        "paths":       base / "02_sensitive_paths",
        "wayback":     base / "03_wayback",
        "gospider":    base / "04_gospider",
        "katana":      base / "05_katana",
        "combined":    base / "06_combined_urls",
        "js":          base / "07_js_analysis",
        "secrets":     base / "08_secrets",
        "endpoints":   base / "09_endpoints",
        "screenshots": base / "10_screenshots",
        "reports":     base / "11_reports",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return {k: str(v) for k, v in dirs.items()}

# ─────────────────────────────────────────────────────────────────────────────
# SHELL RUNNER
# ─────────────────────────────────────────────────────────────────────────────
def run(cmd: str, output_file: str = None, shell=True, timeout=600) -> str:
    """Run a shell command, optionally tee output to file. Returns stdout as string."""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True, timeout=timeout
        )
        out = result.stdout.strip()
        if output_file and out:
            with open(output_file, "w") as f:
                f.write(out + "\n")
        return out
    except subprocess.TimeoutExpired:
        warn(f"Command timed out: {cmd[:80]}...")
        return ""
    except Exception as e:
        error(f"Command failed: {e}")
        return ""

def run_pipe(cmd: str) -> list:
    """Run command and return list of non-empty lines."""
    out = run(cmd)
    return [l.strip() for l in out.splitlines() if l.strip()]

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 — SUBDOMAIN ENUMERATION
# ─────────────────────────────────────────────────────────────────────────────
def phase_subdomains(domains: list, dirs: dict, missing_tools: list) -> list:
    phase("Phase 1 — Subdomain Enumeration")
    all_subs = set()

    for domain in domains:
        info(f"Running subfinder on {domain}")
        if "subfinder" not in missing_tools:
            out = run(f"subfinder -d {domain} -silent")
            subs = [l.strip() for l in out.splitlines() if l.strip()]
            all_subs.update(subs)
            success(f"subfinder → {len(subs)} subdomains for {domain}")
        else:
            warn("subfinder not available, skipping")

    subfinder_file = os.path.join(dirs["subdomains"], "subfinder_all.txt")
    with open(subfinder_file, "w") as f:
        f.write("\n".join(sorted(all_subs)) + "\n")
    info(f"Total unique subdomains: {len(all_subs)}")

    # Get live subdomains
    live_file = os.path.join(dirs["subdomains"], "live_subdomains.txt")
    if "httpx" not in missing_tools and all_subs:
        info("Probing live subdomains with httpx...")
        run(
            f"cat {subfinder_file} | httpx -silent -mc 200,401,403,404,302 -o {live_file}",
        )
        live_domains = [l.strip() for l in open(live_file).readlines() if l.strip()]
        success(f"Live subdomains: {len(live_domains)}")
        return live_domains
    else:
        with open(live_file, "w") as f:
            f.write("\n".join(sorted(all_subs)) + "\n")
        return list(all_subs)

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 — SENSITIVE PATH CHECKING
# ─────────────────────────────────────────────────────────────────────────────
SENSITIVE_PATHS = [
    "/debug.log", "/oauth.txt", "/logs/emails.txt", "/emails.txt",
    "/logs/debug.log", "/logs/log.txt", "/log.txt",
    "/register/logs/log.txt", "/register/logs/emails.txt",
    "/config.js", "/config.json", "/app/config.js",
    "/settings.json", "/database.json", "/firebase.json",
    "/.env", "/.env.production", "/.env.local", "/.env.dev",
    "/api_keys.json", "/credentials.json", "/secrets.json",
    "/google-services.json", "/package.json", "/package-lock.json",
    "/composer.json", "/pom.xml", "/docker-compose.yml",
    "/manifest.json", "/service-worker.js",
    "/wp-config.php", "/.git/config", "/.gitignore",
    "/robots.txt", "/sitemap.xml", "/crossdomain.xml",
    "/web.config", "/app.config", "/appsettings.json",
    "/swagger.json", "/openapi.json", "/api-docs.json",
    "/graphql", "/graphiql", "/.well-known/security.txt",
    "/server-status", "/server-info", "/phpinfo.php",
    "/backup.zip", "/backup.sql", "/dump.sql",
    "/admin", "/admin/config", "/api/swagger",
]

def check_sensitive_paths(live_domains: list, dirs: dict, missing_tools: list):
    phase("Phase 2 — Sensitive Path Discovery")
    raw_findings = os.path.join(dirs["paths"], "raw_findings.txt")
    filtered_findings = os.path.join(dirs["paths"], "findings_unique.txt")

    if "httpx" in missing_tools:
        warn("httpx not available — skipping sensitive path check")
        return

    # Build URL list
    urls = []
    for host in live_domains:
        host = host.strip().rstrip("/")
        if not host.startswith("http"):
            host = "https://" + host
        for path in SENSITIVE_PATHS:
            urls.append(host + path)

    urls_file = os.path.join(dirs["paths"], "paths_to_check.txt")
    with open(urls_file, "w") as f:
        f.write("\n".join(urls) + "\n")
    info(f"Checking {len(urls)} sensitive path combinations...")

    # httpx -mc 200 -cl -sc gives: URL [status] [content-length]
    run(f"cat {urls_file} | httpx -silent -mc 200 -cl -sc -o {raw_findings}")

    if not os.path.exists(raw_findings) or os.path.getsize(raw_findings) == 0:
        info("No sensitive paths found (200 OK)")
        return

    # Deduplicate by content-length to remove honeypots/default pages
    # Also store size info: url|status|content_length
    info("Filtering by content-length to remove false positives...")
    from collections import defaultdict
    cl_map = {}   # url -> (status, content_length_str)
    cl_raw = run(f"cat {raw_findings} | httpx -silent -mc 200 -cl -sc")
    for line in cl_raw.splitlines():
        parts = line.strip().split()
        # httpx output: URL [status-code] [content-length]
        if len(parts) >= 2:
            url = parts[0]
            # last token = content-length, second-to-last = status if 3 tokens
            cl  = parts[-1]
            sc  = parts[-2] if len(parts) >= 3 else "200"
            cl_map[url] = (sc, cl)

    seen_cls   = defaultdict(set)
    unique_entries = []   # list of (url, status, cl)
    for url, (sc, cl) in cl_map.items():
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        if cl not in seen_cls[domain]:
            seen_cls[domain].add(cl)
            # Human-readable size
            try:
                cl_int = int(cl)
                if cl_int >= 1048576:
                    size_str = f"{cl_int/1048576:.1f} MB"
                elif cl_int >= 1024:
                    size_str = f"{cl_int/1024:.1f} KB"
                else:
                    size_str = f"{cl_int} B"
            except Exception:
                size_str = cl
            unique_entries.append((url, sc, cl, size_str))

    # Save as: URL|STATUS|CL_BYTES|SIZE_HUMAN
    with open(filtered_findings, "w") as f:
        for url, sc, cl, size_str in unique_entries:
            f.write(f"{url}|{sc}|{cl}|{size_str}\n")

    success(f"Unique sensitive path findings: {len(unique_entries)}")
    for url, sc, cl, size_str in unique_entries:
        finding(f"SENSITIVE PATH [{sc}] [{size_str}] → {url}")

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3 — URL COLLECTION (Wayback, GoSpider, Katana)
# ─────────────────────────────────────────────────────────────────────────────
def phase_url_collection(live_domains: list, subfinder_file: str, dirs: dict, missing_tools: list):
    phase("Phase 3 — URL Collection (Wayback / GoSpider / Katana)")
    all_urls = set()

    # Waybackurls
    wb_out = os.path.join(dirs["wayback"], "wayback_urls.txt")
    if "waybackurls" not in missing_tools:
        info("Collecting URLs from Wayback Machine...")
        subs_file = subfinder_file
        run(f"cat {subs_file} | waybackurls | tee {wb_out}")
        wb_urls = [l.strip() for l in open(wb_out).readlines() if l.strip()] if os.path.exists(wb_out) else []
        all_urls.update(wb_urls)
        success(f"Waybackurls → {len(wb_urls)} URLs")
    else:
        warn("waybackurls not found — skipping")

    # GoSpider
    gs_out = os.path.join(dirs["gospider"], "gospider_output")
    gs_urls_file = os.path.join(dirs["gospider"], "gospider_urls.txt")
    if "gospider" not in missing_tools and live_domains:
        sites_file = os.path.join(dirs["gospider"], "sites.txt")
        with open(sites_file, "w") as f:
            for d in live_domains:
                d = d.strip()
                if not d.startswith("http"):
                    d = "https://" + d
                f.write(d + "\n")
        info("Running GoSpider...")
        run(f"gospider -S {sites_file} -o {gs_out} -c 10 -d 1 --quiet 2>/dev/null")
        # Parse gospider output files
        gs_urls = set()
        if os.path.isdir(gs_out):
            for fname in os.listdir(gs_out):
                fpath = os.path.join(gs_out, fname)
                try:
                    with open(fpath) as f:
                        for line in f:
                            m = re.search(r'\[url\]\s*-\s*\[.*?\]\s*-\s*(https?://\S+)', line)
                            if m:
                                gs_urls.add(m.group(1).strip())
                            elif line.startswith("http"):
                                gs_urls.add(line.strip())
                except Exception:
                    pass
        with open(gs_urls_file, "w") as f:
            f.write("\n".join(gs_urls) + "\n")
        all_urls.update(gs_urls)
        success(f"GoSpider → {len(gs_urls)} URLs")
    else:
        warn("gospider not found or no live domains — skipping")

    # Katana
    katana_out = os.path.join(dirs["katana"], "katana_urls.txt")
    if "katana" not in missing_tools:
        subs_file = subfinder_file
        info("Running Katana...")
        run(f"cat {subs_file} | katana -silent 2>/dev/null | tee {katana_out}")
        katana_urls = [l.strip() for l in open(katana_out).readlines() if l.strip()] if os.path.exists(katana_out) else []
        all_urls.update(katana_urls)
        success(f"Katana → {len(katana_urls)} URLs")
    else:
        warn("katana not found — skipping")

    # ── Combine all URLs ─────────────────────────────────────────────────
    combined_file = os.path.join(dirs["combined"], "urls.txt")
    with open(combined_file, "w") as f:
        f.write("\n".join(sorted(all_urls)) + "\n")
    success(f"Combined unique URLs: {len(all_urls)}")

    # ── Build source_map: js_url → list of pages it was found on ─────────
    # Parse gospider output which records [source] → [discovered_url]
    # gospider line format: [url] - [status] - [source_page] - discovered_url
    # OR:                   [linkfinder] - [source_page] - discovered_url
    from collections import defaultdict as _ddsm
    source_map = _ddsm(set)   # js_url -> set of source pages

    if os.path.isdir(gs_out):
        for fname in os.listdir(gs_out):
            fpath = os.path.join(gs_out, fname)
            try:
                with open(fpath) as fh:
                    for line in fh:
                        line = line.strip()
                        # Pattern: [url] - [200] - https://source.com - https://cdn.x.com/a.js
                        m1 = re.search(
                            r'\[(?:url|linkfinder|form)\]\s*-\s*\[.*?\]\s*-\s*(https?://\S+)\s*-\s*(https?://\S+)',
                            line
                        )
                        if m1:
                            source_page   = m1.group(1).strip()
                            discovered    = m1.group(2).strip()
                            if discovered.endswith(".js") or ".js?" in discovered:
                                source_map[discovered].add(source_page)
                            continue
                        # Simpler pattern: [url] - [200] - https://cdn.x.com/a.js
                        m2 = re.search(
                            r'\[url\]\s*-\s*\[.*?\]\s*-\s*(https?://\S+)',
                            line
                        )
                        if m2:
                            discovered = m2.group(1).strip()
                            # source is the spider seed = the filename is the domain
                            seed = os.path.splitext(fname)[0]
                            if not seed.startswith("http"):
                                seed = "https://" + seed
                            if discovered.endswith(".js") or ".js?" in discovered:
                                source_map[discovered].add(seed)
            except Exception:
                pass

    # Also infer from katana output lines (katana prints source→url with -field endpoint)
    # Katana plain output is just discovered URLs — infer source from subdomain match
    for url in all_urls:
        if not (url.endswith(".js") or ".js?" in url):
            continue
        parsed = urllib.parse.urlparse(url)
        js_host = parsed.netloc
        # If the JS host matches a live domain exactly, the page is likely the root
        for live in live_domains:
            live_clean = live.strip()
            if not live_clean.startswith("http"):
                live_clean = "https://" + live_clean
            live_host = urllib.parse.urlparse(live_clean).netloc
            if live_host and (live_host == js_host or js_host.endswith("." + live_host)):
                source_map[url].add(live_clean)

    # Save source_map for debugging
    source_map_file = os.path.join(dirs["combined"], "js_source_map.json")
    with open(source_map_file, "w") as f:
        json.dump({k: list(v) for k, v in source_map.items()}, f, indent=2)
    js_with_sources = sum(1 for v in source_map.values() if v)
    info(f"Source map built: {js_with_sources} JS URLs have known source pages")

    return combined_file, list(all_urls), dict(source_map)

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4 — URL FILTERING (Extensions + Keywords)
# ─────────────────────────────────────────────────────────────────────────────
SENSITIVE_EXTENSIONS = (
    r"\.(xls|xlsx|tar\.gz|bak|backup|xml|json|rar|pdf|sql|doc|docx|pptx|"
    r"txt|zip|tgz|7z|csv|log|conf|config|db|old|java|htaccess|env|pem|key|p12|pfx)$"
)

WAYBACK_KEYWORDS = [
    "admin", "pwd", ".js", ".json", "/api", "config", "auth", "key",
    "dev", "uri", "id=", ".sql", "token", "s3", "env", "access", "git",
    "app.js", "dir", "path", "cdn", "config.js", "proxy", "oauth", "saml",
    "awskey", "secretkey", ".conf", ".csv", "redirect=", "metrics", ".db",
    ".txt", "filepicker_key", "firebase", "webhook", "password", "secret",
    "apikey", "api_key", "client_secret", "bearer", "authorization",
    "private_key", "access_token", "refresh_token", "consumer_key",
]

def phase_filter_urls(combined_file: str, dirs: dict):
    phase("Phase 4 — URL Filtering (Extensions & Keywords)")
    all_urls = [l.strip() for l in open(combined_file).readlines() if l.strip()]

    # Filter by sensitive extensions
    ext_filtered = [u for u in all_urls if re.search(SENSITIVE_EXTENSIONS, u, re.IGNORECASE)]
    ext_file = os.path.join(dirs["combined"], "sensitive_extension_urls.txt")
    with open(ext_file, "w") as f:
        f.write("\n".join(ext_filtered) + "\n")
    success(f"Sensitive extension URLs: {len(ext_filtered)}")

    # Filter by keywords
    kw_pattern = "|".join(re.escape(k) for k in WAYBACK_KEYWORDS)
    kw_filtered = [u for u in all_urls if re.search(kw_pattern, u, re.IGNORECASE)]
    kw_file = os.path.join(dirs["combined"], "keyword_urls.txt")
    with open(kw_file, "w") as f:
        f.write("\n".join(kw_filtered) + "\n")
    success(f"Keyword-matched URLs: {len(kw_filtered)}")

    # Live URL check (httpx mc 200)
    live_file = os.path.join(dirs["combined"], "liveurls.txt")
    info("Probing combined URLs for HTTP 200 responses...")
    run(f"cat {combined_file} | httpx -silent -mc 200 -o {live_file}")
    live_count = len(open(live_file).readlines()) if os.path.exists(live_file) else 0
    success(f"Live 200-OK URLs: {live_count}")

    # Content-type filter
    ct_file = os.path.join(dirs["combined"], "finalurls_with_ct.txt")
    run(f"cat {combined_file} | httpx -silent -mc 200 -ct -o {ct_file}")

    # Secret pattern filter (advanced regex)
    secret_pattern = (
        r"(?:access_key|access_token|admin_pass|admin_user|algolia_admin_key|algolia_api_key|"
        r"alias_pass|alicloud_access_key|amazon_secret_access_key|amazonaws|ansible_vault_password|"
        r"aos_key|api_key|api_key_secret|api_key_sid|api_secret|apikey|apiSecret|app_debug|app_id|"
        r"app_key|app_secret|appkey|appkeysecret|application_key|appsecret|auth_token|"
        r"authorizationToken|authsecret|aws_access|aws_access_key_id|aws_bucket|aws_key|aws_secret|"
        r"aws_secret_key|aws_token|AWSSecretKey|client_secret|consumer_key|consumer_secret|"
        r"credentials|database_password|db_password|db_username|dbpasswd|dbpassword|dbuser|"
        r"deploy_password|docker_password|encryption_key|encryption_password|"
        r"api\.googlemaps AIza)[a-z0-9_.,-]{0,25})[:<>=|]{1,2}.{0,5}['\"]([0-9A-Za-z\-_=]{8,64})['\"]"
    )
    secret_urls = []
    for u in all_urls:
        try:
            if re.search(secret_pattern, u, re.IGNORECASE):
                secret_urls.append(u)
        except Exception:
            pass
    secret_file = os.path.join(dirs["combined"], "secret_pattern_urls.txt")
    with open(secret_file, "w") as f:
        f.write("\n".join(secret_urls) + "\n")
    success(f"Secret-pattern URLs: {len(secret_urls)}")

    # Extract JS URLs
    js_urls = [u for u in all_urls if re.search(r'\.js(\?.*)?$', u, re.IGNORECASE)]
    js_file = os.path.join(dirs["js"], "js_urls.txt")
    with open(js_file, "w") as f:
        f.write("\n".join(sorted(set(js_urls))) + "\n")
    success(f"JS file URLs extracted: {len(set(js_urls))}")

    return js_file, list(set(js_urls))

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 5 — JS FILE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

# Comprehensive keyword set for JS secret hunting
JS_KEYWORDS = {
    "Authentication & Tokens": [
        r"(?:api[_\-]?key|apikey|api[_\-]?secret)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-]{8,64})",
        r"(?:access[_\-]?token|auth[_\-]?token|bearer[_\-]?token)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-\.]{10,})",
        r"(?:secret[_\-]?key|secret[_\-]?token|client[_\-]?secret)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-\.]{8,})",
        r"Authorization[\"'\s]*[:=][\"'\s]*(?:Bearer\s+)?([a-zA-Z0-9_\-\.]{20,})",
        r"(?:refresh[_\-]?token)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-\.]{10,})",
        r"(?:id[_\-]?token|session[_\-]?token)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-\.]{10,})",
    ],
    "AWS & Cloud": [
        r"AKIA[0-9A-Z]{16}",
        r"(?:aws[_\-]?access[_\-]?key[_\-]?id|AWS_ACCESS_KEY_ID)[\"'\s]*[:=][\"'\s]*([A-Z0-9]{20})",
        r"(?:aws[_\-]?secret[_\-]?access[_\-]?key|AWS_SECRET_ACCESS_KEY)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9/+=]{40})",
        r"(?:aws[_\-]?session[_\-]?token)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9/+=]{100,})",
        r"s3\.amazonaws\.com[/\"]?([a-zA-Z0-9\-_]{3,63})",
        r"(?:bucket|s3[_\-]?bucket)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9\-_\.]{3,63})",
    ],
    "Database": [
        r"(?:db[_\-]?password|database[_\-]?password|mysql[_\-]?pass|dbpass)[\"'\s]*[:=][\"'\s]*([^\s\"']{4,})",
        r"(?:jdbc:mysql|jdbc:postgresql|jdbc:oracle|jdbc:mssql)://[^\s\"']+",
        r"mongodb(?:\+srv)?://[^\s\"']+",
        r"(?:connection[_\-]?string)[\"'\s]*[:=][\"'\s]*([^\s\"']{10,})",
        r"(?:db[_\-]?user|database[_\-]?user|db[_\-]?username)[\"'\s]*[:=][\"'\s]*([^\s\"']{2,})",
        r"(?:redis://|postgresql://|mysql://)[^\s\"']+",
    ],
    "OAuth & SSO": [
        r"(?:client[_\-]?id)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9\-_]{8,})",
        r"(?:oauth[_\-]?token|oauth[_\-]?secret)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-\.]{8,})",
        r"(?:saml|openid|oidc)[^\n\"']{0,100}(?:secret|key|token)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-\.]{8,})",
    ],
    "Firebase & Google": [
        r"AIza[0-9A-Za-z\-_]{35}",
        r"(?:firebase[_\-]?api[_\-]?key|FIREBASE_API_KEY)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-]{20,})",
        r"(?:firebase[_\-]?auth[_\-]?domain)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9\-\.]+\.firebaseapp\.com)",
        r"(?:storageBucket)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9\-\.]+\.appspot\.com)",
        r"(?:messagingSenderId|appId)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9:_\-\.]+)",
    ],
    "Passwords & Credentials": [
        r"(?:password|passwd|pwd)[\"'\s]*[:=][\"'\s]*([^\s\"']{4,})",
        r"(?:admin[_\-]?password|root[_\-]?password)[\"'\s]*[:=][\"'\s]*([^\s\"']{4,})",
        r"(?:credentials|creds)[\"'\s]*[:=]\s*\{[^}]{0,200}\}",
    ],
    "Private Keys & Certificates": [
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        r"-----BEGIN CERTIFICATE-----",
        r"(?:private[_\-]?key|pem[_\-]?key)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9/+=\-]{20,})",
    ],
    "Webhooks & Integrations": [
        r"https://hooks\.slack\.com/services/[A-Z0-9/]+",
        r"https://discord\.com/api/webhooks/[0-9]+/[a-zA-Z0-9\-_]+",
        r"(?:webhook[_\-]?url|WEBHOOK_URL)[\"'\s]*[:=][\"'\s]*(https?://[^\s\"']+)",
        r"https://api\.telegram\.org/bot[a-zA-Z0-9:_\-]+",
    ],
    "API Endpoints & URLs": [
        r"(?:api[_\-]?url|base[_\-]?url|api[_\-]?base|endpoint)[\"'\s]*[:=][\"'\s]*(https?://[^\s\"']+)",
        r"(?:apiURL|baseURL|API_URL|BASE_URL)[\"'\s]*[:=][\"'\s]*(https?://[^\s\"']+)",
        r"(?:/api/v[0-9]+/[^\s\"']+)",
        r"(?:graphql|gql)[\"'\s]*[:=][\"'\s]*(https?://[^\s\"']+)",
    ],
    "Environment & Config": [
        r"(?:NODE_ENV|APP_ENV|ENVIRONMENT)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-]+)",
        r"(?:\.env|env\.[a-z]+)[\"'\s]*",
        r"process\.env\.([A-Z_]{3,})\s*",
        r"(?:config\.js|config\.json|settings\.json)[\"'\s]",
    ],
    "Developer Secrets (Extended)": [
        r"(?:stripe[_\-]?key|stripe[_\-]?secret)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_\-]{20,})",
        r"sk_(?:live|test)_[a-zA-Z0-9]{24,}",
        r"pk_(?:live|test)_[a-zA-Z0-9]{24,}",
        r"(?:twilio[_\-]?(?:account[_\-]?sid|auth[_\-]?token))[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9]{20,})",
        r"(?:sendgrid[_\-]?api[_\-]?key)[\"'\s]*[:=][\"'\s]*(SG\.[a-zA-Z0-9_\-\.]{20,})",
        r"(?:mailgun[_\-]?api[_\-]?key)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9\-]{20,})",
        r"(?:github[_\-]?token|GH_TOKEN|GITHUB_TOKEN)[\"'\s]*[:=][\"'\s]*(ghp_[a-zA-Z0-9]{36}|[a-zA-Z0-9]{40})",
        r"(?:jwt[_\-]?secret|JWT_SECRET)[\"'\s]*[:=][\"'\s]*([^\s\"']{8,})",
        r"(?:encryption[_\-]?key|ENCRYPTION_KEY)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9/+=]{16,})",
        r"(?:app[_\-]?id|application[_\-]?id|APP_ID)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9\-_]{4,})",
        r"(?:heroku[_\-]?api[_\-]?key)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9\-]{30,})",
        r"(?:datadog|newrelic|sentry)[_\-]?(?:api[_\-]?)?key[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9\-_]{20,})",
    ],
}

# URL pattern inside JS
JS_URL_PATTERN = re.compile(
    r'(?:url|href|src|endpoint|path|redirect|location|action)\s*[:=]\s*["\']'
    r'((?:https?://|/)[^\s"\'<>]+)["\']'
    r'|["\']((https?://)[^\s"\'<>]{5,})["\']',
    re.IGNORECASE
)

# API endpoint pattern inside JS
JS_API_PATTERN = re.compile(
    r'["\']'
    r'(/(?:api|v[0-9]+|graphql|rest|service|endpoint|auth|oauth|admin|internal)'
    r'(?:/[a-zA-Z0-9_\-\.{}/:?=&%]+)?)'
    r'["\']',
    re.IGNORECASE
)

def beautify_js(content: str) -> str:
    """Simple JS beautifier — expand braces and add newlines."""
    try:
        import jsbeautifier
        return jsbeautifier.beautify(content)
    except ImportError:
        # Fallback: basic formatting
        content = re.sub(r';(?!\n)', ';\n', content)
        content = re.sub(r'\{(?!\n)', '{\n', content)
        content = re.sub(r'\}(?!\n)', '\n}\n', content)
        return content

def analyze_js_file(url: str, dirs: dict, found_on: list = None) -> dict:
    """Download and analyze a single JS file."""
    parsed_url = urllib.parse.urlparse(url)
    parent_domain = parsed_url.netloc  # e.g. cdn.example.com
    base_domain   = ".".join(parent_domain.split(".")[-2:]) if parent_domain else ""  # example.com
    result = {
        "url":           url,
        "parent_domain": parent_domain,
        "base_domain":   base_domain,
        "found_on":      sorted(found_on) if found_on else [],  # source pages
        "secrets": {},
        "urls_found":    [],
        "api_endpoints": [],
        "full_endpoints": [],   # full URLs = base_domain + path
        "downloaded":    False,
        "size":          0,
        "sha256":        "",
    }
    try:
        # Download the JS file
        resp = subprocess.run(
            ["curl", "-sL", "--max-time", "15", "-A",
             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
             "-H", "Accept: */*", url],
            capture_output=True, text=True, timeout=20
        )
        content = resp.stdout
        if not content or len(content) < 10:
            return result

        result["downloaded"] = True
        result["size"] = len(content)
        result["sha256"] = hashlib.sha256(content.encode()).hexdigest()

        # Beautify
        beautified = beautify_js(content)

        # Save beautified JS
        safe_name = re.sub(r'[^\w\-_\.]', '_', url.replace("https://", "").replace("http://", ""))[:100]
        js_save_path = os.path.join(dirs["js"], "downloaded", safe_name + ".js")
        os.makedirs(os.path.dirname(js_save_path), exist_ok=True)
        with open(js_save_path, "w", errors="replace") as f:
            f.write(beautified)

        # Scan for secrets
        for category, patterns in JS_KEYWORDS.items():
            matches = []
            for pattern in patterns:
                try:
                    for m in re.finditer(pattern, beautified, re.IGNORECASE | re.MULTILINE):
                        match_str = m.group(0).strip()
                        if len(match_str) > 5:
                            matches.append(match_str)
                except re.error:
                    pass
            if matches:
                result["secrets"][category] = list(set(matches))

        # Extract URLs
        found_urls = []
        for m in JS_URL_PATTERN.finditer(beautified):
            for group in m.groups():
                if group and len(group) > 5:
                    found_urls.append(group)
        result["urls_found"] = list(set(found_urls))

        # Extract API endpoints
        api_eps = []
        for m in JS_API_PATTERN.finditer(beautified):
            ep = m.group(1)
            if ep and len(ep) > 3:
                api_eps.append(ep)
        result["api_endpoints"] = list(set(api_eps))

        # Build full URLs for each endpoint using the JS file's origin
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        full_eps = []
        for ep in result["api_endpoints"]:
            if ep.startswith("http"):
                full_eps.append(ep)
            else:
                full_eps.append(origin.rstrip("/") + "/" + ep.lstrip("/"))
        result["full_endpoints"] = list(set(full_eps))

    except Exception as e:
        pass

    return result

def phase_js_analysis(js_urls: list, dirs: dict, source_map: dict = None):
    phase("Phase 5 — JavaScript File Analysis")

    if not js_urls:
        warn("No JS URLs to analyze")
        return

    source_map = source_map or {}
    info(f"Analyzing {len(js_urls)} JS files...")
    all_results = []
    all_secrets = []
    all_js_urls = []
    all_endpoints = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(
                analyze_js_file, url, dirs,
                list(source_map.get(url, []))
            ): url
            for url in js_urls
        }
        done = 0
        for future in as_completed(futures):
            url = futures[future]
            done += 1
            try:
                result = future.result()
                all_results.append(result)
                if result["secrets"]:
                    finding(f"[{done}/{len(js_urls)}] SECRETS FOUND → {url}")
                    for cat, matches in result["secrets"].items():
                        print(f"    {C.YELLOW}[{cat}]{C.RESET}")
                        for m in matches[:3]:
                            print(f"      {C.RED}{m[:120]}{C.RESET}")
                    all_secrets.append(result)
                else:
                    if done % 10 == 0:
                        info(f"Progress: {done}/{len(js_urls)} JS files analyzed")
                all_js_urls.extend(result["urls_found"])
                all_endpoints.extend(result["api_endpoints"])
            except Exception:
                pass

    # ── Write secrets report (grouped: domain → JS URL → secrets) ───────
    secrets_report = os.path.join(dirs["secrets"], "js_secrets.txt")
    secrets_json   = os.path.join(dirs["secrets"], "js_secrets.json")

    # Group by base_domain
    from collections import defaultdict as _dd
    by_domain = _dd(list)
    for item in all_secrets:
        by_domain[item.get("base_domain", "unknown")].append(item)

    all_full_endpoints = []
    with open(secrets_report, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("  JSRecon Cyborg Edition V1 — by Rahul Masal\n")
        f.write(f"  JS Secrets Report  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        if not all_secrets:
            f.write("No secrets found.\n")
        else:
            for domain in sorted(by_domain.keys()):
                items = by_domain[domain]
                f.write(f"\n{'█'*80}\n")
                f.write(f"  DOMAIN : {domain}  ({len(items)} JS file(s) with secrets)\n")
                f.write(f"{'█'*80}\n")
                for item in items:
                    f.write(f"\n  {'─'*76}\n")
                    f.write(f"  JS URL   : {item['url']}\n")
                    f.write(f"  Host     : {item.get('parent_domain','')}\n")
                    f.write(f"  Size     : {item['size']:,} bytes\n")
                    f.write(f"  SHA256   : {item['sha256']}\n")
                    # ── Found on (source pages) ───────────────────────────
                    found_on_list = item.get("found_on", [])
                    if found_on_list:
                        f.write(f"  Found on :\n")
                        for src in found_on_list[:10]:
                            f.write(f"    → {src}\n")
                    else:
                        f.write(f"  Found on : (source page not tracked)\n")
                    f.write(f"  {'─'*76}\n")
                    for cat, matches in item["secrets"].items():
                        sev, score, _ = get_severity(cat)
                        f.write(f"\n    ┌─ [{sev}] {cat} (CVSS {score}) \n")
                        for m in matches:
                            f.write(f"    │  {m[:200]}\n")
                        f.write(f"    └{'─'*60}\n")
                    if item.get("full_endpoints"):
                        f.write(f"\n    ┌─ API Endpoints from this JS file\n")
                        for ep in item["full_endpoints"][:20]:
                            f.write(f"    │  {ep}\n")
                            all_full_endpoints.append(ep)
                        f.write(f"    └{'─'*60}\n")
                f.write("\n")

    with open(secrets_json, "w") as f:
        json.dump(all_secrets, f, indent=2, default=str)

    success(f"Secrets written (grouped by domain) → {secrets_report}")

    # ── Write extracted URLs from JS ─────────────────────────────────────
    js_file_urls = os.path.join(dirs["js"], "jsfileurls.txt")
    with open(js_file_urls, "w") as f:
        f.write("\n".join(sorted(set(all_js_urls))) + "\n")
    success(f"URLs extracted from JS files: {len(set(all_js_urls))} → {js_file_urls}")

    # ── Write API endpoints as FULL URLs ──────────────────────────────────
    # Collect full_endpoints from ALL results (not just secret ones)
    for item in all_results:
        if item:
            all_full_endpoints.extend(item.get("full_endpoints", []))
            # Also raw paths for reference
            all_endpoints.extend(item.get("api_endpoints", []))

    ep_file      = os.path.join(dirs["endpoints"], "api_endpoints_full.txt")
    ep_file_raw  = os.path.join(dirs["endpoints"], "api_endpoints_paths.txt")
    with open(ep_file, "w") as f:
        f.write("\n".join(sorted(set(all_full_endpoints))) + "\n")
    with open(ep_file_raw, "w") as f:
        f.write("\n".join(sorted(set(all_endpoints))) + "\n")
    # Keep legacy filename pointing to full URLs for report compatibility
    import shutil as _sh
    _sh.copy2(ep_file, os.path.join(dirs["endpoints"], "api_endpoints.txt"))
    success(f"API endpoints (full URLs): {len(set(all_full_endpoints))} → {ep_file}")

    return all_results

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 6 — SCREENSHOTS with GoWitness
# ─────────────────────────────────────────────────────────────────────────────
def _gowitness_version() -> int:
    """
    Detect gowitness major version by inspecting help output.
    v3: top-level commands are 'scan', 'report', 'version'
        file scanning is: gowitness scan file -f <file>
    v2: top-level command is 'file'
        file scanning is: gowitness file -f <file>
    Returns 3, 2, or 0 if not found.
    """
    try:
        out = subprocess.run(
            ["gowitness", "--help"],
            capture_output=True, text=True, timeout=10
        )
        combined = (out.stdout + out.stderr).lower()
        # v3 shows 'scan' as a top-level command, no 'file' at top level
        if "perform various scans" in combined or (
            "scan" in combined and "file" not in combined.split("available commands")[1][:200]
            if "available commands" in combined else False
        ):
            return 3
        # v3 fallback: check scan subcommand
        out2 = subprocess.run(
            ["gowitness", "scan", "--help"],
            capture_output=True, text=True, timeout=10
        )
        if out2.returncode == 0 and "file" in (out2.stdout + out2.stderr).lower():
            return 3
        # v2: has 'file' as a direct subcommand
        if "file" in combined:
            return 2
    except Exception:
        pass
    return 0


def _find_chrome() -> str:
    """
    Find any usable Chrome/Chromium binary on this system.
    Returns the full path, or empty string if none found.
    """
    candidates = [
        "chromium", "chromium-browser",
        "google-chrome", "google-chrome-stable",
        "/usr/bin/chromium", "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
        "/snap/bin/chromium",
        # WSL / Kali paths
        "/usr/bin/chromium-browser",
        "/usr/lib/chromium/chromium",
        "/usr/lib/chromium-browser/chromium-browser",
    ]
    for c in candidates:
        if shutil.which(c) or os.path.isfile(c):
            return shutil.which(c) or c
    return ""


def _ensure_chrome(dirs: dict) -> str:
    """
    Try to auto-install Chromium if not present.
    Returns the path to a working Chrome binary, or empty string.
    """
    found = _find_chrome()
    if found:
        return found

    warn("Chrome/Chromium not found — attempting auto-install...")
    # Try apt (Debian/Ubuntu/Kali)
    for pkg in ["chromium", "chromium-browser"]:
        ret = os.system(f"apt-get install -y {pkg} -qq 2>/dev/null")
        if ret == 0:
            found = _find_chrome()
            if found:
                success(f"Chromium installed: {found}")
                return found
    warn("Auto-install failed. Install manually:")
    warn("  Ubuntu/Kali : apt install -y chromium-browser")
    warn("  Or download : https://www.google.com/chrome/")
    return ""


def _run_gowitness(version: int, sites_file: str, screenshot_dir: str,
                   threads: int = 5, timeout: int = 15,
                   chrome_path: str = "") -> bool:
    """
    Run gowitness v3 (only — v2 is fully deprecated).
    v3 syntax: gowitness scan file -f <file> -s <dir> -t N -T N [--chrome-path X]
    Returns True if at least one screenshot was produced.
    """
    abs_sites = os.path.abspath(sites_file)
    abs_dir   = os.path.abspath(screenshot_dir)

    chrome_flag = f"--chrome-path {chrome_path} " if chrome_path else ""

    # v3 only — the 'file' sub-subcommand lives under 'scan'
    cmd = (
        f"gowitness scan file -f {abs_sites} "
        f"-s {abs_dir} "            # -s / --screenshot-path
        f"-t {threads} "
        f"-T {timeout} "
        f"--write-none "            # no db/csv/jsonl — screenshots only
        f"--screenshot-format png " # ensure PNG output
        f"{chrome_flag}"
        f"-q "                      # quiet
        f"2>&1"
    )

    info(f"gowitness cmd: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=False,
                            text=True, timeout=900)

    if result.returncode != 0:
        # Capture stderr for diagnosis
        result2 = subprocess.run(cmd.replace("2>&1",""), shell=True,
                                 capture_output=True, text=True, timeout=30)
        stderr_out = (result2.stdout + result2.stderr)[:400]
        warn(f"gowitness exited {result.returncode}: {stderr_out[:200]}")
        return False
    return True


def _run_aquatone(sites_file: str, screenshot_dir: str,
                  threads: int = 5, timeout: int = 15) -> bool:
    """
    Run Aquatone as fallback screenshot tool.
    Correct Aquatone flags (all in milliseconds):
      -threads N
      -screenshot-timeout N   (ms, not seconds)
      -http-timeout N         (ms)
      -scan-timeout N         (ms)
      -out <dir>
    Aquatone reads URLs from stdin.
    """
    abs_dir   = os.path.abspath(screenshot_dir)
    abs_sites = os.path.abspath(sites_file)

    # Aquatone timeouts are in MILLISECONDS
    screenshot_ms = timeout * 1000
    http_ms       = max(timeout * 500, 3000)   # at least 3s

    cmd = (
        f"cat {abs_sites} | "
        f"aquatone "
        f"-out {abs_dir} "
        f"-threads {threads} "
        f"-screenshot-timeout {screenshot_ms} "
        f"-http-timeout {http_ms} "
        f"-silent "
        f"2>&1"
    )
    info(f"aquatone cmd: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, text=True, timeout=900
        )
        if result.returncode != 0:
            warn(f"aquatone exited {result.returncode}")
            return False
        return True
    except subprocess.TimeoutExpired:
        warn("aquatone timed out")
        return False
    except Exception as e:
        error(f"aquatone error: {e}")
        return False


def _collect_screenshots(screenshot_dir: str) -> list:
    """
    Collect all PNG/JPEG screenshots from screenshot_dir and any subdirs.
    Aquatone saves to <dir>/screenshots/, gowitness saves directly to <dir>.
    """
    screens = []
    for root, dirs_, files in os.walk(screenshot_dir):
        for fname in files:
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                rel = os.path.relpath(os.path.join(root, fname), screenshot_dir)
                screens.append(rel)
    return sorted(screens)


def _build_screenshot_html(screenshot_dir: str, screens: list,
                            live_domains: list, tool_used: str,
                            target_name: str) -> str:
    """Build the screenshot HTML gallery. Returns path to report file."""
    report_html = os.path.join(screenshot_dir, "screenshot_report.html")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cards = ""
    for rel in screens:
        fname = os.path.basename(rel)
        cards += f"""
  <div class="card" data-name="{rel.lower()}">
    <img src="{rel}" loading="lazy" alt="{fname}" onclick="openLB(this.src)">
    <div class="meta">
      <div class="fname">{rel[:90]}</div>
    </div>
  </div>"""

    if not cards:
        cards = """<div class="empty" style="grid-column:1/-1">
    <h2>⚠ No screenshots captured</h2>
    <p>Make sure Chrome/Chromium is installed and reachable targets exist.</p>
    <p style="margin-top:8px;font-size:11px">
      Debug: <code>gowitness scan single -u https://example.com</code>
    </p></div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Screenshots — JSRecon {target_name}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0d1117;color:#c9d1d9;font-family:'Courier New',monospace;padding:20px}}
header{{border-bottom:1px solid #30363d;padding-bottom:14px;margin-bottom:20px}}
header h1{{color:#58a6ff;font-size:20px}}
header p{{color:#8b949e;font-size:11px;margin-top:5px}}
.bar{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:18px;align-items:center}}
.stat{{background:#161b22;border:1px solid #30363d;border-radius:6px;
       padding:8px 16px;text-align:center}}
.stat .n{{font-size:22px;font-weight:bold;color:#58a6ff}}
.stat .l{{font-size:10px;color:#8b949e;margin-top:2px}}
.search input{{background:#161b22;border:1px solid #30363d;border-radius:5px;
               color:#c9d1d9;padding:7px 12px;width:340px;font-family:inherit;
               font-size:12px;outline:none}}
.search input:focus{{border-color:#58a6ff}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:14px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:7px;overflow:hidden;
       transition:border-color .2s}}
.card:hover{{border-color:#58a6ff}}
.card img{{width:100%;display:block;cursor:zoom-in;border-bottom:1px solid #30363d;
           background:#0d1117;min-height:40px}}
.meta{{padding:8px 10px}}
.fname{{color:#8b949e;font-size:10px;word-break:break-all}}
.empty{{text-align:center;padding:50px;color:#484f58}}
.empty h2{{color:#8b949e;font-size:16px;margin-bottom:8px}}
.lb{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.93);
     z-index:9999;align-items:center;justify-content:center;cursor:zoom-out}}
.lb.on{{display:flex}}
.lb img{{max-width:95vw;max-height:95vh;border-radius:5px}}
.lb-x{{position:fixed;top:12px;right:18px;color:#fff;font-size:24px;cursor:pointer;z-index:10000}}
footer{{border-top:1px solid #30363d;padding:14px;color:#8b949e;font-size:10px;
        text-align:center;margin-top:30px}}
</style>
</head>
<body>
<header>
  <h1>📸 Visual Reconnaissance</h1>
  <p>JSRecon Cyborg V1 — by <strong style="color:#f85149">Rahul Masal</strong>
     &nbsp;·&nbsp; Target: <strong style="color:#58a6ff">{target_name}</strong>
     &nbsp;·&nbsp; Tool: <strong style="color:#a78bfa">{tool_used}</strong>
     &nbsp;·&nbsp; {now_str}</p>
</header>
<div class="bar">
  <div class="stat"><div class="n">{len(live_domains)}</div><div class="l">Targets</div></div>
  <div class="stat"><div class="n" id="vis-cnt">{len(screens)}</div><div class="l">Captured</div></div>
  <div class="stat"><div class="n">{len(live_domains)-len(screens)}</div><div class="l">Failed</div></div>
  <div class="search">
    <input type="text" id="q" placeholder="🔍 filter by filename..." oninput="doFilter()">
  </div>
</div>
<div class="grid" id="grid">{cards}</div>
<div class="lb" id="lb" onclick="closeLB()">
  <span class="lb-x" onclick="closeLB()">✕</span>
  <img id="lb-img" src="" alt="">
</div>
<footer>JSRecon Cyborg V1 · Rahul Masal · {now_str}</footer>
<script>
function openLB(s){{document.getElementById("lb-img").src=s;document.getElementById("lb").classList.add("on")}}
function closeLB(){{document.getElementById("lb").classList.remove("on");document.getElementById("lb-img").src=""}}
document.addEventListener("keydown",e=>{{if(e.key==="Escape")closeLB()}})
function doFilter(){{
  const q=document.getElementById("q").value.toLowerCase();
  let n=0;
  document.querySelectorAll(".card").forEach(c=>{{
    const show=!q||c.dataset.name.includes(q);
    c.style.display=show?"":"none";
    if(show)n++;
  }});
  document.getElementById("vis-cnt").textContent=n;
}}
</script>
</body></html>"""

    with open(report_html, "w", encoding="utf-8") as fh:
        fh.write(html)
    return report_html


def phase_screenshots(live_domains: list, dirs: dict, missing_tools: list):
    phase("Phase 6 — Visual Reconnaissance (Screenshots)")

    if not live_domains:
        warn("No live domains to screenshot")
        return

    screenshot_dir = os.path.join(dirs["screenshots"], "captures")
    os.makedirs(screenshot_dir, exist_ok=True)

    # Write sites file (one URL per line, with http/https)
    sites_file = os.path.join(dirs["screenshots"], "sites.txt")
    with open(sites_file, "w") as fh:
        for d in live_domains:
            d = d.strip()
            if not d.startswith("http"):
                d = "https://" + d
            fh.write(d + "\n")
    info(f"Targets written: {len(live_domains)} → {sites_file}")

    tool_used = "none"
    success_flag = False

    # ── Find / install Chrome — required by both gowitness and aquatone ───
    chrome_path = _ensure_chrome(dirs)
    if chrome_path:
        info(f"Chrome binary: {chrome_path}")
    else:
        warn("No Chrome/Chromium found — screenshots will likely fail")
        warn("  Fix: apt install -y chromium-browser  (Ubuntu/Kali/Debian)")

    # ── Try gowitness (v3 only — v3 shipped Sept 2024) ────────────────────
    if "gowitness" not in missing_tools:
        ver = _gowitness_version()
        info(f"gowitness version detected: v{ver if ver else '?'}")
        # Always use v3 syntax; v2 is completely unsupported on v3 binary
        ver = 3
        success_flag = _run_gowitness(
            ver, sites_file, screenshot_dir,
            chrome_path=chrome_path
        )
        if success_flag:
            tool_used = f"gowitness v{ver}"
        else:
            warn("gowitness failed — check Chrome is installed")

    # ── Collect after gowitness (check before trying aquatone) ────────────
    # gowitness v3 may also write to ./screenshots/ inside cwd
    for extra_dir in [screenshot_dir, os.getcwd(),
                      os.path.join(os.getcwd(), "screenshots")]:
        for fname in os.listdir(extra_dir) if os.path.isdir(extra_dir) else []:
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                src = os.path.join(extra_dir, fname)
                dst = os.path.join(screenshot_dir, fname)
                if src != dst and not os.path.exists(dst):
                    shutil.move(src, dst)

    screens = _collect_screenshots(screenshot_dir)

    # ── Fallback: Aquatone ────────────────────────────────────────────────
    if not screens and "aquatone" not in missing_tools:
        warn("gowitness produced no screenshots — trying Aquatone fallback...")
        aquatone_dir = os.path.join(dirs["screenshots"], "aquatone_out")
        os.makedirs(aquatone_dir, exist_ok=True)
        success_flag = _run_aquatone(sites_file, aquatone_dir)
        if success_flag:
            tool_used = "aquatone"
            # Aquatone saves PNGs to <out>/screenshots/
            aq_screens_dir = os.path.join(aquatone_dir, "screenshots")
            if os.path.isdir(aq_screens_dir):
                for fname in os.listdir(aq_screens_dir):
                    if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                        shutil.copy2(
                            os.path.join(aq_screens_dir, fname),
                            os.path.join(screenshot_dir, fname)
                        )
            # Also copy Aquatone's aquatone_report.html
            aq_html = os.path.join(aquatone_dir, "aquatone_report.html")
            if os.path.exists(aq_html):
                shutil.copy2(aq_html, os.path.join(dirs["screenshots"], "aquatone_report.html"))
                info("Aquatone HTML report also available: aquatone_report.html")
        screens = _collect_screenshots(screenshot_dir)

    # ── Final result ──────────────────────────────────────────────────────
    if screens:
        success(f"Screenshots captured: {len(screens)} (tool: {tool_used}) → {screenshot_dir}")
    else:
        warn("No screenshots captured by any tool.")
        warn("Install Chrome/Chromium, then ensure one of these is in PATH:")
        warn("  gowitness : go install github.com/sensepost/gowitness@latest")
        warn("  aquatone  : go install github.com/michenriksen/aquatone@latest")

    # ── Build HTML gallery ────────────────────────────────────────────────
    report_html = _build_screenshot_html(
        dirs["screenshots"], screens, live_domains,
        tool_used, dirs["base"].split(os.sep)[-1]
    )
    success(f"Screenshot report → {report_html}")


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7 — FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# CONFIG LOADER  (.env file in same directory as the script)
# ─────────────────────────────────────────────────────────────────────────────
def load_config() -> dict:
    """
    Load notification credentials from jsrecon.env.
    Accepts BOTH uppercase and lowercase key names.
    Searches: script dir → cwd → home dir → /etc/jsrecon.env
    """
    cfg = {
        "telegram_bot_token":  "",
        "telegram_chat_id":    "",
        "discord_webhook_url": "",
    }

    # Key aliases: accept any casing or variation
    KEY_ALIASES = {
        "telegram_bot_token":  ["telegram_bot_token", "TELEGRAM_BOT_TOKEN",
                                 "bot_token", "BOT_TOKEN", "tg_token", "TG_TOKEN"],
        "telegram_chat_id":    ["telegram_chat_id",   "TELEGRAM_CHAT_ID",
                                 "chat_id", "CHAT_ID",   "tg_chat_id", "TG_CHAT_ID"],
        "discord_webhook_url": ["discord_webhook_url","DISCORD_WEBHOOK_URL",
                                 "discord_webhook",   "DISCORD_WEBHOOK",
                                 "webhook_url",       "WEBHOOK_URL"],
    }
    # Build reverse lookup: any alias → canonical key
    alias_map = {}
    for canonical, aliases in KEY_ALIASES.items():
        for alias in aliases:
            alias_map[alias.lower()] = canonical

    # Search locations in priority order
    search_paths = []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.append(os.path.join(script_dir, "jsrecon.env"))
    except Exception:
        pass
    search_paths.append(os.path.join(os.getcwd(), "jsrecon.env"))
    search_paths.append(os.path.expanduser("~/.jsrecon.env"))
    search_paths.append("/etc/jsrecon.env")

    env_path = None
    for p in search_paths:
        if os.path.isfile(p):
            env_path = p
            break

    if not env_path:
        warn("─" * 60)
        warn("jsrecon.env NOT FOUND. Telegram/Discord notifications disabled.")
        warn("Searched in:")
        for p in search_paths:
            warn(f"  {p}")
        warn("Fix: create jsrecon.env in the same folder as jsrecon.py")
        warn("Contents needed:")
        warn("  TELEGRAM_BOT_TOKEN=1234567890:ABCdef...")
        warn("  TELEGRAM_CHAT_ID=123456789")
        warn("  DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
        warn("─" * 60)
        return cfg

    success(f"Config file found: {env_path}")

    # Parse the file
    raw_lines = []
    with open(env_path, "r", errors="replace") as f:
        raw_lines = f.readlines()

    for line in raw_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'").strip()

        # Skip empty values and placeholders
        if not v:
            continue
        if any(ph in v.lower() for ph in ["your_", "placeholder", "here", "token_here",
                                            "id_here", "url_here", "example"]):
            warn(f"Placeholder value detected for key: {k} — update jsrecon.env")
            continue

        # Map to canonical key
        canonical = alias_map.get(k.lower())
        if canonical:
            cfg[canonical] = v

    # Report what was loaded
    info("─" * 50)
    info("Notification config status:")
    for key, val in cfg.items():
        if val:
            # Mask middle of token for security
            if len(val) > 10:
                masked = val[:8] + "****" + val[-4:]
            else:
                masked = "****"
            success(f"  {key:25s} = {masked}")
        else:
            warn(f"  {key:25s} = NOT SET")
    info("─" * 50)

    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# SEVERITY ENGINE
# ─────────────────────────────────────────────────────────────────────────────
# Each secret category maps to (severity_label, cvss_score, color_hex)
SEVERITY_MAP = {
    "AWS & Cloud":                    ("CRITICAL", 9.8, "#ff4444"),
    "Private Keys & Certificates":    ("CRITICAL", 9.5, "#ff4444"),
    "Database":                       ("CRITICAL", 9.3, "#ff4444"),
    "Authentication & Tokens":        ("HIGH",     8.5, "#ff8800"),
    "OAuth & SSO":                    ("HIGH",     8.2, "#ff8800"),
    "Firebase & Google":              ("HIGH",     8.0, "#ff8800"),
    "Webhooks & Integrations":        ("HIGH",     7.5, "#ff8800"),
    "Developer Secrets (Extended)":   ("HIGH",     7.8, "#ff8800"),
    "Passwords & Credentials":        ("HIGH",     8.1, "#ff8800"),
    "API Endpoints & URLs":           ("MEDIUM",   5.5, "#ffcc00"),
    "Environment & Config":           ("MEDIUM",   5.0, "#ffcc00"),
}

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}

def get_severity(category: str) -> tuple:
    return SEVERITY_MAP.get(category, ("LOW", 3.5, "#44aaff"))

def overall_severity(secret_cats: list) -> tuple:
    """Return the highest severity across all found categories."""
    best = ("INFO", 0.0, "#888888")
    for cat in secret_cats:
        sev, score, color = get_severity(cat)
        if SEVERITY_ORDER.get(sev, 99) < SEVERITY_ORDER.get(best[0], 99):
            best = (sev, score, color)
    return best


# ─────────────────────────────────────────────────────────────────────────────
# HTML REPORT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def _sev_badge(sev: str) -> str:
    colors = {
        "CRITICAL": ("#ff4444", "#fff"),
        "HIGH":     ("#ff8800", "#fff"),
        "MEDIUM":   ("#ffcc00", "#000"),
        "LOW":      ("#44aaff", "#fff"),
        "INFO":     ("#888888", "#fff"),
    }
    bg, fg = colors.get(sev, ("#888", "#fff"))
    return (f'<span style="background:{bg};color:{fg};padding:2px 10px;'
            f'border-radius:4px;font-size:11px;font-weight:bold;'
            f'letter-spacing:1px">{sev}</span>')

def _score_ring(score: float, color: str) -> str:
    """SVG circular score ring."""
    pct   = score / 10.0
    r     = 36
    circ  = 2 * 3.14159 * r
    dash  = pct * circ
    return f"""
<svg width="90" height="90" viewBox="0 0 90 90">
  <circle cx="45" cy="45" r="{r}" fill="none" stroke="#2d333b" stroke-width="8"/>
  <circle cx="45" cy="45" r="{r}" fill="none" stroke="{color}" stroke-width="8"
          stroke-dasharray="{dash:.1f} {circ:.1f}"
          stroke-linecap="round"
          transform="rotate(-90 45 45)"/>
  <text x="45" y="49" text-anchor="middle" fill="{color}"
        font-size="16" font-weight="bold" font-family="monospace">{score:.1f}</text>
</svg>"""

def generate_html_report(dirs: dict, target_name: str, elapsed: float,
                          secrets_data: list, stats: dict) -> str:
    """Build a full professional HTML report. Returns path to the file."""

    report_path = os.path.join(dirs["reports"], "jsrecon_report.html")

    # ── Aggregate findings ────────────────────────────────────────────────
    all_cats = []
    for item in secrets_data:
        all_cats.extend(item.get("secrets", {}).keys())

    overall_sev, overall_score, overall_color = overall_severity(list(set(all_cats)))

    # Group findings by severity
    findings_by_sev = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": [], "INFO": []}
    for item in secrets_data:
        for cat, matches in item.get("secrets", {}).items():
            sev, score, color = get_severity(cat)
            findings_by_sev[sev].append({
                "category": cat,
                "url":      item["url"],
                "matches":  matches,
                "score":    score,
                "color":    color,
            })

    # Sensitive paths — format: url|status|cl_bytes|size_human
    sens_paths = []   # list of dicts
    sp_file = os.path.join(dirs["paths"], "findings_unique.txt")
    if os.path.exists(sp_file):
        for line in open(sp_file):
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) == 4:
                sens_paths.append({
                    "url": parts[0], "status": parts[1],
                    "cl":  parts[2], "size":   parts[3],
                })
            else:
                # legacy plain-URL format
                sens_paths.append({
                    "url": line, "status": "200", "cl": "?", "size": "?",
                })

    # API endpoints
    endpoints = []
    ep_file = os.path.join(dirs["endpoints"], "api_endpoints.txt")
    if os.path.exists(ep_file):
        endpoints = [l.strip() for l in open(ep_file) if l.strip()][:100]

    # Screenshots
    screens = []
    cap_dir = os.path.join(dirs["screenshots"], "captures")
    if os.path.isdir(cap_dir):
        screens = sorted(f for f in os.listdir(cap_dir) if f.endswith(".png"))

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Build findings rows (grouped: domain → JS URL → secrets) ──────────
    from collections import defaultdict as _dd2
    domain_finding_map = _dd2(list)
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        for f_item in findings_by_sev[sev]:
            dom  = urllib.parse.urlparse(f_item["url"]).netloc
            base = ".".join(dom.split(".")[-2:]) if dom else "unknown"
            domain_finding_map[base].append({**f_item, "sev": sev, "host": dom})

    # ── also build js_url → found_on map from secrets_data for HTML ──────
    js_found_on_map = {}
    for item in secrets_data:
        fo = item.get("found_on", [])
        if fo:
            js_found_on_map[item["url"]] = fo

    finding_rows = ""
    row_idx = 0
    for domain in sorted(domain_finding_map.keys()):
        items = domain_finding_map[domain]
        finding_rows += (
            f'<tr class="domain-hdr-row">' +
            f'<td colspan="6"><span class="domain-hdr-badge">🌐 {domain}</span>' +
            f'<span class="domain-hdr-count">{len(items)} finding(s)</span></td></tr>'
        )
        for f in items:
            row_idx += 1
            matches_html = ""
            for m in f["matches"][:5]:
                safe = m[:180].replace("<","&lt;").replace(">","&gt;")
                matches_html += f'<code class="match-line">{safe}</code>'
            if len(f["matches"]) > 5:
                matches_html += f'<span class="more-badge">+{len(f["matches"])-5} more</span>'
            js_short   = f["url"] if len(f["url"]) <= 72 else "…" + f["url"][-70:]
            found_pages = js_found_on_map.get(f["url"], [])
            if found_pages:
                found_on_html = "".join(
                    f'<a href="{pg}" target="_blank" class="found-on-link" title="{pg}">'
                    f'📄 {pg[:70]}{"…" if len(pg)>70 else ""}</a>'
                    for pg in found_pages[:5]
                )
                found_on_block = f'<div class="found-on-wrap"><span class="found-on-lbl">Found on:</span>{found_on_html}</div>'
            else:
                found_on_block = '<div class="found-on-wrap found-on-unknown">Found on: <span>not tracked</span></div>'

            finding_rows += (
                f'<tr class="finding-row sev-{f["sev"].lower()}">' +
                f'<td class="td-num">{row_idx}</td>' +
                f'<td>{_sev_badge(f["sev"])}</td>' +
                f'<td><span class="score-pill" style="color:{f["color"]}">{f["score"]}</span></td>' +
                f'<td class="td-cat">{f["category"]}</td>' +
                f'<td class="td-url">' +
                f'<div class="host-chip">{f["host"]}</div>' +
                f'<a href="{f["url"]}" target="_blank" class="url-link js-url-link" title="{f["url"]}">{js_short}</a>' +
                found_on_block +
                f'</td>' +
                f'<td class="td-matches">{matches_html}</td>' +
                f'</tr>'
            )
    # ── Sensitive paths rows (with size) ─────────────────────────────────
    path_rows = ""
    for i, p in enumerate(sens_paths[:100], 1):
        url_val    = p.get("url","")
        status_val = p.get("status","200")
        size_val   = p.get("size","?")
        safe_url   = url_val.replace("<","&lt;").replace(">","&gt;")
        short_url  = url_val
        if len(short_url) > 80:
            short_url = "…" + short_url[-78:]
        sc_color   = "#22c55e" if status_val == "200" else "#ff8800"
        path_rows += f"""
<tr>
  <td class="td-num">{i}</td>
  <td>{_sev_badge("HIGH")}</td>
  <td><span class="sc-badge" style="background:{sc_color}">{status_val}</span></td>
  <td><span class="size-badge">{size_val}</span></td>
  <td><a href="{url_val}" target="_blank" class="url-link" title="{safe_url}">{short_url}</a></td>
</tr>"""
    if not path_rows:
        path_rows = '<tr><td colspan="5" class="td-empty">No sensitive paths found</td></tr>'

    # ── Endpoint rows (full URLs) ─────────────────────────────────────────
    ep_rows = ""
    for i, ep in enumerate(endpoints[:200], 1):
        safe_ep  = ep.replace("<","&lt;").replace(">","&gt;")
        ep_short = ep if len(ep) <= 100 else "…" + ep[-98:]
        is_full  = ep.startswith("http")
        link     = f'<a href="{ep}" target="_blank" class="url-link">{ep_short}</a>' if is_full else f'<code class="td-ep">{safe_ep}</code>'
        parsed   = urllib.parse.urlparse(ep) if is_full else None
        domain   = f'<span class="host-chip" style="font-size:9px">{parsed.netloc}</span>' if parsed and parsed.netloc else ""
        ep_rows += f'''<tr>
  <td class="td-num">{i}</td>
  <td class="td-ep-host">{domain}</td>
  <td>{link}</td>
</tr>'''
    if not ep_rows:
        ep_rows = '<tr><td colspan="3" class="td-empty">No API endpoints found</td></tr>'

    # ── Screenshot cards ──────────────────────────────────────────────────
    screen_cards = ""
    if screens:
        for s in screens[:50]:
            rel = f"../10_screenshots/captures/{s}"
            screen_cards += f"""
<div class="sc-card">
  <img src="{rel}" loading="lazy" onclick="openLB(this.src)" alt="{s}">
  <div class="sc-label">{s[:60]}</div>
</div>"""
    else:
        screen_cards = '<p class="td-empty" style="padding:20px">No screenshots available</p>'

    # ── Stat cards ────────────────────────────────────────────────────────
    def stat_card(icon, label, val, color="#58a6ff"):
        return f"""
<div class="stat-card">
  <div class="stat-icon">{icon}</div>
  <div class="stat-val" style="color:{color}">{val}</div>
  <div class="stat-lbl">{label}</div>
</div>"""

    stat_cards = (
        stat_card("🌐", "Subdomains",      stats.get("subdomains", 0))
      + stat_card("✅", "Live Hosts",       stats.get("live", 0), "#22c55e")
      + stat_card("🔗", "Total URLs",       stats.get("combined", 0))
      + stat_card("📜", "JS Files",         stats.get("js", 0), "#a78bfa")
      + stat_card("🔑", "Secret Files",     len(secrets_data), overall_color)
      + stat_card("🛤️",  "API Endpoints",   stats.get("endpoints", 0), "#f59e0b")
      + stat_card("🚨", "Sensitive Paths",  stats.get("sensitive", 0), "#ef4444")
      + stat_card("📸", "Screenshots",      len(screens))
    )

    # ── Severity breakdown bars ───────────────────────────────────────────
    sev_bars = ""
    sev_meta = [
        ("CRITICAL", "#ff4444"),
        ("HIGH",     "#ff8800"),
        ("MEDIUM",   "#ffcc00"),
        ("LOW",      "#44aaff"),
        ("INFO",     "#888888"),
    ]
    total_findings = max(sum(len(findings_by_sev[s]) for s in findings_by_sev), 1)
    for sev, color in sev_meta:
        cnt = len(findings_by_sev[sev])
        pct = (cnt / total_findings) * 100
        sev_bars += f"""
<div class="sev-bar-row">
  <span class="sev-bar-lbl" style="color:{color}">{sev}</span>
  <div class="sev-bar-track">
    <div class="sev-bar-fill" style="width:{pct:.1f}%;background:{color}"></div>
  </div>
  <span class="sev-bar-cnt">{cnt}</span>
</div>"""

    # ── Filter buttons ────────────────────────────────────────────────────
    filter_btns = '<button class="filter-btn active" onclick="filterSev(\'all\',this)">ALL</button>'
    for sev, color in sev_meta:
        cnt = len(findings_by_sev[sev])
        filter_btns += (f'<button class="filter-btn" style="border-color:{color};color:{color}" '
                        f'onclick="filterSev(\'{sev.lower()}\',this)">{sev} ({cnt})</button>')

    # ─────────────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JSRecon Report — {target_name}</title>
<style>
:root{{
  --bg:#0d1117;--bg2:#161b22;--bg3:#21262d;
  --border:#30363d;--text:#c9d1d9;--muted:#8b949e;
  --blue:#58a6ff;--green:#22c55e;--red:#ff4444;
  --orange:#ff8800;--yellow:#ffcc00;--purple:#a78bfa;
  --font:'Courier New',monospace;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:var(--font);font-size:13px}}
a{{color:var(--blue);text-decoration:none}}
a:hover{{text-decoration:underline}}

/* ── TOP BAR ── */
.topbar{{background:linear-gradient(135deg,#0d1117 0%,#161b22 100%);
         border-bottom:2px solid var(--border);padding:20px 32px;
         display:flex;align-items:center;justify-content:space-between}}
.topbar-left h1{{font-size:20px;color:var(--blue);letter-spacing:1px}}
.topbar-left p{{color:var(--muted);font-size:11px;margin-top:4px}}
.topbar-right{{text-align:right}}
.topbar-right .ts{{color:var(--muted);font-size:11px}}

/* ── OVERALL SCORE ── */
.score-section{{background:var(--bg2);border-bottom:1px solid var(--border);
                padding:24px 32px;display:flex;gap:32px;align-items:center;flex-wrap:wrap}}
.score-ring-wrap{{display:flex;flex-direction:column;align-items:center;gap:6px}}
.score-label{{font-size:11px;color:var(--muted)}}
.overall-sev{{font-size:22px;font-weight:bold;letter-spacing:2px}}
.sev-breakdown{{flex:1;min-width:200px}}
.sev-bar-row{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
.sev-bar-lbl{{width:80px;font-size:11px;font-weight:bold}}
.sev-bar-track{{flex:1;height:8px;background:var(--bg3);border-radius:4px;overflow:hidden}}
.sev-bar-fill{{height:100%;border-radius:4px;transition:width .5s}}
.sev-bar-cnt{{width:30px;text-align:right;font-size:12px;color:var(--muted)}}
.score-meta{{color:var(--muted);font-size:11px;line-height:1.8}}
.score-meta strong{{color:var(--text)}}

/* ── MAIN ── */
.main{{padding:24px 32px;max-width:1600px}}

/* ── STAT CARDS ── */
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));
             gap:12px;margin-bottom:28px}}
.stat-card{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;
            padding:16px 12px;text-align:center}}
.stat-icon{{font-size:20px;margin-bottom:6px}}
.stat-val{{font-size:24px;font-weight:bold;margin-bottom:4px}}
.stat-lbl{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}}

/* ── SECTION HEADERS ── */
.section{{margin-bottom:32px}}
.section-hdr{{display:flex;align-items:center;gap:10px;margin-bottom:14px;
              border-bottom:1px solid var(--border);padding-bottom:10px}}
.section-hdr h2{{font-size:15px;color:var(--blue)}}
.section-hdr .count{{background:var(--bg3);border:1px solid var(--border);
                     border-radius:10px;padding:1px 10px;font-size:11px;color:var(--muted)}}

/* ── FILTER BUTTONS ── */
.filter-bar{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}}
.filter-btn{{background:var(--bg3);border:1px solid var(--border);
             color:var(--muted);border-radius:4px;padding:4px 12px;
             cursor:pointer;font-family:var(--font);font-size:11px;
             transition:all .2s}}
.filter-btn:hover,.filter-btn.active{{background:var(--bg2);color:var(--text);
                                       border-color:var(--blue)}}

/* ── TABLE ── */
.tbl-wrap{{overflow-x:auto;border-radius:8px;border:1px solid var(--border)}}
table{{width:100%;border-collapse:collapse}}
th{{background:var(--bg3);color:var(--muted);font-size:10px;text-transform:uppercase;
    letter-spacing:.5px;padding:10px 12px;text-align:left;border-bottom:1px solid var(--border)}}
td{{padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:top}}
tr:last-child td{{border-bottom:none}}
tr.finding-row:hover td{{background:var(--bg3)}}
.hidden{{display:none}}
.td-num{{color:var(--muted);font-size:11px;width:36px}}
.td-cat{{font-size:11px;color:var(--purple);white-space:nowrap}}
.td-url .url-link{{font-size:11px;color:var(--blue)}}
.td-matches{{max-width:400px}}
.td-empty{{color:var(--muted);font-size:12px;padding:20px;text-align:center}}
.td-ep{{font-family:monospace;font-size:11px;color:#22c55e}}

.match-line{{display:block;background:#0d1117;border:1px solid var(--border);
             border-radius:3px;padding:3px 8px;margin:2px 0;font-size:10px;
             color:#ffa657;word-break:break-all;white-space:pre-wrap}}
.more-badge{{background:var(--bg3);border:1px solid var(--border);
             border-radius:10px;padding:1px 8px;font-size:10px;
             color:var(--muted);margin-left:4px}}
.score-pill{{font-weight:bold;font-size:12px}}

/* ── SCREENSHOT GRID ── */
.sc-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}}
.sc-card{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;overflow:hidden}}
.sc-card img{{width:100%;display:block;cursor:zoom-in;border-bottom:1px solid var(--border)}}
.sc-label{{padding:8px 10px;font-size:10px;color:var(--muted);word-break:break-all}}
.sc-card:hover{{border-color:var(--blue)}}

/* ── LIGHTBOX ── */
.lb{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.92);
     z-index:9999;align-items:center;justify-content:center;cursor:zoom-out}}
.lb.on{{display:flex}}
.lb img{{max-width:94vw;max-height:94vh;border-radius:6px}}
.lb-close{{position:fixed;top:14px;right:20px;color:#fff;font-size:26px;cursor:pointer;z-index:10000}}

/* ── FOOTER ── */
footer{{border-top:1px solid var(--border);padding:16px 32px;
        color:var(--muted);font-size:11px;text-align:center;margin-top:40px}}

.domain-hdr-row td{{background:#0d1117;padding:12px 10px 6px}}
.domain-hdr-badge{{color:#58a6ff;font-size:13px;font-weight:bold;margin-right:10px}}
.domain-hdr-count{{color:#8b949e;font-size:11px}}
.host-chip{{display:inline-block;background:#21262d;border:1px solid #30363d;
           border-radius:3px;padding:1px 7px;font-size:10px;color:#a78bfa;
           margin-bottom:3px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.js-url-link{{font-size:11px;display:block;word-break:break-all}}
.sc-badge{{display:inline-block;border-radius:3px;padding:1px 7px;
          font-size:10px;font-weight:bold;color:#fff}}
.size-badge{{display:inline-block;background:#21262d;border:1px solid #30363d;
            border-radius:3px;padding:1px 7px;font-size:10px;color:#f59e0b}}
.td-ep-host{{width:160px;vertical-align:middle}}
.found-on-wrap{{margin-top:5px;display:flex;flex-direction:column;gap:2px}}
.found-on-lbl{{font-size:9px;color:#8b949e;text-transform:uppercase;letter-spacing:.5px;margin-bottom:2px}}
.found-on-link{{font-size:10px;color:#58a6ff;display:block;word-break:break-all;
                padding:1px 0;text-decoration:none}}
.found-on-link:hover{{text-decoration:underline}}
.found-on-unknown span{{color:#484f58;font-size:10px}}
.found-on-unknown{{margin-top:4px}}

/* ── PRINT / PDF ── */
@media print{{
  .topbar,.score-section,.filter-bar{{break-inside:avoid}}
  .sc-grid{{grid-template-columns:repeat(2,1fr)}}
  body{{background:#fff;color:#000}}
  .tbl-wrap{{border:1px solid #ccc}}
  th{{background:#f3f3f3;color:#333}}
  .match-line{{background:#f9f9f9;color:#c04}}
}}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <div class="topbar-left">
    <h1>⚡ JSRecon — Cyborg Edition V1</h1>
    <p>by <strong style="color:#f85149">Rahul Masal</strong>
       &nbsp;·&nbsp; Target: <strong style="color:var(--blue)">{target_name}</strong>
       &nbsp;·&nbsp; Authorized Security Assessment</p>
  </div>
  <div class="topbar-right">
    <div class="ts">Generated: {now_str}</div>
    <div class="ts">Runtime: {elapsed:.1f}s</div>
  </div>
</div>

<!-- OVERALL SCORE -->
<div class="score-section">
  <div class="score-ring-wrap">
    {_score_ring(overall_score, overall_color)}
    <div class="score-label">CVSS Score</div>
  </div>
  <div class="score-ring-wrap">
    <div class="overall-sev" style="color:{overall_color}">{overall_sev}</div>
    <div class="score-label">Overall Severity</div>
  </div>
  <div class="sev-breakdown">
    {sev_bars}
  </div>
  <div class="score-meta">
    <strong>Target:</strong> {target_name}<br>
    <strong>JS Files w/ Secrets:</strong> {len(secrets_data)}<br>
    <strong>Unique Categories:</strong> {len(set(all_cats))}<br>
    <strong>Sensitive Paths:</strong> {len(sens_paths)}<br>
    <strong>Runtime:</strong> {elapsed:.1f}s
  </div>
</div>

<!-- MAIN -->
<div class="main">

<!-- STAT CARDS -->
<div class="stats-grid">{stat_cards}</div>

<!-- FINDINGS TABLE -->
<div class="section">
  <div class="section-hdr">
    <h2>🔑 Secret Findings</h2>
    <span class="count">{row_idx} findings</span>
  </div>
  <div class="filter-bar">{filter_btns}</div>
  <div class="tbl-wrap">
    <table id="findings-tbl">
      <thead>
        <tr>
          <th>#</th><th>Severity</th><th>Score</th>
          <th>Category</th><th>Source URL</th><th>Matched Secrets</th>
        </tr>
      </thead>
      <tbody>
        {finding_rows if finding_rows else '<tr><td colspan="6" class="td-empty">No secrets found</td></tr>'}
      </tbody>
    </table>
  </div>
</div>

<!-- SENSITIVE PATHS -->
<div class="section">
  <div class="section-hdr">
    <h2>🚨 Sensitive Paths (HTTP 200)</h2>
    <span class="count">{len(sens_paths)}</span>
  </div>
  <div class="tbl-wrap">
    <table>
      <thead><tr><th>#</th><th>Severity</th><th>Status</th><th>Size</th><th>URL</th></tr></thead>
      <tbody>{path_rows}</tbody>
    </table>
  </div>
</div>

<!-- API ENDPOINTS -->
<div class="section">
  <div class="section-hdr">
    <h2>🛤️ API Endpoints Extracted from JS</h2>
    <span class="count">{len(endpoints)}</span>
  </div>
  <div class="tbl-wrap">
    <table>
      <thead><tr><th>#</th><th>Domain</th><th>Full Endpoint URL</th></tr></thead>
      <tbody>{ep_rows}</tbody>
    </table>
  </div>
</div>

<!-- SCREENSHOTS -->
<div class="section">
  <div class="section-hdr">
    <h2>📸 Visual Reconnaissance</h2>
    <span class="count">{len(screens)}</span>
  </div>
  <div class="sc-grid">{screen_cards}</div>
</div>

</div><!-- /main -->

<!-- LIGHTBOX -->
<div class="lb" id="lb" onclick="closeLB()">
  <span class="lb-close" onclick="closeLB()">✕</span>
  <img id="lb-img" src="" alt="">
</div>

<footer>
  JSRecon Cyborg Edition V1 — by Rahul Masal &nbsp;|&nbsp;
  For authorized security testing only &nbsp;|&nbsp;
  {now_str}
</footer>

<script>
// Severity filter
function filterSev(sev, btn){{
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('#findings-tbl tbody tr').forEach(r=>{{
    if(sev==='all') r.classList.remove('hidden');
    else r.classList.toggle('hidden', !r.classList.contains('sev-'+sev));
  }});
}}
// Lightbox
function openLB(src){{
  document.getElementById('lb-img').src=src;
  document.getElementById('lb').classList.add('on');
}}
function closeLB(){{
  document.getElementById('lb').classList.remove('on');
  document.getElementById('lb-img').src='';
}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeLB();}});
</script>
</body></html>"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    success(f"HTML report → {report_path}")
    return report_path


# ─────────────────────────────────────────────────────────────────────────────
# PDF EXPORT  (wkhtmltopdf → weasyprint → fallback message)
# ─────────────────────────────────────────────────────────────────────────────
def export_pdf(html_path: str) -> str:
    """Convert HTML report to PDF. Returns PDF path or empty string on failure."""
    pdf_path = html_path.replace(".html", ".pdf")

    # Try wkhtmltopdf first (best output quality)
    if shutil.which("wkhtmltopdf"):
        cmd = (
            f'wkhtmltopdf --quiet --enable-local-file-access '
            f'--page-size A4 --orientation Landscape '
            f'--margin-top 10mm --margin-bottom 10mm '
            f'--margin-left 8mm --margin-right 8mm '
            f'"{html_path}" "{pdf_path}" 2>/dev/null'
        )
        ret = os.system(cmd)
        if ret == 0 and os.path.exists(pdf_path):
            success(f"PDF exported (wkhtmltopdf) → {pdf_path}")
            return pdf_path
        warn("wkhtmltopdf ran but produced no output, trying weasyprint...")

    # Try weasyprint
    try:
        import weasyprint  # type: ignore
        weasyprint.HTML(filename=html_path).write_pdf(pdf_path)
        success(f"PDF exported (weasyprint) → {pdf_path}")
        return pdf_path
    except ImportError:
        pass
    except Exception as e:
        warn(f"weasyprint failed: {e}")

    # Last resort: chromium headless
    for chrome in ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]:
        if shutil.which(chrome):
            cmd = (
                f'{chrome} --headless --disable-gpu --no-sandbox '
                f'--print-to-pdf="{pdf_path}" '
                f'"file://{os.path.abspath(html_path)}" 2>/dev/null'
            )
            ret = os.system(cmd)
            if ret == 0 and os.path.exists(pdf_path):
                success(f"PDF exported (chromium headless) → {pdf_path}")
                return pdf_path

    warn("PDF export skipped — install wkhtmltopdf:  apt install wkhtmltopdf")
    warn("  or weasyprint:  pip3 install weasyprint")
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# TELEGRAM NOTIFIER
# ─────────────────────────────────────────────────────────────────────────────
def _tg_post(token: str, chat_id: str, data: dict, files: dict = None) -> bool:
    """POST to Telegram Bot API. Returns True on success."""
    if files:
        # multipart/form-data for file uploads
        import email.mime.multipart
        boundary = "----JSReconBoundary"
        body_parts = []
        for key, val in data.items():
            body_parts.append(
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
                f'{val}\r\n'
            )
        for key, (fname, fdata, mime) in files.items():
            body_parts.append(
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="{key}"; filename="{fname}"\r\n'
                f'Content-Type: {mime}\r\n\r\n'
            )
        body = "".join(body_parts).encode()
        for key, (fname, fdata, mime) in files.items():
            body += fdata + f'\r\n--{boundary}--\r\n'.encode()

        method = "sendDocument"
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    else:
        body = json.dumps(data).encode()
        method = "sendMessage"
        headers = {"Content-Type": "application/json"}

    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200
    except Exception as e:
        warn(f"Telegram API error: {e}")
        return False


def _tg_send_message(token: str, chat_id: str, text: str) -> bool:
    """Send a plain text/markdown message via Telegram Bot API."""
    url  = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "Markdown",
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if resp.status == 200:
                return True
            warn(f"Telegram sendMessage HTTP {resp.status}: {body[:200]}")
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        warn(f"Telegram sendMessage error {e.code}: {body[:300]}")
        return False
    except Exception as e:
        warn(f"Telegram sendMessage exception: {e}")
        return False


def _tg_send_document(token: str, chat_id: str, file_path: str, caption: str = "") -> bool:
    """
    Upload a file to Telegram using a properly constructed multipart/form-data body.
    Telegram requires CRLF line endings and correct boundary handling.
    """
    url   = f"https://api.telegram.org/bot{token}/sendDocument"
    fname = os.path.basename(file_path)
    mime  = "application/pdf" if file_path.endswith(".pdf") else "text/html"

    try:
        with open(file_path, "rb") as fh:
            file_data = fh.read()
    except Exception as e:
        warn(f"Cannot read file {file_path}: {e}")
        return False

    file_size = len(file_data)
    if file_size > 50 * 1024 * 1024:
        warn(f"File too large for Telegram ({file_size/1024/1024:.1f} MB > 50 MB)")
        return False

    info(f"Uploading to Telegram: {fname} ({file_size/1024:.1f} KB)")

    boundary = "TGReconBoundary20250101"
    CRLF     = b"\r\n"

    def field(name: str, value: str) -> bytes:
        return (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n'
            f"\r\n"
            f"{value}\r\n"
        ).encode("utf-8")

    body = (
        field("chat_id",  chat_id)
        + field("caption", caption[:1024])
        + (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="document"; filename="{fname}"\r\n'
            f"Content-Type: {mime}\r\n"
            f"\r\n"
        ).encode("utf-8")
        + file_data
        + f"\r\n--{boundary}--\r\n".encode("utf-8")
    )

    try:
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            if resp.status == 200:
                success(f"Telegram: document sent ✔  ({fname}, {file_size/1024:.1f} KB)")
                return True
            warn(f"Telegram sendDocument HTTP {resp.status}: {resp_body[:300]}")
            return False
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8", errors="replace")
        warn(f"Telegram sendDocument error {e.code}: {resp_body[:400]}")
        # If file send fails, note it clearly
        if e.code == 400:
            warn("Tip: Make sure the bot has started a conversation with your chat_id first.")
            warn("  Send any message to your bot, then retry.")
        return False
    except Exception as e:
        warn(f"Telegram sendDocument exception: {e}")
        return False


def send_telegram(cfg: dict, target_name: str, report_stats: dict,
                  secrets_data: list, pdf_path: str, html_path: str):
    """
    Send JSRecon summary + report file to Telegram.
    Always sends the text summary first; file attachment is best-effort.
    """
    token   = cfg.get("telegram_bot_token",  "").strip()
    chat_id = cfg.get("telegram_chat_id",    "").strip()

    # ── Credential validation ─────────────────────────────────────────────
    if not token:
        warn("Telegram: TELEGRAM_BOT_TOKEN not set in jsrecon.env — skipping")
        return
    if not chat_id:
        warn("Telegram: TELEGRAM_CHAT_ID not set in jsrecon.env — skipping")
        return
    if "your_bot_token_here" in token:
        warn("Telegram: still has placeholder token — edit jsrecon.env")
        return
    if "your_chat_id_here" in chat_id:
        warn("Telegram: still has placeholder chat_id — edit jsrecon.env")
        return

    info(f"Sending Telegram notification → chat_id: {chat_id}")

    # ── Build severity counts ─────────────────────────────────────────────
    all_cats = []
    for item in secrets_data:
        all_cats.extend(item.get("secrets", {}).keys())
    overall_sev, overall_score, _ = overall_severity(list(set(all_cats)))

    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for item in secrets_data:
        for cat in item.get("secrets", {}).keys():
            sev, _, _ = get_severity(cat)
            if sev in sev_counts:
                sev_counts[sev] += 1

    sev_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡",
                 "LOW": "🔵", "INFO": "⚪"}
    overall_emoji = sev_emoji.get(overall_sev, "⚪")

    # ── Build HTML-formatted message ──────────────────────────────────────
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = (
        f"⚡ <b>JSRecon Cyborg V1</b> — by Rahul Masal\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>Target:</b> <code>{target_name}</code>\n"
        f"🕐 <b>Date:</b> {now}\n"
        f"\n"
        f"{overall_emoji} <b>Overall Severity:</b> <code>{overall_sev}</code>"
        f" (CVSS {overall_score:.1f})\n"
        f"\n"
        f"<b>📊 Findings:</b>\n"
        f"  🔴 CRITICAL : <code>{sev_counts['CRITICAL']}</code>\n"
        f"  🟠 HIGH     : <code>{sev_counts['HIGH']}</code>\n"
        f"  🟡 MEDIUM   : <code>{sev_counts['MEDIUM']}</code>\n"
        f"  🔵 LOW      : <code>{sev_counts['LOW']}</code>\n"
        f"\n"
        f"<b>📈 Recon Stats:</b>\n"
        f"  Subdomains      : <code>{report_stats.get('subdomains', 0)}</code>\n"
        f"  Live Hosts      : <code>{report_stats.get('live', 0)}</code>\n"
        f"  Total URLs      : <code>{report_stats.get('combined', 0)}</code>\n"
        f"  JS Files        : <code>{report_stats.get('js', 0)}</code>\n"
        f"  JS w/ Secrets   : <code>{len(secrets_data)}</code>\n"
        f"  API Endpoints   : <code>{report_stats.get('endpoints', 0)}</code>\n"
        f"  Sensitive Paths : <code>{report_stats.get('sensitive', 0)}</code>\n"
        f"\n"
        f"📎 <b>Report attached below</b>"
    )

    # ── Step 1: Send text message ─────────────────────────────────────────
    api_base = f"https://api.telegram.org/bot{token}"
    msg_sent = False
    try:
        payload = json.dumps({
            "chat_id":    chat_id,
            "text":       msg,
            "parse_mode": "HTML",
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{api_base}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
            if body.get("ok"):
                success("Telegram ✔ summary message sent")
                msg_sent = True
            else:
                warn(f"Telegram sendMessage not ok: {body.get('description', 'unknown error')}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        warn(f"Telegram sendMessage HTTP {e.code}: {err_body[:300]}")
        if e.code == 401:
            error("Telegram 401: Bot token is INVALID or REVOKED.")
            error("  → Get a new token from @BotFather and update jsrecon.env")
            return
        if e.code == 400:
            error("Telegram 400: Bad Request — most likely wrong chat_id.")
            error(f"  → Your chat_id in jsrecon.env: {chat_id}")
            error("  → Get your real chat_id from @userinfobot on Telegram")
            return
        if e.code == 403:
            error("Telegram 403: Bot was blocked or never started by user.")
            error("  → Send any message to your bot first, then retry.")
            return
    except Exception as e:
        error(f"Telegram sendMessage exception: {e}")
        return

    if not msg_sent:
        warn("Telegram: text message failed — skipping file attachment")
        return

    # ── Step 2: Attach report file ────────────────────────────────────────
    # Priority: PDF > HTML > plain text summary
    attach_candidates = []
    if pdf_path  and os.path.exists(pdf_path):  attach_candidates.append(pdf_path)
    if html_path and os.path.exists(html_path): attach_candidates.append(html_path)

    # Also always send the plain-text summary (small, always works)
    txt_summary = os.path.join(
        os.path.dirname(html_path) if html_path else "/tmp",
        "summary_report.txt"
    )
    # Find it properly from dirs structure
    for candidate in attach_candidates or []:
        rep_dir = os.path.dirname(os.path.dirname(candidate))
        txt_candidate = os.path.join(rep_dir, "11_reports", "summary_report.txt")
        if os.path.exists(txt_candidate):
            txt_summary = txt_candidate
            break

    if not attach_candidates and os.path.exists(txt_summary):
        attach_candidates.append(txt_summary)
    elif os.path.exists(txt_summary):
        attach_candidates.insert(0, txt_summary)  # send txt first (small, reliable)

    for attach_path in attach_candidates[:2]:   # max 2 files
        fname     = os.path.basename(attach_path)
        fsize     = os.path.getsize(attach_path)
        ext       = os.path.splitext(fname)[1].lower()
        mime_map  = {".pdf": "application/pdf", ".html": "text/html",
                     ".txt": "text/plain", ".json": "application/json"}
        mime      = mime_map.get(ext, "application/octet-stream")

        if fsize > 50 * 1024 * 1024:
            warn(f"Telegram: {fname} is {fsize/1024/1024:.1f} MB — too large (>50 MB), skipping")
            continue

        info(f"Telegram: uploading {fname} ({fsize/1024:.1f} KB)...")

        boundary = "JSReconBnd20250529"
        caption  = (f"JSRecon — {target_name} | {overall_sev} "
                    f"(CVSS {overall_score:.1f}) | {now}")[:1024]

        try:
            with open(attach_path, "rb") as fh:
                file_bytes = fh.read()

            body_parts = (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
                f"{chat_id}\r\n"
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="caption"\r\n\r\n'
                f"{caption}\r\n"
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="document"; filename="{fname}"\r\n'
                f"Content-Type: {mime}\r\n\r\n"
            ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

            req = urllib.request.Request(
                f"{api_base}/sendDocument",
                data=body_parts,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8", errors="replace"))
                if body.get("ok"):
                    success(f"Telegram ✔ file sent: {fname} ({fsize/1024:.1f} KB)")
                else:
                    warn(f"Telegram sendDocument not ok: {body.get('description','')}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            warn(f"Telegram sendDocument HTTP {e.code}: {err_body[:300]}")
        except Exception as e:
            warn(f"Telegram sendDocument exception: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# DISCORD NOTIFIER  (critical/high findings only)
# ─────────────────────────────────────────────────────────────────────────────
def send_discord(cfg: dict, target_name: str, secrets_data: list):
    """Send CRITICAL and HIGH findings to Discord webhook as rich embeds."""
    webhook_url = cfg.get("discord_webhook_url", "").strip()
    if not webhook_url:
        warn("Discord webhook not configured — skipping Discord notification")
        warn("  Edit jsrecon.env and set DISCORD_WEBHOOK_URL")
        return

    # Collect critical/high items
    critical_items = []
    for item in secrets_data:
        for cat, matches in item.get("secrets", {}).items():
            sev, score, color_hex = get_severity(cat)
            if sev in ("CRITICAL", "HIGH"):
                critical_items.append({
                    "sev": sev, "score": score, "color": color_hex,
                    "cat": cat, "url": item["url"], "matches": matches,
                })

    if not critical_items:
        info("No CRITICAL/HIGH findings — skipping Discord alert")
        return

    info(f"Sending {len(critical_items)} critical/high findings to Discord...")

    # Discord embed color (int from hex)
    def hex_to_int(h: str) -> int:
        return int(h.lstrip("#"), 16)

    # Discord max: 10 embeds per message, 4096 chars per embed
    CHUNK = 10

    for batch_start in range(0, len(critical_items), CHUNK):
        batch = critical_items[batch_start:batch_start + CHUNK]
        embeds = []
        for item in batch:
            # Format matches, truncate to fit Discord limits
            match_lines = []
            for m in item["matches"][:6]:
                safe = m[:200].replace("`", "'")
                match_lines.append(f"`{safe}`")
            if len(item["matches"]) > 6:
                match_lines.append(f"*…and {len(item['matches'])-6} more*")
            matches_text = "\n".join(match_lines)

            # Truncate URL for display
            display_url = item["url"][:200]

            embed = {
                "title":       f"{'🔴' if item['sev']=='CRITICAL' else '🟠'} {item['sev']} — {item['cat']}",
                "description": f"**CVSS Score:** {item['score']}\n**Source URL:** {display_url}",
                "color":       hex_to_int(item["color"]),
                "fields": [
                    {
                        "name":   "Matched Secrets",
                        "value":  matches_text[:1020] or "N/A",
                        "inline": False,
                    },
                    {
                        "name":   "Full URL",
                        "value":  item["url"][:1020],
                        "inline": False,
                    },
                ],
                "footer": {
                    "text": f"JSRecon Cyborg V1 · Rahul Masal · Target: {target_name}"
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            embeds.append(embed)

        payload = {
            "username":   "JSRecon Cyborg V1",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2092/2092757.png",
            "content": (
                f"⚡ **JSRecon Alert** — `{target_name}`\n"
                f"{'🔴 CRITICAL/HIGH findings detected' if batch_start == 0 else f'continued ({batch_start+1}–{batch_start+len(batch)})'}"
                if batch_start == 0 else ""
            ),
            "embeds": embeds,
        }

        try:
            body = json.dumps(payload).encode()
            req  = urllib.request.Request(
                webhook_url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 204):
                    success(f"Discord: batch {batch_start//CHUNK + 1} sent ({len(batch)} embeds)")
                else:
                    warn(f"Discord: HTTP {resp.status}")
        except urllib.error.HTTPError as e:
            body_txt = e.read().decode(errors="replace")[:300]
            warn(f"Discord HTTP error {e.code}: {body_txt}")
        except Exception as e:
            warn(f"Discord send failed: {e}")

        # Rate limit: Discord allows 5 requests/2 seconds on webhooks
        if batch_start + CHUNK < len(critical_items):
            time.sleep(0.5)

    success(f"Discord notifications sent for {len(critical_items)} critical/high findings")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN REPORT ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def generate_report(dirs: dict, target_name: str, start_time: float):
    phase("Phase 7 — Generating Reports & Notifications")
    elapsed = time.time() - start_time

    def count_lines(fpath):
        try:
            with open(fpath) as fh:
                return sum(1 for l in fh if l.strip())
        except Exception:
            return 0

    subdomain_count  = count_lines(os.path.join(dirs["subdomains"], "subfinder_all.txt"))
    live_count       = count_lines(os.path.join(dirs["subdomains"], "live_subdomains.txt"))
    sensitive_count  = count_lines(os.path.join(dirs["paths"],      "findings_unique.txt"))
    combined_count   = count_lines(os.path.join(dirs["combined"],   "urls.txt"))
    js_count         = count_lines(os.path.join(dirs["js"],         "js_urls.txt"))
    endpoints_count  = count_lines(os.path.join(dirs["endpoints"],  "api_endpoints.txt"))
    jsfileurls_count = count_lines(os.path.join(dirs["js"],         "jsfileurls.txt"))

    stats = {
        "subdomains": subdomain_count,
        "live":       live_count,
        "sensitive":  sensitive_count,
        "combined":   combined_count,
        "js":         js_count,
        "endpoints":  endpoints_count,
        "jsfileurls": jsfileurls_count,
    }

    # Load secrets JSON
    secrets_json_path = os.path.join(dirs["secrets"], "js_secrets.json")
    secrets_data = []
    if os.path.exists(secrets_json_path):
        try:
            with open(secrets_json_path) as fh:
                secrets_data = json.load(fh)
        except Exception:
            pass

    secret_cats = set()
    for item in secrets_data:
        secret_cats.update(item.get("secrets", {}).keys())

    overall_sev, overall_score, _ = overall_severity(list(secret_cats))

    # Plain-text summary
    report_file = os.path.join(dirs["reports"], "summary_report.txt")
    with open(report_file, "w") as fh:
        fh.write("=" * 72 + "\n")
        fh.write("  JSRecon Cyborg Edition V1  |  by Rahul Masal\n")
        fh.write(f"  Target  : {target_name}\n")
        fh.write(f"  Date    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        fh.write(f"  Runtime : {elapsed:.1f}s\n")
        fh.write(f"  Overall : {overall_sev}  (CVSS {overall_score:.1f})\n")
        fh.write("=" * 72 + "\n\n")
        fh.write(f"  Subdomains Discovered : {subdomain_count}\n")
        fh.write(f"  Live Subdomains       : {live_count}\n")
        fh.write(f"  Sensitive Paths       : {sensitive_count}\n")
        fh.write(f"  Combined URLs         : {combined_count}\n")
        fh.write(f"  JS Files Analyzed     : {js_count}\n")
        fh.write(f"  JS Files w/ Secrets   : {len(secrets_data)}\n")
        fh.write(f"  API Endpoints         : {endpoints_count}\n")
        fh.write(f"  URLs Extracted from JS: {jsfileurls_count}\n\n")
        if secret_cats:
            fh.write("  SECRET CATEGORIES FOUND:\n")
            for cat in sorted(secret_cats):
                sev, score, _ = get_severity(cat)
                fh.write(f"    [{sev:8s} {score:.1f}]  {cat}\n")
        fh.write("\n  OUTPUT DIRECTORIES:\n")
        for name, path in dirs.items():
            fh.write(f"    {name:<15}: {path}\n")

    success(f"Summary report  -> {report_file}")

    # ── HTML report (wrapped so errors don't block notifications) ─────────
    html_path = ""
    try:
        html_path = generate_html_report(dirs, target_name, elapsed, secrets_data, stats)
    except Exception as e:
        error(f"HTML report generation failed: {e}")
        import traceback; traceback.print_exc()

    # ── PDF export ────────────────────────────────────────────────────────
    pdf_path = ""
    if html_path:
        try:
            pdf_path = export_pdf(html_path)
        except Exception as e:
            warn(f"PDF export failed: {e}")

    # ── Load notification config ──────────────────────────────────────────
    phase("Sending Notifications")
    cfg = load_config()

    # ── Telegram notification (ALWAYS fires, even if HTML/PDF failed) ─────
    try:
        send_telegram(cfg, target_name, stats, secrets_data, pdf_path, html_path)
    except Exception as e:
        error(f"Telegram notification failed unexpectedly: {e}")
        import traceback; traceback.print_exc()

    # ── Discord (critical/high only) ──────────────────────────────────────
    try:
        send_discord(cfg, target_name, secrets_data)
    except Exception as e:
        error(f"Discord notification failed: {e}")

    # Final console banner
    print(f"\n{C.CYAN}{C.BOLD}{'=' * 70}")
    print(f"  JSRecon Cyborg V1 — by Rahul Masal")
    print(f"  Target    : {target_name}")
    print(f"  Severity  : {overall_sev}  (CVSS {overall_score:.1f})")
    print(f"  Runtime   : {elapsed:.1f}s")
    print(f"  Output    : {dirs['base']}")
    print(f"  HTML      : {html_path}")
    if pdf_path:
        print(f"  PDF       : {pdf_path}")
    print(f"{'=' * 70}{C.RESET}\n")
    print(open(report_file).read())
# ─────────────────────────────────────────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        prog="jsrecon",
        description=f"{C.CYAN}JSRecon Cyborg Edition V1 — by Rahul Masal{C.RESET}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 jsrecon.py -d example.com
  python3 jsrecon.py -l domains.txt
  python3 jsrecon.py -d example.com --skip-screenshots
  python3 jsrecon.py -d example.com --js-only
        """
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("-d", "--domain", help="Single target domain (e.g. example.com)")
    target.add_argument("-l", "--list",   help="File containing list of domains")
    parser.add_argument("--skip-screenshots", action="store_true", help="Skip GoWitness screenshots")
    parser.add_argument("--skip-wayback",     action="store_true", help="Skip waybackurls collection")
    parser.add_argument("--skip-spider",      action="store_true", help="Skip GoSpider + Katana")
    parser.add_argument("--js-only",          action="store_true", help="Skip recon, only analyze JS from stdin")
    parser.add_argument("--threads",          type=int, default=10,  help="Threads for JS analysis (default: 10)")
    parser.add_argument("--test-notify",      action="store_true",    help="Test Telegram/Discord credentials and exit")
    return parser.parse_args()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    banner()
    args = parse_args()
    start_time = time.time()

    # Load domains
    if args.domain:
        domains = [args.domain.strip()]
        target_name = args.domain.strip()
    else:
        if not os.path.exists(args.list):
            error(f"Domain list file not found: {args.list}")
            sys.exit(1)
        with open(args.list) as f:
            domains = [l.strip() for l in f if l.strip()]
        target_name = os.path.splitext(os.path.basename(args.list))[0]

    info(f"Targets loaded: {len(domains)} domain(s)")
    dirs = setup_output(target_name)
    success(f"Output directory: {dirs['base']}")

    # ── --test-notify: validate credentials and send a test message ───────
    if args.test_notify:
        phase("Testing Notification Credentials")
        cfg = load_config()
        token   = cfg.get("telegram_bot_token", "")
        chat_id = cfg.get("telegram_chat_id", "")
        if not token or not chat_id:
            error("Cannot test — credentials not loaded. Fix jsrecon.env first.")
            sys.exit(1)
        info("Sending test message to Telegram...")
        test_msg = (
            f"✅ <b>JSRecon Test Message</b>\n"
            f"Your Telegram notifications are working!\n"
            f"Bot token and chat_id are correctly configured.\n"
            f"— JSRecon Cyborg V1 by Rahul Masal"
        )
        try:
            import urllib.request, json as _json
            payload = _json.dumps({
                "chat_id": chat_id, "text": test_msg, "parse_mode": "HTML"
            }).encode()
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=payload, headers={"Content-Type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = _json.loads(resp.read())
                if body.get("ok"):
                    success("✔ Telegram test message sent successfully!")
                    success("Check your Telegram — you should see the test message.")
                else:
                    error(f"Telegram returned not-ok: {body.get('description','')}")
        except Exception as e:
            error(f"Telegram test failed: {e}")
        sys.exit(0)

    # Check tools
    missing_tools = check_tools()

    if args.js_only:
        # Read JS URLs from stdin
        info("JS-only mode: reading JS URLs from stdin...")
        js_urls = [l.strip() for l in sys.stdin if l.strip()]
        phase_js_analysis(js_urls, dirs, source_map={})
        generate_report(dirs, target_name, start_time)
        return

    # Phase 1 — Subdomains
    live_domains = phase_subdomains(domains, dirs, missing_tools)
    subfinder_file = os.path.join(dirs["subdomains"], "subfinder_all.txt")

    # Phase 2 — Sensitive paths
    phase_check = check_sensitive_paths(live_domains, dirs, missing_tools)

    # Phase 3 — URL collection
    skip_wayback = args.skip_wayback
    skip_spider  = args.skip_spider
    if skip_wayback:
        missing_tools.append("waybackurls")
    if skip_spider:
        missing_tools.append("gospider")
        missing_tools.append("katana")

    combined_file, all_urls, source_map = phase_url_collection(
        live_domains, subfinder_file, dirs, missing_tools
    )

    # Phase 4 — Filter URLs + extract JS
    js_file, js_urls = phase_filter_urls(combined_file, dirs)

    # Phase 5 — JS Analysis (pass source_map so each result gets found_on)
    phase_js_analysis(js_urls, dirs, source_map=source_map)

    # Phase 6 — Screenshots
    if not args.skip_screenshots:
        phase_screenshots(live_domains, dirs, missing_tools)
    else:
        info("Screenshots skipped (--skip-screenshots)")

    # Phase 7 — Final Report
    generate_report(dirs, target_name, start_time)


if __name__ == "__main__":
    main()
