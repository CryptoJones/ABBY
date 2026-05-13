#!/bin/bash
# RunPod startup script for ABBY — handles SSH, then delegates to launch.sh
set -e

LOG=/workspace/logs/run.log
mkdir -p /workspace/logs
exec > >(tee -a "$LOG") 2>&1

echo "=== ABBY startup $(date) ==="

# SSH setup
apt-get install -y -q openssh-server 2>/dev/null || true
ssh-keygen -A 2>/dev/null || true
mkdir -p /root/.ssh /run/sshd
if [ -n "$PUBLIC_KEY" ]; then
    echo "$PUBLIC_KEY" > /root/.ssh/authorized_keys
    chmod 700 /root/.ssh
    chmod 600 /root/.ssh/authorized_keys
fi
/usr/sbin/sshd || true

# Pull latest and train
cd /workspace
if [ -d ABBY ]; then
    git -C ABBY pull
else
    git clone https://codeberg.org/Ronin48/ABBY.git
fi

bash /workspace/ABBY/scripts/launch.sh
