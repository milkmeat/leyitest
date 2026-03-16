"""Screenshot regression test runner.

Usage:
    python tests/test_screenshot.py                          # all games
    python tests/test_screenshot.py westgame2                # one game
    python tests/test_screenshot.py westgame2/popup_001      # one case
"""

import os
import sys
import glob
import time

# Add project root to path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tests.screenshot_helpers import build_pipeline, run_one_case


SCREENSHOTS_DIR = os.path.join(_PROJECT_ROOT, "tests", "screenshots")


def discover_cases(filter_arg: str | None = None) -> list[tuple[str, str, str]]:
    """Discover test cases: list of (game_id, png_path, yaml_path).

    filter_arg can be:
        None          — all games, all cases
        "westgame2"   — all cases for one game
        "westgame2/popup_001" — one specific case
    """
    cases = []

    if filter_arg and "/" in filter_arg:
        # Specific case: game_id/case_name
        game_id, case_name = filter_arg.split("/", 1)
        yaml_path = os.path.join(SCREENSHOTS_DIR, game_id, f"{case_name}.yaml")
        png_path = os.path.join(SCREENSHOTS_DIR, game_id, f"{case_name}.png")
        if os.path.isfile(yaml_path):
            cases.append((game_id, png_path, yaml_path))
        else:
            print(f"Case not found: {yaml_path}")
        return cases

    # Determine which game dirs to scan
    if filter_arg:
        game_dirs = [filter_arg]
    else:
        game_dirs = sorted(
            d for d in os.listdir(SCREENSHOTS_DIR)
            if os.path.isdir(os.path.join(SCREENSHOTS_DIR, d))
        ) if os.path.isdir(SCREENSHOTS_DIR) else []

    for game_id in game_dirs:
        game_dir = os.path.join(SCREENSHOTS_DIR, game_id)
        if not os.path.isdir(game_dir):
            continue
        yaml_files = sorted(glob.glob(os.path.join(game_dir, "*.yaml")))
        for yaml_path in yaml_files:
            base = os.path.splitext(yaml_path)[0]
            png_path = base + ".png"
            cases.append((game_id, png_path, yaml_path))

    return cases


def main():
    filter_arg = sys.argv[1] if len(sys.argv) > 1 else None

    cases = discover_cases(filter_arg)
    if not cases:
        print("No test cases found.")
        sys.exit(1)

    print(f"Found {len(cases)} test case(s)\n")

    passed = 0
    failed = 0
    results = []

    # Group by game_id to reuse pipeline
    current_game = None
    pipeline = None

    for game_id, png_path, yaml_path in cases:
        if game_id != current_game:
            current_game = game_id
            print(f"--- {game_id} ---")
            t0 = time.time()
            pipeline = build_pipeline(game_id)
            print(f"  Pipeline init: {time.time() - t0:.1f}s")

        case_name = os.path.splitext(os.path.basename(yaml_path))[0]
        t0 = time.time()
        result = run_one_case(pipeline, png_path, yaml_path)
        elapsed = time.time() - t0

        if result.passed:
            print(f"  PASS  {case_name} ({elapsed:.1f}s)")
            passed += 1
        else:
            print(f"  FAIL  {case_name} ({elapsed:.1f}s)")
            for err in result.errors:
                print(f"        {err}")
            failed += 1

        results.append(result)

    # Summary
    print(f"\n{'='*40}")
    print(f"Total: {passed + failed}  Passed: {passed}  Failed: {failed}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
