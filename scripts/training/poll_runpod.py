#!/usr/bin/env python3
"""Poll RunPod pod status and GPU utilization."""

import json
import subprocess
import sys
import time

import requests

POD_ID = "84xy4l8wxo79o8"


def get_key():
    try:
        return subprocess.check_output(["pass", "show", "runpod/api-key"], text=True).strip()
    except Exception:
        return sys.argv[1] if len(sys.argv) > 1 else ""


def query(q, key):
    resp = requests.post(
        "https://api.runpod.io/graphql",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"query": q},
        timeout=30,
    )
    return resp.json()


def main():
    key = get_key()
    q = """{ pod(input: {podId: "%s"}) {
        desiredStatus
        runtime { uptimeInSeconds ports { ip publicPort privatePort type } }
        latestTelemetry { cpuUtilization memoryUtilization gpuUtilization gpuMemoryUtilization }
    } }""" % POD_ID

    print("Polling ABBY pod (Ctrl-C to stop)...\n")
    while True:
        d = query(q, key)
        pod = d["data"]["pod"]
        rt = pod.get("runtime") or {}
        telem = pod.get("latestTelemetry") or {}
        uptime = rt.get("uptimeInSeconds", 0)
        ports = [(p["publicPort"], p["privatePort"]) for p in (rt.get("ports") or [])]
        gpu = telem.get("gpuUtilization", "?")
        gpu_mem = telem.get("gpuMemoryUtilization", "?")
        cpu = telem.get("cpuUtilization", "?")
        print(f"uptime={uptime}s  cpu={cpu}%  gpu={gpu}%  gpu_mem={gpu_mem}%  ports={ports}")
        time.sleep(30)


if __name__ == "__main__":
    main()
