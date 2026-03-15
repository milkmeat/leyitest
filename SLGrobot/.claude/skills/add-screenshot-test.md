# Add Screenshot Test Case

This skill captures a screenshot from the running emulator and creates a regression test case for the screenshot unit testing framework.

TRIGGER when: user says "添加截屏测试", "add screenshot test", "截屏做测试用例", "从模拟器截屏生成回归测试", "capture a screenshot test case", or any similar request to create a screenshot-based test case from the emulator.

## Workflow

1. Capture a screenshot from the emulator:
   ```bash
   python main.py screenshot test_capture
   ```

2. Run the YAML generator on the captured screenshot to get a draft expected output:
   ```bash
   python tests/generate_expected.py data/test_capture.png --game <ACTIVE_GAME>
   ```
   (Check `config.py` for `ACTIVE_GAME` value, or use the game the user specifies.)

3. Show the generated scene, elements, and action to the user. Ask if the output looks correct and if any adjustments are needed.

4. Ask the user for a test case name, or auto-generate one as `<scene>_<NNN>` where NNN is the next available number for that scene type in the game's screenshot directory.

5. Copy the PNG to the test directory:
   ```bash
   cp data/test_capture.png tests/screenshots/<game_id>/<name>.png
   ```

6. Save the (possibly edited) YAML:
   Write the YAML content to `tests/screenshots/<game_id>/<name>.yaml`

7. Run the new test case to verify it passes:
   ```bash
   python tests/test_screenshot.py <game_id>/<name>
   ```

8. Run full regression to ensure nothing else broke:
   ```bash
   python tests/test_screenshot.py
   ```

Report results to the user.
