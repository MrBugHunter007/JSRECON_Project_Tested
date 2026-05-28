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
    "curl":        "apt install curl",
}

def check_tools():
    phase("Checking Required Tools")
    missing = []
    for tool, install_cmd in REQUIRED_TOOLS.items():
        if shutil.which(tool):
            success(f"{tool:15s} found")
        else:
            warn(f"{tool:15s} NOT FOUND  →  {C.DIM}{install_cmd}{C.RESET}")
            missing.append(tool)
    if missing:
        warn(f"Missing tools: {', '.join(missing)}. Some phases will be skipped.")
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

    run(f"cat {urls_file} | httpx -silent -mc 200 -o {raw_findings}")

    if not os.path.exists(raw_findings):
        info("No sensitive paths found (200 OK)")
        return

    # Deduplicate by content-length to remove honeypots/default pages
    info("Filtering by content-length to remove false positives...")
    cl_map = {}  # url -> content_length
    cl_raw = run(f"cat {raw_findings} | httpx -silent -mc 200 -cl")
    for line in cl_raw.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            url, cl = parts[0], parts[-1]
            cl_map[url] = cl

    # Group by domain, find unique content-lengths
    from collections import defaultdict
    domain_cls = defaultdict(set)
    for url, cl in cl_map.items():
        parsed = urllib.parse.urlparse(url)
        domain_cls[parsed.netloc].add(cl)

    unique_urls = []
    seen_cls = defaultdict(set)
    for url, cl in cl_map.items():
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        if cl not in seen_cls[domain]:
            seen_cls[domain].add(cl)
            unique_urls.append(url)

    with open(filtered_findings, "w") as f:
        f.write("\n".join(unique_urls) + "\n")

    success(f"Unique sensitive path findings: {len(unique_urls)}")
    for u in unique_urls:
        finding(f"SENSITIVE PATH → {u}")

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

    # Combine all URLs
    combined_file = os.path.join(dirs["combined"], "urls.txt")
    with open(combined_file, "w") as f:
        f.write("\n".join(sorted(all_urls)) + "\n")
    success(f"Combined unique URLs: {len(all_urls)}")

    return combined_file, list(all_urls)

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

def analyze_js_file(url: str, dirs: dict) -> dict:
    """Download and analyze a single JS file."""
    result = {
        "url": url,
        "secrets": {},
        "urls_found": [],
        "api_endpoints": [],
        "downloaded": False,
        "size": 0,
        "sha256": "",
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

    except Exception as e:
        pass

    return result

def phase_js_analysis(js_urls: list, dirs: dict):
    phase("Phase 5 — JavaScript File Analysis")

    if not js_urls:
        warn("No JS URLs to analyze")
        return

    info(f"Analyzing {len(js_urls)} JS files...")
    all_results = []
    all_secrets = []
    all_js_urls = []
    all_endpoints = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(analyze_js_file, url, dirs): url for url in js_urls}
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

    # ── Write secrets report ──────────────────────────────────────────────
    secrets_report = os.path.join(dirs["secrets"], "js_secrets.txt")
    secrets_json   = os.path.join(dirs["secrets"], "js_secrets.json")

    with open(secrets_report, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("  JSRecon Cyborg Edition V1 — by Rahul Masal\n")
        f.write(f"  JS Secrets Report  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        if not all_secrets:
            f.write("No secrets found.\n")
        for item in all_secrets:
            f.write(f"\n{'─'*70}\n")
            f.write(f"  URL    : {item['url']}\n")
            f.write(f"  Size   : {item['size']} bytes\n")
            f.write(f"  SHA256 : {item['sha256']}\n")
            f.write(f"{'─'*70}\n")
            for cat, matches in item["secrets"].items():
                f.write(f"\n  [{cat}]\n")
                for m in matches:
                    f.write(f"    {m[:200]}\n")
            f.write("\n")

    with open(secrets_json, "w") as f:
        json.dump(all_secrets, f, indent=2, default=str)

    success(f"Secrets written → {secrets_report}")

    # ── Write extracted URLs from JS ─────────────────────────────────────
    js_file_urls = os.path.join(dirs["js"], "jsfileurls.txt")
    with open(js_file_urls, "w") as f:
        f.write("\n".join(sorted(set(all_js_urls))) + "\n")
    success(f"URLs extracted from JS files: {len(set(all_js_urls))} → {js_file_urls}")

    # ── Write API endpoints ───────────────────────────────────────────────
    ep_file = os.path.join(dirs["endpoints"], "api_endpoints.txt")
    with open(ep_file, "w") as f:
        f.write("\n".join(sorted(set(all_endpoints))) + "\n")
    success(f"API endpoints extracted: {len(set(all_endpoints))} → {ep_file}")

    return all_results

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 6 — SCREENSHOTS with GoWitness
# ─────────────────────────────────────────────────────────────────────────────
def _gowitness_version() -> int:
    """
    Detect gowitness major version.
    v2 help contains '--db string'  (flag style)
    v3 help contains 'file [flags]' and uses --destination / --disable-db
    Returns 2, 3, or 0 if unknown.
    """
    try:
        out = subprocess.run(
            ["gowitness", "--help"], capture_output=True, text=True, timeout=10
        )
        combined = (out.stdout + out.stderr).lower()
        if "--destination" in combined or "disable-db" in combined:
            return 3
        if "--db string" in combined or "gowitness.db" in combined:
            return 2
    except Exception:
        pass
    return 0


def _build_gowitness_cmd(version: int, sites_file: str,
                          screenshot_dir: str, db_file: str,
                          threads: int = 5, timeout: int = 15) -> str:
    """
    Build the correct gowitness command for the detected version.

    v2:  gowitness file -f <file> -d <dest> -D <db> --threads N --timeout N
    v3:  gowitness --destination <dest> --disable-db file -f <file> --threads N --timeout N
         (v3 also accepts:  gowitness file -f <file> --destination <dest> ...)
    """
    if version == 3:
        # v3: global flags before sub-command, screenshot saved to --destination
        # --disable-db avoids needing sqlite / chrome profile issues
        return (
            f"gowitness "
            f"--destination {screenshot_dir} "
            f"--disable-db "
            f"file -f {sites_file} "
            f"--threads {threads} "
            f"--timeout {timeout} "
            f"2>&1"
        )
    else:
        # v2 (default / fallback)
        return (
            f"gowitness file -f {sites_file} "
            f"-d {screenshot_dir} "
            f"-D {db_file} "
            f"--threads {threads} "
            f"--timeout {timeout} "
            f"2>&1"
        )


def phase_screenshots(live_domains: list, dirs: dict, missing_tools: list):
    phase("Phase 6 — Screenshots with GoWitness")

    if "gowitness" in missing_tools:
        warn("gowitness not found — skipping screenshots")
        warn("Install: go install github.com/sensepost/gowitness@latest")
        return

    if not live_domains:
        warn("No live domains — skipping screenshots")
        return

    # ── Prepare sites file ────────────────────────────────────────────────
    sites_file     = os.path.join(dirs["screenshots"], "sites.txt")
    screenshot_dir = os.path.join(dirs["screenshots"], "captures")
    db_file        = os.path.join(dirs["screenshots"], "gowitness.sqlite3")
    os.makedirs(screenshot_dir, exist_ok=True)

    with open(sites_file, "w") as f:
        for d in live_domains:
            d = d.strip()
            if not d.startswith("http"):
                d = "https://" + d
            f.write(d + "\n")

    info(f"Targets written: {len(live_domains)} URLs → {sites_file}")

    # ── Detect version ────────────────────────────────────────────────────
    ver = _gowitness_version()
    info(f"Detected gowitness version: v{ver if ver else '?'} (using {'v3' if ver == 3 else 'v2'} syntax)")

    # ── Run gowitness ─────────────────────────────────────────────────────
    cmd = _build_gowitness_cmd(ver, sites_file, screenshot_dir, db_file)
    info(f"Running: {cmd}")

    # gowitness must be run with CWD = screenshot_dir so it writes PNGs there
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=screenshot_dir,
            capture_output=False, text=True, timeout=600
        )
        if result.returncode != 0:
            warn(f"gowitness exited with code {result.returncode}")
    except subprocess.TimeoutExpired:
        warn("gowitness timed out after 600 seconds")
    except Exception as e:
        error(f"gowitness error: {e}")

    # ── v3 edge-case: screenshots might land in CWD instead of --destination
    #    Move any stray PNGs from the screenshots base dir into captures/
    base_dir = dirs["screenshots"]
    for fname in os.listdir(base_dir):
        if fname.endswith(".png"):
            src = os.path.join(base_dir, fname)
            dst = os.path.join(screenshot_dir, fname)
            os.rename(src, dst)
            info(f"Moved stray screenshot → captures/{fname}")

    # ── Collect results ───────────────────────────────────────────────────
    screens = sorted(f for f in os.listdir(screenshot_dir) if f.endswith(".png"))

    if screens:
        success(f"Screenshots captured: {len(screens)} → {screenshot_dir}")
    else:
        warn("No screenshots were captured.")
        warn("Possible causes:")
        warn("  • Chrome / Chromium is not installed (required by gowitness)")
        warn("  • All targets timed out or refused connections")
        warn("  • Run manually to debug: gowitness single https://<target>")

    # ── Build HTML report ─────────────────────────────────────────────────
    report_html = os.path.join(dirs["screenshots"], "screenshot_report.html")

    # Map filename → original URL for labels
    url_map = {}
    for d in live_domains:
        d = d.strip()
        if not d.startswith("http"):
            d = "https://" + d
        # gowitness names PNGs by URL-encoding the full URL
        safe = re.sub(r'[^\w\-]', '_', d)[:120]
        url_map[safe] = d

    with open(report_html, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>JSRecon Screenshot Report — Rahul Masal</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#0d1117;color:#c9d1d9;font-family:'Courier New',monospace;padding:24px}}
    header{{border-bottom:1px solid #30363d;padding-bottom:16px;margin-bottom:24px}}
    header h1{{color:#58a6ff;font-size:22px}}
    header p{{color:#8b949e;font-size:13px;margin-top:6px}}
    .stats{{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap}}
    .stat{{background:#161b22;border:1px solid #30363d;border-radius:6px;
           padding:12px 20px;text-align:center}}
    .stat .num{{font-size:28px;font-weight:bold;color:#58a6ff}}
    .stat .lbl{{font-size:11px;color:#8b949e;margin-top:4px}}
    .search{{margin-bottom:20px}}
    .search input{{background:#161b22;border:1px solid #30363d;border-radius:6px;
                   color:#c9d1d9;padding:8px 14px;width:100%;max-width:500px;
                   font-family:inherit;font-size:13px;outline:none}}
    .search input:focus{{border-color:#58a6ff}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:16px}}
    .card{{background:#161b22;border:1px solid #30363d;border-radius:8px;
           overflow:hidden;transition:border-color .2s}}
    .card:hover{{border-color:#58a6ff}}
    .card img{{width:100%;display:block;cursor:zoom-in;
               border-bottom:1px solid #30363d;background:#0d1117}}
    .card .meta{{padding:10px 12px}}
    .card .url{{color:#79c0ff;font-size:11px;word-break:break-all;
                text-decoration:none}}
    .card .url:hover{{text-decoration:underline}}
    .card .fname{{color:#484f58;font-size:10px;margin-top:4px}}
    .empty{{text-align:center;padding:60px;color:#484f58}}
    .empty h2{{font-size:18px;color:#8b949e;margin-bottom:10px}}
    .lightbox{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.9);
               z-index:999;align-items:center;justify-content:center;cursor:zoom-out}}
    .lightbox.active{{display:flex}}
    .lightbox img{{max-width:95vw;max-height:95vh;border-radius:6px;
                   box-shadow:0 0 60px rgba(0,0,0,.8)}}
    .lightbox .close{{position:fixed;top:16px;right:24px;color:#fff;
                      font-size:28px;cursor:pointer;z-index:1000}}
  </style>
</head>
<body>
<header>
  <h1>📸 Screenshot Report</h1>
  <p>JSRecon Cyborg Edition V1 — by <strong style="color:#f85149">Rahul Masal</strong>
     &nbsp;|&nbsp; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
     &nbsp;|&nbsp; Target count: {len(live_domains)}</p>
</header>

<div class="stats">
  <div class="stat"><div class="num">{len(live_domains)}</div><div class="lbl">Targets</div></div>
  <div class="stat"><div class="num" id="cap-count">{len(screens)}</div><div class="lbl">Captured</div></div>
  <div class="stat"><div class="num">{len(live_domains) - len(screens)}</div><div class="lbl">Failed</div></div>
</div>

<div class="search">
  <input type="text" id="search" placeholder="🔍  Filter by URL or filename..." oninput="filterCards()">
</div>

<div class="grid" id="grid">
""")
        if not screens:
            f.write("""  <div class="empty" style="grid-column:1/-1">
    <h2>⚠ No screenshots captured</h2>
    <p>Make sure Chrome/Chromium is installed and gowitness can reach the targets.</p>
    <p style="margin-top:10px;font-size:12px">Debug: <code>gowitness single https://example.com</code></p>
  </div>\n""")
        else:
            for screen in screens:
                # Try to recover original URL from filename
                label = screen.replace("_", "/").replace(".png", "")
                f.write(
                    f'  <div class="card" data-name="{screen.lower()}">\n'
                    f'    <img src="captures/{screen}" loading="lazy" '
                    f'         alt="{screen}" onclick="openLightbox(this.src)">\n'
                    f'    <div class="meta">\n'
                    f'      <a class="url" href="captures/{screen}" target="_blank">{screen}</a>\n'
                    f'      <div class="fname">{screen}</div>\n'
                    f'    </div>\n'
                    f'  </div>\n'
                )
        f.write(f"""</div>

<div class="lightbox" id="lightbox" onclick="closeLightbox()">
  <span class="close" onclick="closeLightbox()">✕</span>
  <img id="lb-img" src="" alt="">
</div>

<script>
function openLightbox(src){{
  document.getElementById('lb-img').src = src;
  document.getElementById('lightbox').classList.add('active');
}}
function closeLightbox(){{
  document.getElementById('lightbox').classList.remove('active');
  document.getElementById('lb-img').src = '';
}}
document.addEventListener('keydown', e => {{ if(e.key==='Escape') closeLightbox(); }});
function filterCards(){{
  const q = document.getElementById('search').value.toLowerCase();
  let vis = 0;
  document.querySelectorAll('.card').forEach(c => {{
    const show = !q || c.dataset.name.includes(q);
    c.style.display = show ? '' : 'none';
    if(show) vis++;
  }});
  document.getElementById('cap-count').textContent = vis;
}}
</script>
</body></html>
""")

    success(f"Screenshot HTML report → {report_html}")
    if screens:
        info(f"Open in browser: file://{os.path.abspath(report_html)}")

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7 — FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# CONFIG LOADER  (.env file in same directory as the script)
# ─────────────────────────────────────────────────────────────────────────────
def load_config() -> dict:
    """
    Load notification credentials from jsrecon.env in the script directory.
    Never hardcode credentials in source code.
    """
    cfg = {
        "telegram_bot_token": "",
        "telegram_chat_id":   "",
        "discord_webhook_url": "",
    }
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jsrecon.env")
    if not os.path.exists(env_path):
        return cfg
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                k = k.strip().lower()
                v = v.strip().strip('"').strip("'")
                if k in cfg:
                    cfg[k] = v
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

    # Sensitive paths
    sens_paths = []
    sp_file = os.path.join(dirs["paths"], "findings_unique.txt")
    if os.path.exists(sp_file):
        sens_paths = [l.strip() for l in open(sp_file) if l.strip()]

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

    # ── Build severity rows ───────────────────────────────────────────────
    finding_rows = ""
    row_idx = 0
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        for f in findings_by_sev[sev]:
            row_idx += 1
            matches_html = ""
            for m in f["matches"][:5]:
                safe = m[:180].replace("<", "&lt;").replace(">", "&gt;")
                matches_html += f'<code class="match-line">{safe}</code>'
            if len(f["matches"]) > 5:
                matches_html += (f'<span class="more-badge">+{len(f["matches"])-5} more</span>')
            finding_rows += f"""
<tr class="finding-row sev-{sev.lower()}">
  <td class="td-num">{row_idx}</td>
  <td>{_sev_badge(sev)}</td>
  <td><span class="score-pill" style="color:{f['color']}">{f['score']}</span></td>
  <td class="td-cat">{f['category']}</td>
  <td class="td-url"><a href="{f['url']}" target="_blank" class="url-link">{f['url'][:80]}{'…' if len(f['url'])>80 else ''}</a></td>
  <td class="td-matches">{matches_html}</td>
</tr>"""

    # ── Sensitive paths rows ──────────────────────────────────────────────
    path_rows = ""
    for i, p in enumerate(sens_paths[:50], 1):
        safe_p = p.replace("<","&lt;").replace(">","&gt;")
        path_rows += f"""
<tr>
  <td class="td-num">{i}</td>
  <td>{_sev_badge("HIGH")}</td>
  <td><a href="{p}" target="_blank" class="url-link">{safe_p}</a></td>
</tr>"""
    if not path_rows:
        path_rows = '<tr><td colspan="3" class="td-empty">No sensitive paths found</td></tr>'

    # ── Endpoint rows ─────────────────────────────────────────────────────
    ep_rows = ""
    for i, ep in enumerate(endpoints[:100], 1):
        safe_ep = ep.replace("<","&lt;").replace(">","&gt;")
        ep_rows += f'<tr><td class="td-num">{i}</td><td class="td-ep">{safe_ep}</td></tr>'
    if not ep_rows:
        ep_rows = '<tr><td colspan="2" class="td-empty">No API endpoints found</td></tr>'

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
      <thead><tr><th>#</th><th>Severity</th><th>URL</th></tr></thead>
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
      <thead><tr><th>#</th><th>Endpoint</th></tr></thead>
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


def send_telegram(cfg: dict, target_name: str, report_stats: dict,
                  secrets_data: list, pdf_path: str, html_path: str):
    """Send summary message + PDF/HTML report to Telegram."""
    token   = cfg.get("telegram_bot_token", "").strip()
    chat_id = cfg.get("telegram_chat_id", "").strip()

    if not token or not chat_id:
        warn("Telegram credentials not configured — skipping Telegram notification")
        warn("  Edit jsrecon.env and set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return

    info("Sending Telegram notification...")

    # Build summary
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

    sev_line = (f"🔴 CRIT: {sev_counts['CRITICAL']}  "
                f"🟠 HIGH: {sev_counts['HIGH']}  "
                f"🟡 MED: {sev_counts['MEDIUM']}  "
                f"🔵 LOW: {sev_counts['LOW']}")

    msg = (
        f"⚡ *JSRecon Cyborg V1 — by Rahul Masal*\n"
        f"{'─'*35}\n"
        f"🎯 *Target:* `{target_name}`\n"
        f"🕐 *Date:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"📊 *Severity:* `{overall_sev}` (CVSS {overall_score:.1f})\n"
        f"{sev_line}\n\n"
        f"📈 *Stats*\n"
        f"• Subdomains: `{report_stats.get('subdomains',0)}`\n"
        f"• Live Hosts: `{report_stats.get('live',0)}`\n"
        f"• Total URLs: `{report_stats.get('combined',0)}`\n"
        f"• JS Files:   `{report_stats.get('js',0)}`\n"
        f"• Secrets:    `{len(secrets_data)}` files\n"
        f"• Endpoints:  `{report_stats.get('endpoints',0)}`\n"
        f"• Sens Paths: `{report_stats.get('sensitive',0)}`\n\n"
        f"📎 Full report attached below ↓"
    )

    # Send text message
    _tg_post(token, chat_id, {
        "chat_id":    chat_id,
        "text":       msg,
        "parse_mode": "Markdown",
    })

    # Send PDF if available, else HTML
    attach_path = pdf_path if pdf_path and os.path.exists(pdf_path) else html_path
    if attach_path and os.path.exists(attach_path):
        fname = os.path.basename(attach_path)
        mime  = "application/pdf" if attach_path.endswith(".pdf") else "text/html"
        with open(attach_path, "rb") as fh:
            fdata = fh.read()

        # Telegram max file size for bots: 50 MB
        if len(fdata) > 50 * 1024 * 1024:
            warn("Report file too large for Telegram (>50 MB) — sending text summary only")
        else:
            boundary = "JSReconTGBoundary7x"
            body = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
                f'{chat_id}\r\n'
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="caption"\r\n\r\n'
                f'JSRecon Report — {target_name}\r\n'
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="document"; filename="{fname}"\r\n'
                f'Content-Type: {mime}\r\n\r\n'
            ).encode() + fdata + f'\r\n--{boundary}--\r\n'.encode()

            url = f"https://api.telegram.org/bot{token}/sendDocument"
            try:
                req = urllib.request.Request(
                    url, data=body,
                    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    if resp.status == 200:
                        success(f"Telegram: report file sent ({fname})")
                    else:
                        warn(f"Telegram: document send returned {resp.status}")
            except Exception as e:
                warn(f"Telegram document upload failed: {e}")
    else:
        warn("No report file to attach to Telegram message")


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

    # HTML report
    html_path = generate_html_report(dirs, target_name, elapsed, secrets_data, stats)

    # PDF export
    pdf_path = export_pdf(html_path)

    # Load notification config
    cfg = load_config()

    # Telegram notification
    send_telegram(cfg, target_name, stats, secrets_data, pdf_path, html_path)

    # Discord (critical/high only)
    send_discord(cfg, target_name, secrets_data)

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

    # Check tools
    missing_tools = check_tools()

    if args.js_only:
        # Read JS URLs from stdin
        info("JS-only mode: reading JS URLs from stdin...")
        js_urls = [l.strip() for l in sys.stdin if l.strip()]
        phase_js_analysis(js_urls, dirs)
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

    combined_file, all_urls = phase_url_collection(
        live_domains, subfinder_file, dirs, missing_tools
    )

    # Phase 4 — Filter URLs + extract JS
    js_file, js_urls = phase_filter_urls(combined_file, dirs)

    # Phase 5 — JS Analysis
    phase_js_analysis(js_urls, dirs)

    # Phase 6 — Screenshots
    if not args.skip_screenshots:
        phase_screenshots(live_domains, dirs, missing_tools)
    else:
        info("Screenshots skipped (--skip-screenshots)")

    # Phase 7 — Final Report
    generate_report(dirs, target_name, start_time)


if __name__ == "__main__":
    main()
