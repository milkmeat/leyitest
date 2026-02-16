"""Phase 2 Test Script - Verify vision pipeline: template matching, OCR, grid, scene classification."""

import sys
import os
import time

# Initialize logging first
from utils.logger import GameLogger
game_logger = GameLogger("logs")

import config
from device.adb_controller import ADBController
from vision.screenshot import ScreenshotManager
from vision.template_matcher import TemplateMatcher
from vision.ocr_locator import OCRLocator
from vision.grid_overlay import GridOverlay
from vision.element_detector import ElementDetector
from scene.classifier import SceneClassifier
from scene.popup_filter import PopupFilter


def test_template_matcher(screenshot):
    """Test 1: Template matching engine."""
    print("\n" + "=" * 50)
    print("Test 1: Template Matcher")
    print("=" * 50)

    matcher = TemplateMatcher(config.TEMPLATE_DIR, config.TEMPLATE_MATCH_THRESHOLD)
    templates = matcher.get_template_names()
    print(f"  Loaded templates: {len(templates)}")
    for name in templates:
        print(f"    - {name}")

    if templates:
        # Test match_all
        results = matcher.match_all(screenshot)
        print(f"  match_all results: {len(results)} matches")
        for r in results:
            print(f"    - {r.template_name}: confidence={r.confidence:.3f} at ({r.x}, {r.y})")

        # Test match_one with first template
        first = templates[0]
        result = matcher.match_one(screenshot, first)
        if result:
            print(f"  match_one('{first}'): confidence={result.confidence:.3f} "
                  f"at ({result.x}, {result.y}) bbox={result.bbox}")
        else:
            print(f"  match_one('{first}'): no match above threshold")
    else:
        print("  (No templates loaded - add PNGs to templates/ directory)")
        print("  Testing with empty template set: match_all returns empty list")
        results = matcher.match_all(screenshot)
        assert results == [], "match_all should return empty list with no templates"

    print("  PASSED")
    return matcher


def test_ocr(screenshot):
    """Test 2: OCR text detection."""
    print("\n" + "=" * 50)
    print("Test 2: OCR Locator")
    print("=" * 50)

    ocr = OCRLocator()
    print("  Initializing RapidOCR (first call may be slow)...")

    # Find all text
    results = ocr.find_all_text(screenshot)
    print(f"  Found {len(results)} text regions:")
    for r in results[:10]:  # Show first 10
        print(f"    '{r.text}' confidence={r.confidence:.3f} at {r.center} bbox={r.bbox}")
    if len(results) > 10:
        print(f"    ... and {len(results) - 10} more")

    # Test find_numbers_in_region (top portion where resource bar usually is)
    h, w = screenshot.shape[:2]
    top_region = (0, 0, w, h // 8)
    numbers = ocr.find_numbers_in_region(screenshot, top_region)
    print(f"  Numbers in top region: '{numbers}'")

    print("  PASSED")
    return ocr


def test_grid_overlay(screenshot):
    """Test 3: Grid overlay annotation."""
    print("\n" + "=" * 50)
    print("Test 3: Grid Overlay")
    print("=" * 50)

    grid = GridOverlay()
    print(f"  Grid: {grid.cols}x{grid.rows} cells")
    print(f"  Cell size: {grid.cell_width}x{grid.cell_height} pixels")

    # Test cell_to_pixel
    a1_pixel = grid.cell_to_pixel("A1")
    print(f"  A1 center: {a1_pixel}")
    h6_pixel = grid.cell_to_pixel("H6")
    print(f"  H6 center: {h6_pixel}")
    d3_pixel = grid.cell_to_pixel("D3")
    print(f"  D3 center: {d3_pixel}")

    # Test pixel_to_cell
    cell = grid.pixel_to_cell(d3_pixel[0], d3_pixel[1])
    print(f"  pixel_to_cell({d3_pixel[0]}, {d3_pixel[1]}) -> '{cell}'")
    assert cell == "D3", f"Expected D3, got {cell}"

    # Test get_cell_region
    region = grid.get_cell_region("B2")
    print(f"  B2 region: {region}")

    # Generate annotated image and save
    annotated = grid.annotate(screenshot)
    output_path = os.path.join("logs", "grid_overlay_test.png")
    import cv2
    cv2.imwrite(output_path, annotated)
    print(f"  Annotated image saved to: {output_path}")
    assert os.path.exists(output_path), "Annotated image not saved"

    print("  PASSED")
    return grid


def test_element_detector(screenshot, matcher, ocr, grid):
    """Test 4: Unified element detector."""
    print("\n" + "=" * 50)
    print("Test 4: Element Detector")
    print("=" * 50)

    detector = ElementDetector(matcher, ocr, grid)

    # Test locate_all
    elements = detector.locate_all(screenshot)
    print(f"  locate_all found {len(elements)} elements:")
    for e in elements[:10]:
        print(f"    [{e.source}] '{e.name}' confidence={e.confidence:.3f} at ({e.x}, {e.y})")
    if len(elements) > 10:
        print(f"    ... and {len(elements) - 10} more")

    # Test grid fallback
    grid_element = detector.locate(screenshot, "D3", methods=["grid"])
    if grid_element:
        print(f"  Grid locate 'D3': ({grid_element.x}, {grid_element.y})")
    assert grid_element is not None, "Grid fallback should always work"

    # Test locate with template (may or may not find something)
    templates = matcher.get_template_names()
    if templates:
        result = detector.locate(screenshot, templates[0])
        if result:
            print(f"  Template locate '{templates[0]}': ({result.x}, {result.y})")
        else:
            print(f"  Template locate '{templates[0]}': not found in this screenshot")

    print("  PASSED")
    return detector


def test_scene_classifier(screenshot, matcher):
    """Test 5: Scene classification."""
    print("\n" + "=" * 50)
    print("Test 5: Scene Classifier")
    print("=" * 50)

    classifier = SceneClassifier(matcher)

    # Classify current screenshot
    scene = classifier.classify(screenshot)
    print(f"  Current scene: {scene}")

    # Get confidence scores
    scores = classifier.get_confidence(screenshot)
    print(f"  Confidence scores:")
    for scene_name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        bar = "#" * int(score * 20)
        print(f"    {scene_name:12s}: {score:.3f} {bar}")

    print("  PASSED")
    return classifier


def test_popup_filter(screenshot, matcher, adb):
    """Test 6: Popup detection (detection only, no tap)."""
    print("\n" + "=" * 50)
    print("Test 6: Popup Filter")
    print("=" * 50)

    popup_filter = PopupFilter(matcher, adb)
    is_popup = popup_filter.is_popup(screenshot)
    print(f"  Current screen is popup: {is_popup}")

    if is_popup:
        print("  Popup detected! (Would close it in production)")
        print("  Skipping auto-close in test mode")
    else:
        print("  No popup detected on current screen")

    print("  PASSED")


def main():
    print("SLGrobot Phase 2 - Vision Test Suite")
    print(f"Target: {config.ADB_HOST}:{config.ADB_PORT}")
    print(f"Template dir: {config.TEMPLATE_DIR}")

    try:
        # Connect and capture screenshot
        print("\nConnecting to emulator...")
        adb = ADBController(config.ADB_HOST, config.ADB_PORT, config.NOX_ADB_PATH)
        if not adb.connect():
            print("Failed to connect to emulator!")
            sys.exit(1)

        mgr = ScreenshotManager(adb, config.SCREENSHOT_DIR)
        screenshot, filepath = mgr.capture_and_save("phase2_test")
        h, w = screenshot.shape[:2]
        print(f"Screenshot captured: {w}x{h} -> {filepath}")

        # Run all tests
        matcher = test_template_matcher(screenshot)
        ocr = test_ocr(screenshot)
        grid = test_grid_overlay(screenshot)
        test_element_detector(screenshot, matcher, ocr, grid)
        test_scene_classifier(screenshot, matcher)
        test_popup_filter(screenshot, matcher, adb)

        print("\n" + "=" * 50)
        print("ALL PHASE 2 TESTS PASSED")
        print("=" * 50)

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
