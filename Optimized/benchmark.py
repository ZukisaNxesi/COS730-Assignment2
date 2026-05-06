"""
COS 730 – Assignment 2
Task 6: Empirical Evaluation Script
Runs N iterations of both systems and collects metrics.
"""

import time
import sys
import os
import statistics

sys.path.insert(0, os.path.dirname(__file__))

from baseline   import build_baseline_system  as build_base
from optimised  import build_optimised_system as build_opt

RUNS = 200

SAMPLE_DATA = {
    "title":   "Deep Learning in NLP",
    "author":  "Z. Nxesi",
    "content": "This paper explores transformer-based NLP approaches.",
    "topic":   "NLP"
}

def benchmark(build_fn, label, runs=RUNS):
    times  = []
    calls  = []

    for _ in range(runs):
        ui, ctrl = build_fn()
        t0 = time.perf_counter()
        result = ui.submitResearchOutput(dict(SAMPLE_DATA))
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)   # ms
        calls.append(result.get("calls", 0))

    return {
        "label"       : label,
        "runs"        : runs,
        "avg_time_ms" : round(statistics.mean(times), 4),
        "std_time_ms" : round(statistics.stdev(times), 4),
        "min_time_ms" : round(min(times), 4),
        "max_time_ms" : round(max(times), 4),
        "avg_calls"   : round(statistics.mean(calls), 2),
        "min_calls"   : min(calls),
        "max_calls"   : max(calls),
    }

if __name__ == "__main__":
    import json
    base_metrics = benchmark(build_base, "Baseline",   RUNS)
    opt_metrics  = benchmark(build_opt,  "Optimised",  RUNS)

    print(json.dumps({"baseline": base_metrics, "optimised": opt_metrics}, indent=2))

