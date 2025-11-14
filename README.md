# Server Lab  
**Home Lab for learning Linux, Networking, Automation & Server Management**

[![CI/CD](https://github.com/PiotrPaluch67/server-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/PiotrPaluch67/server-lab/actions)  
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)  
![Python](https://img.shields.io/badge/Python-3.11-yellow?logo=python)  
![Bash](https://img.shields.io/badge/Bash-Automated-green?logo=gnu-bash)

---

## Overview

This project simulates a **real-world infrastructure environment** using **VirtualBox + Ubuntu**.  
It demonstrates **progressive skill-building** from manual setup to full automation:

1. **Manual server setup**  
2. **Bash automation** (idempotent, logging, dry-run)  
3. **Python scripting** (network scanner, JSON/CSV export)  
4. **Docker containerization** (hardened NGINX, health checks)  
5. **CI/CD pipeline** (GitHub Actions)

---

## Live Demo

**Hardened NGINX Web Server**  
Run locally:  
```bash
docker-compose up -d