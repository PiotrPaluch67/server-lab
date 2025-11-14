# Server setup notes
```bash
#!/bin/bash - tells the OS to run this file with /bin/bash 

# =============================================================================
# Server Lab Bootstrap Script
# Purpose: Secure, idempotent server setup for learning SysAdmin/DevOps/CyberSec
# Features: Logging, validation, SSH keys, UFW, user creation, --dry-run
# =============================================================================
# - Header comment - documentation for person reading the script

set -euo pipefail  # Safer bash
# -e: exit if any command fails
# -u: treat unset variables as error
# -o pipefail: pipelines fail if any part fails


# -------------------------------
# 1. Input Validation
# -------------------------------
if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root. Use: sudo $0"
   exit 1
fi
# $EUID is the effective user ID. Must be 0 (root). If not = abort.

if ! grep -q "Ubuntu" /etc/os-release; then
   echo "ERROR: This script only works on Ubuntu."
   exit 1
fi
# checks that the OS is Ubuntu by looking at /etc/os-release

UBUNTU_VERSION=$(lsb_release -rs)
#capture ubuntu version

if [[ "$(echo "$UBUNTU_VERSION < 20.04" | bc -l)" -eq 1 ]]; then
   echo "ERROR: Ubuntu 20.04 or higher required. Found: $UBUNTU_VERSION"
   exit 1
fi
# compare version using `bc`

# -------------------------------
# 2. Parse --dry-run flag
# -------------------------------
DRY_RUN=false
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Usage: sudo $0 [--dry-run]"
            exit 1
            ;;
    esac
done
#argument parser. Only supports --dry-run

# -------------------------------
# 3. Logging Setup
# -------------------------------
LOG_FILE="/var/log/server-lab.log"
if ! $DRY_RUN; then
    touch "$LOG_FILE" 2>/dev/null || {
        echo "ERROR: Cannot write to $LOG_FILE. Check permissions."
        exit 1
    }
    chmod 644 "$LOG_FILE"
fi
# create log file only if not in dry-run mode
# 644 = owner rw, others r (standard for logs)

log() {
    local msg="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $msg" | tee -a "$LOG_FILE"
}
# log function: prints to screen and appends to log file

log "=== Server Lab Bootstrap Started ==="
$DRY_RUN && log "DRY RUN MODE: No changes will be made."
# first log entries

# -------------------------------
# 4. Helper: Run command (with dry-run)
# -------------------------------
run() {
    if $DRY_RUN; then
        log "[DRY RUN] Would execute: $*"
    else
        log "Executing: $*"
        "$@" #runs the command
    fi
}
# wrapper: logs and conditionally executes ant command

# -------------------------------
# 5. Update & Install Packages
# -------------------------------
log "Updating package list..."
run apt update
# refresh package index

PACKAGES="vim curl git ufw openssh-server net-tools"
for pkg in $PACKAGES; do
    if dpkg -l | grep -q "^ii  $pkg "; then
        log "$pkg already installed — skipping."
    else
        log "Installing $pkg..."
        run apt install -y "$pkg"
    fi
done
# only installs if not present

# -------------------------------
# 6. Create Lab User (labadmin)
# -------------------------------
LAB_USER="labadmin"
if id "$LAB_USER" &>/dev/null; then
    log "User '$LAB_USER' already exists — skipping."
else
    log "Creating user '$LAB_USER' with passwordless sudo..."
    run useradd -m -s /bin/bash "$LAB_USER"
    run usermod -aG sudo "$LAB_USER"
    echo "$LAB_USER ALL=(ALL) NOPASSWD:ALL" | run tee /etc/sudoers.d/$LAB_USER
    run chmod 440 /etc/sudoers.d/$LAB_USER
fi
# creates user only if missing
# adds to sudo group and gives passwordless sudo

# -------------------------------
# 7. SSH Key Setup (for labadmin)
# -------------------------------
USER_HOME=$(eval echo ~$LAB_USER)
SSH_DIR="$USER_HOME/.ssh"
KEY_FILE="$SSH_DIR/id_rsa"
# get home directory of labadmin

if [ ! -d "$SSH_DIR" ]; then
    log "Creating .ssh directory for $LAB_USER..."
    run mkdir -p "$SSH_DIR"
    run chmod 700 "$SSH_DIR"
    run chown $LAB_USER:$LAB_USER "$SSH_DIR"
fi
# create .ssh with correct permissions and ownership

if [ ! -f "$KEY_FILE" ]; then
    log "Generating SSH key pair for $LAB_USER..."
    run ssh-keygen -t rsa -b 4096 -f "$KEY_FILE" -N "" -q
    run chown $LAB_USER:$LAB_USER "$KEY_FILE"*
else
    log "SSH key already exists — skipping."
fi
# generate 4096-bit RSA key (no passphrase, quiet mode)

# Add public key to authorized_keys
AUTH_FILE="$SSH_DIR/authorized_keys"
if ! grep -q "$(cat "$KEY_FILE.pub")" "$AUTH_FILE" 2>/dev/null; then
    log "Adding public key to authorized_keys..."
    run cat "$KEY_FILE.pub" >> "$AUTH_FILE"
    run chmod 600 "$AUTH_FILE"
    run chown $LAB_USER:$LAB_USER "$AUTH_FILE"
else
    log "Public key already in authorized_keys — skipping."
fi
# ensure public key is authorized_keys

# -------------------------------
# 8. Firewall (UFW)
# -------------------------------
if ufw status | grep -q "Status: active"; then
    log "UFW already active — skipping enable."
else
    log "Enabling UFW..."
    run ufw --force enable
fi
# enable firewall if not active

# Allow only needed ports
for port in 22 80 443; do
    if uadmin ufw status | grep -q "$port.*ALLOW"; then
        log "UFW rule for port $port already exists — skipping."
    else
        log "Allowing port $port/tcp..."
        run ufw allow "$port/tcp" comment "Lab service"
    fi
done

run ufw reload
log "UFW configured."
# apply changes

# -------------------------------
# 9. Final Message
# -------------------------------
log "=== Bootstrap Completed Successfully! ==="
echo
echo "Server Lab is ready!"
echo "   User: $LAB_USER (use 'su - $LAB_USER')"
echo "   SSH:  Key generated at $KEY_FILE"
echo "   Log:  $LOG_FILE"
$DRY_RUN && echo "   (This was a DRY RUN — no changes made)"
echo
# summary for user

exit 0
# exit with success code
```