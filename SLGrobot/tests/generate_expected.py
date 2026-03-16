"""Generate draft expected YAML for a screenshot test case.

Usage:
    python tests/generate_expected.py <png_path> [--game westgame2]

Runs the full DOM pipeline on the screenshot and outputs a draft YAML
to stdout for review and editing.
"""

import os
import re
import sys

# Add project root to path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import cv2
import yaml

from tests.screenshot_helpers import build_pipeline
from brain.script_runner import _flatten_elements


def escape_regex(s: str) -> str:
    """Escape special regex chars for use in a match pattern."""
    return re.escape(s)


def generate_expected(png_path: str, game_id: str) -> dict:
    """Run pipeline on screenshot and build draft expected dict."""
    pipeline = build_pipeline(game_id)
    ocr = pipeline["ocr"]
    dom_builder = pipeline["dom_builder"]
    auto_handler = pipeline["auto_handler"]

    screenshot = cv2.imread(png_path)
    if screenshot is None:
        print(f"Error: cannot load {png_path}", file=sys.stderr)
        sys.exit(1)

    ocr.set_frame(screenshot)
    dom = dom_builder.build(screenshot)

    scene = dom.get("screen", {}).get("scene", "unknown")
    elements = _flatten_elements(dom)

    # Build required_elements from detected icons and buttons
    required = []
    for elem in elements:
        etype = elem.get("type")
        if etype == "icon":
            required.append({
                "type": "icon",
                "name": elem["name"],
            })
        elif etype == "button":
            text = elem.get("text", "")
            entry = {"type": "button"}
            if text:
                entry["text_match"] = escape_regex(text)
            required.append(entry)
        elif etype == "red_dot":
            required.append({"type": "red_dot"})
        elif etype == "finger":
            required.append({"type": "finger"})

    # Build auto_action
    action = auto_handler.get_action(dom)
    if action is None:
        auto_action = None
    else:
        auto_action = {"type": action.get("type", "tap")}
        reason = action.get("reason", "")
        if reason:
            auto_action["reason_match"] = escape_regex(reason)

    result = {"scene": scene}
    if required:
        result["required_elements"] = required
    if auto_action is not None:
        result["auto_action"] = auto_action
    else:
        result["auto_action"] = None

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python tests/generate_expected.py <png_path> [--game <game_id>]")
        sys.exit(1)

    png_path = sys.argv[1]

    # Parse --game flag
    game_id = "westgame2"  # default
    if "--game" in sys.argv:
        idx = sys.argv.index("--game")
        if idx + 1 < len(sys.argv):
            game_id = sys.argv[idx + 1]

    if not os.path.isfile(png_path):
        print(f"Error: file not found: {png_path}", file=sys.stderr)
        sys.exit(1)

    expected = generate_expected(png_path, game_id)

    # Output YAML
    yaml_str = yaml.dump(
        expected,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    print(yaml_str)


if __name__ == "__main__":
    main()
