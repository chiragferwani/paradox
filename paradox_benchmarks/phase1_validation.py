"""Phase 1 — Basic Validation.

Tests:
1. Same Image + Same Nonce  → identical keys
2. Same Image + Different Nonces → all unique keys
3. Different Images + Same Nonce → all unique keys
4. Different Images + Different Nonces → no collisions
"""

import os
from pathlib import Path
from typing import Any, Dict

from paradox_benchmarks.utils import (
    load_test_image, gen_key, header, progress,
)


def run(output_dir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    header("PHASE 1: BASIC VALIDATION")
    results: Dict[str, Any] = {}

    img = load_test_image(64, 64, seed=42)
    fixed_nonce = bytes(range(32))
    fixed_ts = 1_700_000_000.0

    # ---- Test 1 ----
    print("  Test 1: Same Image + Same Nonce → identical keys")
    k1, _ = gen_key(img, nonce=fixed_nonce, timestamp=fixed_ts)
    k2, _ = gen_key(img, nonce=fixed_nonce, timestamp=fixed_ts)
    t1 = k1 == k2
    results["test1_same_image_same_nonce"] = {
        "passed": t1,
        "description": "Same Image + Same Nonce → Identical Keys",
    }
    print(f"    {'PASS ✓' if t1 else 'FAIL ✗'}")

    # ---- Test 2 ----
    n = config.get("phase1_diff_nonce_count", 100)
    print(f"  Test 2: Same Image + {n} Different Nonces")
    keys = set()
    for i in range(n):
        k, _ = gen_key(img, nonce=os.urandom(32), timestamp=fixed_ts)
        keys.add(k)
        if (i + 1) % max(1, n // 20) == 0 or i == n - 1:
            progress(i + 1, n, "Keys")
    t2 = len(keys) == n
    results["test2_same_image_diff_nonce"] = {
        "passed": t2, "total": n, "unique": len(keys),
        "description": f"Same Image + {n} Different Nonces → All Unique",
    }
    print(f"    {'PASS ✓' if t2 else 'FAIL ✗'}  ({len(keys)}/{n} unique)")

    # ---- Test 3 ----
    n_img = config.get("phase1_diff_image_count", 10)
    print(f"  Test 3: {n_img} Different Images + Same Nonce")
    keys = set()
    for i in range(n_img):
        im = load_test_image(64, 64, seed=i * 7 + 1)
        k, _ = gen_key(im, nonce=fixed_nonce, timestamp=fixed_ts)
        keys.add(k)
        progress(i + 1, n_img, "Images")
    t3 = len(keys) == n_img
    results["test3_diff_images_same_nonce"] = {
        "passed": t3, "total": n_img, "unique": len(keys),
        "description": f"{n_img} Different Images + Same Nonce → All Unique",
    }
    print(f"    {'PASS ✓' if t3 else 'FAIL ✗'}  ({len(keys)}/{n_img} unique)")

    # ---- Test 4 ----
    n_mix = config.get("phase1_mixed_count", 100)
    print(f"  Test 4: {n_mix} Different Images + Different Nonces")
    keys = set()
    for i in range(n_mix):
        im = load_test_image(64, 64, seed=i + 200)
        k, _ = gen_key(im, nonce=os.urandom(32))
        keys.add(k)
        if (i + 1) % max(1, n_mix // 20) == 0 or i == n_mix - 1:
            progress(i + 1, n_mix, "Combos")
    t4 = len(keys) == n_mix
    results["test4_diff_images_diff_nonces"] = {
        "passed": t4, "total": n_mix, "unique": len(keys),
        "description": f"{n_mix} Diff Images + Diff Nonces → No Collisions",
    }
    print(f"    {'PASS ✓' if t4 else 'FAIL ✗'}  ({len(keys)}/{n_mix} unique)")

    results["all_passed"] = all(
        v.get("passed", True) for v in results.values() if isinstance(v, dict)
    )
    print(f"\n  Phase 1 overall: {'ALL PASSED ✓' if results['all_passed'] else 'FAILURES DETECTED ✗'}")
    return results
