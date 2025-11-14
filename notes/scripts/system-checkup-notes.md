# script output  `system_check.sh`

```text
==== System Check ====
Date: Sun 09 Nov 2025 09:58:08 PM UTC
Hostname: ubuntu
Uptime: up 28 minutes
-----------------------------
Logged-in users:
user     seat0        2025-11-09 21:29 (login screen)
user     tty2         2025-11-09 21:29 (tty2)
-----------------------------
Disk usage:
/dev/sda2        30G  7.5G   21G  27% /
/dev/sr0         51M   51M     0 100% /media/user/VBox_GAs_7.2.21
-----------------------------
Memory usage:
               total        used        free      shared  buff/cache   available
Mem:           8.6Gi       1.6Gi       5.8Gi        91Mi       1.5Gi       7.0Gi
Swap:             0B          0B          0B
-----------------------------
IP addresses:
    inet 127.0.0.1/8 scope host lo
    inet 192.168.x.x brd 192.168.x.x scope global dynamic noprefixroute enp0s3
=============================
```

# script code `system_check.sh`
```text
echo "==== System Check ===="
echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime -p)"
echo "-----------------------------"
echo "Logged-in users:"
who
echo "-----------------------------"
echo "Disk usage:"
df -h | grep '^/dev/'
echo "-----------------------------"
echo "Memory usage:"
free -h
echo "-----------------------------"
echo "IP addresses:"
ip -4 addr show | grep inet
echo "============================="
```