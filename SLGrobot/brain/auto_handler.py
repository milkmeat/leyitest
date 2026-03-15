"""Auto Handler - DOM-based priority rule engine for the auto loop.

Phase 3 rewrite: replaces template-matching approach with DOM-driven
priority rules. Each scene has an ordered list of rules; the first
matching rule produces the action.

Priority rules are defined per-game in ``game.json`` under
``auto_priorities``. Format::

    "auto_priorities": {
        "popup": [
            {"type": "button", "text_match": "领取|claim", "action": "tap"},
            {"type": "icon", "name": "buttons/close_x", "action": "tap"},
            {"action": "tap_blank"}
        ],
        "_default": [
            {"type": "finger", "action": "tap_fingertip"},
            {"action": "tap_blank"}
        ]
    }
"""

import logging
import re

from brain.script_runner import _flatten_elements, find_element

logger = logging.getLogger(__name__)


def match_priority(dom: dict, rules: list[dict]) -> dict | None:
    """Match first priority rule against DOM elements.

    Iterates rules in order. For each rule, searches DOM elements
    for a match. Returns the action dict for the first matching rule,
    or None if no rule matched.

    Returns:
        Action dict: {"type": "tap", "x": ..., "y": ..., "reason": ...}
        or None if no rule matched.
    """
    elements = _flatten_elements(dom)

    for rule in rules:
        rule_type = rule.get("type")

        # Unconditional fallback (no type specified)
        if rule_type is None:
            action_name = rule.get("action", "tap_blank")
            return _make_fallback_action(action_name, rule)

        # Type-based matching
        matched_elem = _match_rule_against_elements(rule, rule_type, elements)
        if matched_elem is not None:
            return _make_element_action(rule, rule_type, matched_elem)

    return None


def _match_rule_against_elements(
    rule: dict, rule_type: str, elements: list[dict]
) -> dict | None:
    """Find the first DOM element matching a priority rule.

    Returns the matching element dict, or None.
    """
    for elem in elements:
        if elem.get("type") != rule_type:
            continue

        # Type-specific attribute matching
        if rule_type == "button":
            text_match = rule.get("text_match")
            color_match = rule.get("color_match")
            if text_match:
                elem_text = elem.get("text", "")
                if not re.search(text_match, elem_text, re.IGNORECASE):
                    continue
            if color_match:
                elem_color = elem.get("color", "")
                if not re.search(color_match, elem_color, re.IGNORECASE):
                    continue

        elif rule_type == "text":
            value_match = rule.get("value_match")
            if value_match:
                elem_value = elem.get("value", "")
                if not re.search(value_match, elem_value, re.IGNORECASE):
                    continue

        elif rule_type == "icon":
            name = rule.get("name", "")
            elem_name = elem.get("name", "")
            if name != elem_name:
                continue

        # finger, red_dot, green_check — type-only match (no extra attrs)

        return elem

    return None


def _make_element_action(
    rule: dict, rule_type: str, elem: dict
) -> dict:
    """Create an action dict from a matched element."""
    action_name = rule.get("action", "tap")
    pos = elem.get("pos", [540, 960])

    if action_name == "tap_fingertip" and rule_type == "finger":
        # Use fingertip position if available
        fingertip = elem.get("fingertip")
        if fingertip:
            pos = fingertip

    x, y = pos[0], pos[1]
    reason = _build_reason(rule, elem)

    return {
        "type": "tap",
        "x": x,
        "y": y,
        "delay": 0.5,
        "reason": reason,
    }


def _make_fallback_action(action_name: str, rule: dict) -> dict:
    """Create an action dict for unconditional fallback rules."""
    if action_name == "tap_blank":
        return {
            "type": "tap",
            "x": 540,
            "y": 100,
            "delay": 0.5,
            "reason": "priority:tap_blank",
        }
    if action_name == "tap_center":
        return {
            "type": "tap",
            "x": 540,
            "y": 960,
            "delay": 0.5,
            "reason": "priority:tap_center",
        }
    if action_name == "wait":
        return {
            "type": "wait",
            "seconds": rule.get("seconds", 2),
            "reason": "priority:wait",
        }
    # Unknown fallback action — default to tap_blank
    return {
        "type": "tap",
        "x": 540,
        "y": 100,
        "delay": 0.5,
        "reason": f"priority:{action_name}",
    }


def _build_reason(rule: dict, elem: dict) -> str:
    """Build a human-readable reason string for logging."""
    rule_type = rule.get("type", "?")
    action = rule.get("action", "tap")

    if rule_type == "button":
        text = elem.get("text", "")
        return f"priority:{action}:button:{text}"
    if rule_type == "text":
        value = elem.get("value", "")
        return f"priority:{action}:text:{value}"
    if rule_type == "icon":
        name = elem.get("name", "")
        return f"priority:{action}:icon:{name}"
    if rule_type == "finger":
        return f"priority:{action}:finger"
    return f"priority:{action}:{rule_type}"


class AutoHandler:
    """DOM-based auto-handler using priority rules.

    Reads scene from DOM, looks up priority rules for that scene,
    and returns the first matching action.
    """

    def __init__(self, game_profile=None):
        self._priorities: dict[str, list[dict]] = {}
        if game_profile and game_profile.auto_priorities:
            self._priorities = game_profile.auto_priorities
        logger.info(
            f"AutoHandler initialized with {len(self._priorities)} "
            f"scene rule sets"
        )

    def get_action(self, dom: dict) -> dict | None:
        """Get best action for current DOM.

        1. Read scene from dom["screen"]["scene"]
        2. Look up scene in priorities, fall back to "_default"
        3. match_priority(dom, rules)
        4. Return action dict or None
        """
        scene = dom.get("screen", {}).get("scene", "unknown")

        # Look up rules for this scene
        rules = self._priorities.get(scene)
        if rules is None:
            rules = self._priorities.get("_default", [])

        if not rules:
            return None

        action = match_priority(dom, rules)
        if action:
            logger.info(
                f"AutoHandler [{scene}]: {action.get('reason', '?')} "
                f"-> ({action.get('x', '?')}, {action.get('y', '?')})"
            )
        else:
            logger.debug(f"AutoHandler [{scene}]: no rule matched")

        return action
