"""Real-browser checks and screenshots for the local lab.

Install ``.[ui-test]`` and run ``python -m playwright install chromium`` once.
Start the lab, then run ``python -m scripts.check_lab_ui``.
No browser tooling is required to run the application itself.
"""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "output" / "playwright"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--publish-assets", action="store_true", help="update the README screenshots and UI GIF")
    args = parser.parse_args()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    errors, frames = [], []
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1150}, reduced_motion="reduce")
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
        page.goto(args.url)
        page.wait_for_load_state("networkidle")
        expect(page.locator("#result-state")).to_have_text("Result calculated")
        expect(page.locator(".bit")).to_have_count(256)
        original = hashlib.sha256(b"Hello").digest()
        flipped = hashlib.sha256(bytes([ord("H") ^ 128]) + b"ello").digest()
        expected_difference = sum((a ^ b).bit_count() for a, b in zip(original, flipped))
        expect(page.locator(".bit.diff")).to_have_count(expected_difference)
        assert page.locator("html").get_attribute("lang") == "en"
        page.screenshot(path=str(ARTIFACTS / "lab-desktop.png"), full_page=True)

        def capture(name):
            path = ARTIFACTS / f"lab-{name}.png"
            page.screenshot(path=str(path))
            frames.append(path)

        def calculate():
            page.locator("#run").click()
            expect(page.locator("#result-state")).to_have_text("Result calculated", timeout=15000)

        def station(key):
            page.locator(f'a[href="#{key}"][data-station]').click()
            expect(page.locator(f'a[data-station="{key}"]')).to_have_attribute("aria-current", "page")
            calculate()

        capture("hash")
        # Changing inputs must invalidate exports; equal inputs produce no difference.
        page.get_by_label("Modification", exact=True).select_option("text")
        expect(page.locator("#export")).to_be_disabled()
        page.get_by_label("Comparison text", exact=True).fill("Hello")
        calculate()
        expect(page.locator(".bit.diff")).to_have_count(0)
        with page.expect_download() as download:
            page.locator("#export").click()
        download.value.save_as(str(ARTIFACTS / "export.json"))
        exported = json.loads((ARTIFACTS / "export.json").read_text(encoding="utf-8"))
        assert exported["result"]["difference"] == 0

        # HTML input is rendered as data, never as an element.
        hostile = '<img src=x onerror="window.injected=true">'
        station("rsa")
        page.get_by_label("Text to encrypt", exact=True).fill(hostile)
        calculate()
        assert page.locator("#result img").count() == 0
        expect(page.locator(".success-banner")).to_contain_text(hostile)

        station("math")
        expect(page.locator(".equation")).to_contain_text("240 × (-9) + 46 × (47) = 2")
        station("dh")
        expect(page.locator(".success-banner")).to_contain_text("Matching shared secret: 2")
        capture("dh")
        station("aes")
        expect(page.locator("#field-key")).not_to_have_value("")
        page.get_by_label("Operation", exact=True).select_option("decrypt")
        calculate()
        expect(page.locator(".success-banner")).to_contain_text("Valid tag")
        tag = page.locator("#field-tag").input_value()
        page.locator("#field-tag").fill(("0" if tag[0] != "0" else "1") + tag[1:])
        calculate()
        expect(page.locator(".failure-banner")).to_contain_text("Authentication rejected")
        capture("aes-refusal")
        station("authentication")
        expect(page.locator(".failure")).to_have_count(2)
        station("channel")
        expect(page.locator(".timeline")).to_contain_text("Rejected: this sequence")
        capture("channel")
        station("experiments")
        expect(page.locator(".cipher-block")).to_have_count(26)
        capture("modes")
        page.get_by_label("Experiment", exact=True).select_option("attacks")
        calculate()
        expect(page.locator("#result")).to_contain_text("Key 173")
        page.get_by_label("Experiment", exact=True).select_option("benchmark")
        calculate()
        expect(page.locator("tbody tr")).to_have_count(11)

        station("hash")
        page.get_by_label("Modification", exact=True).select_option("bit")
        page.get_by_label("Bit to flip", exact=True).fill("999")
        page.locator("#run").click()
        expect(page.locator("#error")).to_be_visible()
        expect(page.locator("#field-bit")).to_be_focused()
        expect(page.locator("#export")).to_be_disabled()
        page.locator("#reset").click()
        expect(page.locator("#result-state")).to_have_text("Result calculated")

        # The skip link must move focus without changing the selected workspace.
        station("dh")
        page.keyboard.press("Control+Home")
        page.locator(".skip-link").focus()
        page.keyboard.press("Enter")
        expect(page.locator("#workspace")).to_be_focused()
        expect(page.locator("#title")).to_have_text("A secret that never travels.")

        # Long values, each workspace, and 320px reflow without horizontal page overflow.
        for width in (320, 390, 768, 1440):
            page.set_viewport_size({"width": width, "height": 900})
            for key in ("hash", "math", "rsa", "dh", "aes", "authentication", "channel", "experiments"):
                station(key)
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (width, key)
            if width == 390:
                station("hash")
                page.locator("#reset").click()
                expect(page.locator("#result-state")).to_have_text("Result calculated")
                page.screenshot(path=str(ARTIFACTS / "lab-mobile.png"), full_page=True)
        # Deep links survive a reload.
        page.goto(args.url + "/#aes")
        page.wait_for_load_state("networkidle")
        expect(page.locator("#title")).to_have_text("A secret, with its seal.")
        # Offline errors explain how to restart the application.
        page.route("**/api/run", lambda route: route.abort())
        page.locator("#run").click()
        expect(page.locator("#error")).to_contain_text("Restart python -m crypto.lab")
        # Exactly one validation refusal and one deliberately aborted request
        # produce expected resource errors; other console failures still fail QA.
        refusals = [error for error in errors if "status of 400 (Bad Request)" in error]
        aborted = [error for error in errors if "ERR_FAILED" in error]
        assert len(refusals) == 1 and len(aborted) == 1, errors
        errors = [error for error in errors if error not in refusals + aborted]
        browser.close()

    if errors:
        raise AssertionError("Browser errors: " + "\n".join(errors))
    if args.publish_assets:
        assets = ROOT / "docs" / "assets"
        (assets / "lab.png").write_bytes((ARTIFACTS / "lab-desktop.png").read_bytes())
        (assets / "lab-mobile.png").write_bytes((ARTIFACTS / "lab-mobile.png").read_bytes())
        images = []
        for path in frames:
            with Image.open(path) as image:
                images.append(image.convert("RGB").copy())
        images[0].save(assets / "lab.gif", save_all=True, append_images=images[1:],
                       duration=2800, loop=0, optimize=True)
    print("Verified 8 workspaces, all 3 experiments, GCM refusal, JSON export, input errors,")
    print("HTML escaping, keyboard skip link, deep links, offline feedback and 4 responsive widths.")


if __name__ == "__main__":
    main()
