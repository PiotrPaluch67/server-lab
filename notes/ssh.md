# SSH – Secure Shell

## Quick Reference
| Command | Purpose |
|---------|---------|
| `ssh user@host` | Connect to remote host |
| `ssh -p 2222 user@host` | Connect to non-standard port |
| `ssh -i ~/.ssh/id_rsa_lab user@host` | Use specific private key |
| `ssh-copy-id user@host` | Install your public key on remote host |
| `ssh -o StrictHostKeyChecking=no user@host` | Skip host-key prompt (automation) |

## Service Management
```bash
# Check status
sudo systemctl status ssh

# Enable & start
sudo systemctl enable --now ssh

# Restart
sudo systemctl restart ssh