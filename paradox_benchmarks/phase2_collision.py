"""Phase 2 — Collision Testing.

Generate large sets of keys and check for duplicates.
"""

import os
import time
from pathlib import Path
from typing import Any, Dict

from paradox_benchmarks.utils import load_test_image, gen_key, header, progress


def _collision_test(label: str, n: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate *n* keys with random nonces and check for collisions."""
    print(f"  {label}: generating {n:,} keys …")
    img = load_test_image(64, 64, seed=42)
    keys = set()
    collisions = 0
    t0 = time.perf_counter()

    if n >= 500:
        from paradox_benchmarks.utils import gen_keys_parallel

        nonces = [os.urandom(32) for _ in range(n)]
        all_keys = gen_keys_parallel(img.path, nonces, security_level="low")
        for k in all_keys:
            if k in keys:
                collisions += 1
            keys.add(k)
    else:
        for i in range(n):
            k, _ = gen_key(img, nonce=os.urandom(32), security_level="low")
            if k in keys:
                collisions += 1
            keys.add(k)
            if (i + 1) % max(1, n // 40) == 0 or i == n - 1:
                progress(i + 1, n, "Keys")

    elapsed = time.perf_counter() - t0
    rate = collisions / n if n else 0
    passed = collisions == 0

    print(f"    Collisions: {collisions}  |  Rate: {rate:.6%}  |  Time: {elapsed:.1f}s")
    print(f"    {'PASS ✓' if passed else 'FAIL ✗'}")

    return {
        "total_keys": n,
        "unique_keys": len(keys),
        "collisions": collisions,
        "collision_rate": rate,
        "elapsed_s": round(elapsed, 2),
        "passed": passed,
    }


def run(output_dir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    header("PHASE 2: COLLISION TESTING")

    n1 = config.get("phase2_n1", 1000)
    n2 = config.get("phase2_n2", 2000)

    results: Dict[str, Any] = {}
    results["batch_1"] = _collision_test(f"Batch 1 ({n1:,} keys)", n1, config)
    results["batch_2"] = _collision_test(f"Batch 2 ({n2:,} keys)", n2, config)

    results["overall_collision_rate"] = (
        results["batch_1"]["collisions"] + results["batch_2"]["collisions"]
    ) / (n1 + n2)
    results["all_passed"] = (
        results["batch_1"]["passed"] and results["batch_2"]["passed"]
    )
    print(f"\n  Phase 2 overall: {'PASS ✓' if results['all_passed'] else 'FAIL ✗'}")
    return results
