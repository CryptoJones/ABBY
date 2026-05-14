# Lessons Learned — ABBY Training on RunPod

This document captures every dependency conflict, environment bug, and hard-won fix
encountered during the first ABBY training run. If you're following in our footsteps,
read this before you start.

---

## The Environment Problem

The stock RunPod PyTorch template ships with **torch 2.11.0** (or similar dev/nightly
builds). Most pinned ML package versions on PyPI were built against torch 2.2.x or
earlier. This causes a cascade of incompatibilities that are not obvious from the error
messages. Every fix below traces back to this root cause.

**The solution:** Use the `ronin48/qlora-training` Docker image as your RunPod template.
It has all of this pre-solved. See `docs/RUNPOD.md`.

If you insist on the stock template, read on.

---

## Error Log

### 1. FlashAttention2 ImportError

**Error:**
```
ImportError: FlashAttention2 has been toggled on, but it cannot be used due to the
following error: the package flash_attn seems to be not installed.
```

**Cause:** `configs/training_config.yaml` had `attn_implementation: "flash_attention_2"`
and `train_qlora.py` defaulted to it. The stock RunPod template doesn't have
`flash_attn` installed.

**Fix:** Set `attn_implementation: "eager"` in `configs/training_config.yaml`.
`eager` is slower than flash attention but works everywhere.

---

### 2. bitsandbytes CUDA Library Missing

**Error:**
```
RuntimeError: CUDA SETUP ERROR: Missing dependency: libnvJitLink.so.13
Original error: libnvJitLink.so.13: cannot open shared object file: No such file or directory
```

**Cause:** `libnvJitLink.so.13` ships via pip as part of the `nvidia-cu13` package
but isn't in `LD_LIBRARY_PATH` by default.

**Fix:**
```bash
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/nvidia/cu13/lib:${LD_LIBRARY_PATH:-}
```

Add this to your launch script before running training. It's already in `scripts/launch.sh`.

---

### 3. torchvision Crashes on Import

**Error:**
```
RuntimeError: operator torchvision::nms does not exist
```

**Cause:** The installed torchvision was built for torch 2.2.0. On torch 2.11+, the
internal operator registration API changed. torchvision crashes on import, and
this crash cascades up through transformers → bloom model → peft → your training script.

**Fix:** Uninstall torchvision. We do text-only training — it's not needed.
```bash
pip uninstall torchvision -y
```

This is run automatically by `scripts/launch.sh`.

---

### 4. bitsandbytes Version Too Old

**Error:**
```
Could not find the bitsandbytes CUDA binary at libbitsandbytes_cuda130.so
```

**Cause:** Pinning `bitsandbytes>=0.41.0` resolved to an old version with no
CUDA 13 binary.

**Fix:** Don't pin bitsandbytes. Let pip resolve it against the installed torch/CUDA:
```bash
pip install bitsandbytes
```

---

### 5. triton Version Conflict

**Error:**
```
No module named 'triton.ops'
```

**Cause:** `triton.ops` was removed in triton 3.x. Pinning `bitsandbytes==0.43.1`
pulled in an old bitsandbytes that expected triton 2.x internals.

**Fix:** Don't pin triton or bitsandbytes. Let pip resolve compatible versions.

---

### 6. `.to()` Not Supported on 4-bit Models

**Error:**
```
ValueError: `.to` is not supported for `4-bit` or `8-bit` bitsandbytes models.
Please use the model as it is, since the model has already been set to the correct
devices and casted to the correct `dtype`.
```

**Cause:** Two separate triggers for this error:

1. Passing `torch_dtype=torch.bfloat16` to `AutoModelForCausalLM.from_pretrained()`
   alongside `quantization_config`. bitsandbytes manages dtype internally — you
   can't tell it twice.

2. Passing any `device_map` argument. Even `device_map={"": 0}` causes accelerate's
   `dispatch_model()` to call `.to(device)` on an already-quantized model.

3. Pinned `transformers==4.44.2` with newer bitsandbytes/accelerate. Older
   transformers didn't know to skip `.to()` for quantized models.

**Fix:** Remove both `torch_dtype` and `device_map` from `from_pretrained()`.
bitsandbytes places the model on GPU automatically when `load_in_4bit=True`.
Upgrade transformers to latest.

```python
# Wrong:
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",           # triggers dispatch_model → .to() → crash
    torch_dtype=torch.bfloat16, # conflicts with bitsandbytes dtype management
)

# Right:
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    # let bitsandbytes handle placement and dtype
)
```

---

### 7. peft / transformers Version Mismatch

**Error:**
```
ModuleNotFoundError: Could not import module 'BloomPreTrainedModel'.
```

**Cause:** Pinned `peft==0.12.0` imports `BloomPreTrainedModel` from transformers.
Newer transformers restructured the bloom model internals and this import fails.
Also triggered by the torchvision crash cascading through the transformers import chain.

**Fix:** Unpin peft and let it resolve against the installed transformers:
```bash
pip install peft --upgrade
```

---

### 8. Disk Quota Exceeded

**Error:**
```
OSError: I/O error: IO Error: Disk quota exceeded (os error 122)
```

**Cause:** Llama 3.3 70B weights are ~130GB. A 200GB network volume fills up fast
once you add the synthetic dataset, training checkpoints, and adapter output.

**Fix:** Use a **300GB network volume** minimum. 200GB is not enough.

---

### 9. SSH Connection Refused

**Symptom:** `ssh: connect to host <ip> port <port>: Connection refused`

**Cause:** The RunPod PyTorch template runs `start.sh` which executes `sleep infinity`.
It does not launch sshd. Our `startup.sh` is never executed because `dockerArgs` is
silently ignored when a `templateId` is set.

**Fix:** Use the **RunPod web terminal** instead of SSH.
In the RunPod console: **Connect → Web Terminal**.

Then run training manually:
```bash
HF_TOKEN=your_token bash <(curl -s https://codeberg.org/Ronin48/ABBY/raw/branch/main/scripts/launch.sh)
```

---

### 10. HuggingFace Weights Downloading to Container Disk

**Symptom:** Disk full errors mid-download even with a large network volume attached.

**Cause:** HuggingFace defaults to `~/.cache/huggingface` which is on the 50GB
container disk, not the network volume.

**Fix:** Always set before running anything:
```bash
export HF_HOME=/workspace/hf_cache
```

This is set automatically by `scripts/launch.sh`. If you're running manually,
set it first.

---

## The Golden Path

If you're starting from scratch on RunPod, this is the sequence that works:

1. Deploy a pod with the `ronin48/qlora-training` Docker image (see `docs/RUNPOD.md`)
2. Use a **300GB network volume**
3. Open the **web terminal** (not SSH)
4. Run:
   ```bash
   HF_TOKEN=your_token bash <(curl -s https://codeberg.org/Ronin48/ABBY/raw/branch/main/scripts/launch.sh)
   ```
5. Watch for `[train] starting QLoRA training...` then GPU spike > 10%
6. Walk away — training takes 8–10 hours

To train all four first responder models sequentially on one pod:
```bash
HF_TOKEN=your_token bash <(curl -s https://codeberg.org/Ronin48/SELMA/raw/branch/main/scripts/train_all.sh)
```

---

### 11. bitsandbytes Custom Op Schema Error (PyTorch 2.4 + Python 3.11)

**Error:**
```
ValueError: infer_schema(func): Parameter input has unsupported type torch.Tensor.
Got func with signature (input: 'torch.Tensor', weight: 'torch.Tensor', offs: 'torch.Tensor') -> 'torch.Tensor'
```

**Cause:** Older bitsandbytes versions used string-quoted type annotations (`'torch.Tensor'`)
in custom op registrations. PyTorch 2.4's `infer_schema` rejects string annotations —
it requires the actual `torch.Tensor` type object.

**Fix:** Upgrade bitsandbytes to the latest version:
```bash
pip install --upgrade bitsandbytes
```

---

### 12. transformers MoE Custom Op Schema Error (transformers >= 4.50 + PyTorch 2.4)

**Error:**
```
from .integrations.finegrained_fp8 import ALL_FP8_EXPERTS_FUNCTIONS
...
torch.library.custom_op("transformers::grouped_mm_fallback", _grouped_mm_fallback, mutates_args=())
ValueError: infer_schema(func): Parameter input has unsupported type torch.Tensor.
Got func with signature (input: 'torch.Tensor', weight: 'torch.Tensor', offs: 'torch.Tensor') -> 'torch.Tensor'
```

**Cause:** transformers 4.50+ added FP8/MoE expert integrations (`transformers/integrations/moe.py`)
that register custom ops at import time. The functions use string-quoted type annotations
(`'torch.Tensor'`) that PyTorch 2.4's `infer_schema` rejects. Same root cause as the
bitsandbytes schema error (#11) but in transformers itself.

**Fix:** Pin transformers below 4.50:
```bash
pip install "transformers>=4.46.0,<4.50.0"
```

This is now the pin used in all `scripts/launch.sh` files.

---

### 13. trl / transformers Version Sandwich (PyTorch 2.4)

**Error:**
```
ImportError: cannot import name 'is_trackio_available' from 'transformers'
RuntimeError: Failed to import trl.trainer.sft_trainer
```

**Cause:** trl>=1.0.0 imports `is_trackio_available` from transformers. That symbol only
exists in transformers>=4.50. But transformers>=4.50 crashes on PyTorch 2.4 (see error #12).
Pinning transformers<4.50 to fix error #12 therefore breaks trl>=1.0.0.

**Fix:** Pin trl below 1.0.0 to match the transformers<4.50 constraint:
```bash
pip install "transformers>=4.46.0,<4.50.0" "trl>=0.12.0,<1.0.0"
```

The working version matrix for PyTorch 2.4 + CUDA 12.4:

| Package | Pin | Reason |
|---|---|---|
| transformers | `>=4.46.0,<4.50.0` | 4.50+ has MoE custom_op crash on PyTorch 2.4 |
| trl | `>=0.12.0,<1.0.0` | 1.0+ imports `is_trackio_available` from transformers>=4.50 |
| bitsandbytes | latest (--upgrade) | older versions lack CUDA 13 binaries |
| peft | latest (--upgrade) | |
| accelerate | latest (--upgrade) | |

These pins are now in all `scripts/launch.sh` files.

---

### 14. LD_LIBRARY_PATH Hardcoded to Python 3.10

**Symptom:** bitsandbytes CUDA library not found on images using Python 3.11+.

**Cause:** `launch.sh` had a hardcoded path:
`/usr/local/lib/python3.10/dist-packages/nvidia/cu13/lib`

The `runpod/pytorch:2.4.0-py3.11-cuda12.4.1` image uses Python 3.11, so the path
doesn't exist and the library is never added to `LD_LIBRARY_PATH`.

**Fix:** Derive the path dynamically from Python's own site-packages:
```bash
_nvidia_lib=$(python3 -c "import site; print(site.getsitepackages()[0])")/nvidia/cu13/lib
[ -d "$_nvidia_lib" ] && export LD_LIBRARY_PATH="$_nvidia_lib:${LD_LIBRARY_PATH:-}"
```

This is now in all `scripts/launch.sh` files.

---

### 15. SFTTrainer `tokenizer` Renamed to `processing_class` (trl 0.12+)

**Error:**
```
TypeError: SFTTrainer.__init__() got an unexpected keyword argument 'tokenizer'
```

**Cause:** trl 0.12 renamed the `tokenizer` parameter in `SFTTrainer.__init__()` to
`processing_class` to support non-tokenizer processors.

**Fix:** Replace `tokenizer=tokenizer` with `processing_class=tokenizer` in the
`SFTTrainer(...)` call.

---

### 16. SFTTrainer `max_seq_length` Moved to `SFTConfig` (trl 0.12+)

**Error:**
```
TypeError: SFTTrainer.__init__() got an unexpected keyword argument 'max_seq_length'
```

**Cause:** trl 0.12 moved `max_seq_length` out of `SFTTrainer` and into `SFTConfig`
(a subclass of `TrainingArguments` that adds SFT-specific options).

**Fix:** Replace `TrainingArguments` with `SFTConfig` and pass `max_seq_length` there:

```python
# Wrong (trl < 0.12):
from transformers import TrainingArguments
from trl import SFTTrainer
training_args = TrainingArguments(output_dir=..., ...)
trainer = SFTTrainer(..., max_seq_length=4096)

# Right (trl >= 0.12):
from trl import SFTConfig, SFTTrainer
training_args = SFTConfig(max_seq_length=4096, output_dir=..., ...)
trainer = SFTTrainer(...)
```

---

### 17. transformers Version Creep — `--upgrade` Overrides the Pin

**Symptom:** The schema crash from errors #12 or #13 returns even though the pin is in
`launch.sh`. Usually happens after manually running `pip install --upgrade bitsandbytes`
or reconnecting and re-running pip commands without the full version constraint.

**Cause:** Running `pip install --upgrade <any-package>` without the transformers pin
can pull in transformers 5.x as a transitive dependency, overwriting the pinned version.

**Fix:** Always reinstall the full pinned stack together:
```bash
pip install "transformers>=4.46.0,<4.50.0" "trl>=0.12.0,<1.0.0"
```

Then re-run training. Never run bare `pip install --upgrade transformers`.

---

### 18. Web Terminal Drops Kill the Training Process

**Symptom:** RunPod web terminal disconnects after inactivity. Training process dies with it.

**Cause:** The web terminal runs training as a foreground process in the shell session.
When the browser disconnects, the shell exits and SIGHUP kills the process.

**Fix:** Use `nohup` to run the training process immune to terminal disconnects.
`launch.sh` now does this automatically. If running manually:
```bash
nohup python scripts/training/train_qlora.py --config configs/training_config.yaml >> /workspace/logs/train.log 2>&1 &
```

Then follow progress with:
```bash
tail -f /workspace/logs/train.log
```

If you want an interactive session that survives disconnects, install tmux first
(not included in the base image) and use that instead:
```bash
apt-get install tmux
tmux new -s training
# run your command, then Ctrl+B + D to detach
tmux attach -t training  # to reconnect
```

---

## Package Versions That Work Together

As of May 2026 on `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`:

| Package | Pin | Reason |
|---|---|---|
| transformers | `>=4.46.0,<4.50.0` | 4.50+ adds MoE custom ops that crash on PyTorch 2.4 |
| trl | `>=0.12.0,<1.0.0` | 1.0+ imports `is_trackio_available` from transformers>=4.50 |
| peft | latest (`--upgrade`) | |
| bitsandbytes | latest (`--upgrade`) | old versions lack CUDA 13 binaries |
| accelerate | latest (`--upgrade`) | |
| torchvision | **uninstalled** | Crashes on torch 2.4+ — remove it |
| triton | torch-managed | Don't pin separately |

These pins are baked into all `scripts/launch.sh` files.

---

---

## Error 19: `huggingface-cli` deprecated — upload silently fails

**Symptom:** After training completes, the upload step exits with a deprecation warning and no repo is created on HuggingFace. `Ronin48/xxx-lora-adapter` returns 404.

**Cause:** `huggingface-cli` was deprecated and replaced by `hf`. The old binary no longer functions.

**Fix:** Replace `huggingface-cli upload` with `hf upload` in all `scripts/launch.sh` files and in `training_monitor.py`. Same argument order.

```bash
# Wrong
huggingface-cli upload "$HF_REPO" "$ADAPTER_DIR" --token "$HF_TOKEN"

# Correct
hf upload "$HF_REPO" "$ADAPTER_DIR" --token "$HF_TOKEN"
```

**Applied to:** ABBY, SELMA, BONES, BRUNO `scripts/launch.sh` and `SELMA/scripts/training_monitor.py`.

---

---

### 20. Training Monitor Blind to Disk-Full Crashes — Happened 3 Times

**Symptom:** Monitor reports `GPU 0% | active=False` indefinitely. Training never starts.
Claude says "hasn't kicked off yet" or "waiting to start." Pod burns credits doing nothing.
User eventually tells Claude to SSH in. Crash is discovered.

**Cause — two separate bugs that compound each other:**

1. **Wrong volume size.** Llama-3.3-70B needs ~140 GB just for model weights (30 shards × ~4.7 GB).
   A 100 GB volume fills at shard 22/30 with `OSError: [Errno 28] No space left on device`.
   This kills the process before the GPU is ever touched. See also Error #8.

2. **Wrong cache mount.** If `HF_HOME` is not explicitly set, HuggingFace defaults to
   `~/.cache/huggingface` on the **container disk** (~40 GB), not the network volume.
   The model download fills the container disk in minutes. GPU never activates.
   See also Error #10.

3. **Monitor was blind to this failure mode.** The monitor only detected *completion*
   (GPU goes active → idle). It had no detection for the case where GPU *never* activates.
   `GPU 0% | active=False` with a pod that's been up 45+ minutes is a crashed pod, not
   a pod that's still initializing.

**This happened three times before the monitor was fixed.**

**Fixes applied:**
- `ADAPTERS` config now has `min_disk_gb` per model (BONES/BRUNO = 200 GB, ABBY/SELMA = 80 GB)
- Monitor runs a pre-flight check the first time it sees each pod:
  - Verifies `volumeInGb >= min_disk_gb` via RunPod API
  - SSHs in and checks `$HF_HOME` points to `/workspace`, not `~/.cache`
  - Checks current free space on `/workspace`
- If pod has been up ≥ 45 minutes with GPU never active: Telegram alert, not silence
- Mid-training: polls `df /workspace` every cycle, alerts at 85% full

**Rule: `GPU 0% | active=False` after 20+ minutes means crashed, not waiting.**
SSH in immediately and check `/workspace/logs/train.log`. Do not tell anyone "it hasn't started yet."

---

## Contributing

If you hit a new error and fix it, please add it here. The people walking behind
you will thank you.
