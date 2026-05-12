#!/usr/bin/env python3
"""
Merge ABBY LoRA adapter into base model for deployment.
Requires ~140GB system RAM.
"""

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def merge(adapter_path: str, output_path: str, base_model: str):
    print(f"Loading base model: {base_model}")
    model = AutoModelForCausalLM.from_pretrained(
        base_model, torch_dtype=torch.bfloat16, device_map="cpu"
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model)

    print(f"Loading adapter: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)

    print("Merging adapter into base model...")
    model = model.merge_and_unload()

    print(f"Saving merged model to {output_path}")
    Path(output_path).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    print("✓ Merge complete.")


def main():
    parser = argparse.ArgumentParser(description="Merge ABBY LoRA adapter")
    parser.add_argument("--adapter", default="output/abby-qlora/final")
    parser.add_argument("--output", default="output/abby-merged")
    parser.add_argument("--base-model", default="meta-llama/Llama-3.3-70B-Instruct")
    args = parser.parse_args()
    merge(args.adapter, args.output, args.base_model)


if __name__ == "__main__":
    main()
