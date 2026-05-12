#!/bin/bash
# RunPod startup script for ABBY QLoRA training.
# Handles SSH setup, dependency install, data prep, and training.
set -e

LOG=/workspace/logs/run.log
mkdir -p /workspace/logs
exec > >(tee -a "$LOG") 2>&1

echo "=== ABBY startup $(date) ==="

# SSH setup
echo "[ssh] configuring..."
apt-get install -y -q openssh-server 2>/dev/null || true
ssh-keygen -A 2>/dev/null || true
mkdir -p /root/.ssh /run/sshd
if [ -n "$PUBLIC_KEY" ]; then
    echo "$PUBLIC_KEY" > /root/.ssh/authorized_keys
    chmod 700 /root/.ssh
    chmod 600 /root/.ssh/authorized_keys
fi
/usr/sbin/sshd || true
echo "[ssh] done"

# Pull latest ABBY
echo "[git] pulling ABBY..."
cd /workspace
if [ -d ABBY ]; then
    cd ABBY && git pull
else
    git clone https://codeberg.org/Ronin48/ABBY.git && cd ABBY
fi

# Install Python deps
echo "[pip] installing dependencies..."
pip install -q \
    "transformers==4.44.2" \
    "peft==0.12.0" \
    "trl==0.11.4" \
    "bitsandbytes>=0.41.0" \
    "accelerate" \
    "datasets" \
    "pyyaml" \
    "requests" \
    "tqdm"

# Generate synthetic data and prepare dataset
echo "[data] generating synthetic examples..."
python scripts/data_collection/generate_synthetic.py

echo "[data] preparing dataset..."
python scripts/training/prepare_dataset.py

# Train
echo "[train] starting QLoRA training..."
python scripts/training/train_qlora.py --config configs/training_config.yaml

echo "=== ABBY training complete $(date) ==="
