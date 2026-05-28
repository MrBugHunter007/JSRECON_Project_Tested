#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════╗
# ║   JSRecon Cyborg Edition V1 — by Rahul Masal            ║
# ║   Dependency Installer                                   ║
# ╚══════════════════════════════════════════════════════════╝

set -e

RED='\033[91m'; GREEN='\033[92m'; YELLOW='\033[93m'
CYAN='\033[96m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[*]${RESET} $1"; }
success() { echo -e "${GREEN}[✔]${RESET} $1"; }
warn()    { echo -e "${YELLOW}[!]${RESET} $1"; }
error()   { echo -e "${RED}[✘]${RESET} $1"; }

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║        JSRecon Cyborg Edition V1 — by Rahul Masal               ║
║        Dependency Installer                                      ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"

# ── Python packages ───────────────────────────────────────────────
info "Installing Python dependencies..."
pip3 install jsbeautifier requests 2>/dev/null && success "Python packages installed" || warn "pip3 failed — install manually: pip3 install jsbeautifier requests"

# ── Go tools ─────────────────────────────────────────────────────
if ! command -v go &>/dev/null; then
    warn "Go not found. Please install Go first: https://go.dev/dl/"
    warn "Then re-run this script."
    exit 1
fi

GO_TOOLS=(
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    "github.com/projectdiscovery/httpx/cmd/httpx@latest"
    "github.com/tomnomnom/waybackurls@latest"
    "github.com/jaeles-project/gospider@latest"
    "github.com/projectdiscovery/katana/cmd/katana@latest"
    "github.com/sensepost/gowitness@latest"
)

info "Installing Go tools..."
for tool in "${GO_TOOLS[@]}"; do
    name=$(basename "${tool%%@*}")
    if command -v "$name" &>/dev/null; then
        success "$name already installed"
    else
        info "Installing $name..."
        go install -v "$tool" 2>/dev/null && success "$name installed" || warn "$name install failed — try manually: go install $tool"
    fi
done

# ── PATH check ───────────────────────────────────────────────────
if [[ ":$PATH:" != *":$HOME/go/bin:"* ]]; then
    warn "Add Go bin to PATH:"
    echo -e "  ${YELLOW}export PATH=\$PATH:\$HOME/go/bin${RESET}"
    echo -e "  ${YELLOW}echo 'export PATH=\$PATH:\$HOME/go/bin' >> ~/.bashrc && source ~/.bashrc${RESET}"
fi

success "Installation complete!"
echo ""
echo -e "${CYAN}Usage:${RESET}"
echo -e "  python3 jsrecon.py -d example.com"
echo -e "  python3 jsrecon.py -l domains.txt"
echo -e "  python3 jsrecon.py -d example.com --skip-screenshots"
echo -e "  python3 jsrecon.py -d example.com --js-only < js_urls.txt"
