# Bash Scripting – Basics
# 1. Create a Script

```bash
nano myscript.sh          # open editor
# (type your commands)
# Press Ctrl+O → Enter → Ctrl+X to save & exit

chmod +x myscript.sh #Add execute permission for everyone

chmod 700 file #Owner: read+write+execute → rwx------
chmod 644 file #Owner: rw, others: r → rw-r--r--

#Octal numbers
#4 = read, 2 = write, 1 = execute → add them up:
#7 = rwx, 6 = rw-, 5 = r-x
```

# Basic Script Example
```bash
#!/bin/bash
echo "Hello, $(whoami)!"
echo "Today is $(date '+%Y-%m-%d')"
```

# If-Check
```bash
if [[ $EUID -ne 0 ]]; then
    echo "Run as root!"
    exit 1
fi
```

# Dry-Run (Safe Testing)
```bash
#!/bin/bash
DRY_RUN=false
[[ "$1" == "--dry-run" ]] && DRY_RUN=true

run() {
    if $DRY_RUN; then
        echo "[DRY RUN] $*"
    else
        "$@"
    fi
}

run apt update
```
