"""Check local Markdown links, README examples and generated GIF assets."""

import json
from pathlib import Path
import re

from PIL import Image

from examples.tour import SCENES, execute_scene

ROOT = Path(__file__).resolve().parents[1]


def main():
    failures = []
    documents = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "CHANGELOG.md",
                 *sorted((ROOT / "docs").rglob("*.md"))]
    for document in documents:
        base = ROOT if document.name in ("readme_header.md", "readme_footer.md") else document.parent
        markdown = document.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", markdown):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0]
            if path and not (base / path).exists():
                failures.append(f"Broken link in {document.relative_to(ROOT)}: {target}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    outputs = json.loads((ROOT / "docs/results/demo_outputs.json").read_text(encoding="utf-8"))
    for scene in SCENES:
        assert f"docs/assets/{scene.slug}.gif" in readme
        execute_scene(scene)
        assert len(outputs[scene.slug]) == len(scene.steps)
        for output in outputs[scene.slug]:
            assert output in readme
        with Image.open(ROOT / f"docs/assets/{scene.slug}.gif") as animation:
            assert animation.n_frames == len(scene.steps) * 2
            assert animation.info.get("loop") == 0
            for index in range(animation.n_frames):
                animation.seek(index)
                animation.load()
                assert animation.info.get("duration", 0) > 0
                assert animation.size == (1440, 840)
        with Image.open(ROOT / f"docs/assets/{scene.slug}.png") as poster:
            poster.verify()
    for name in ("science", "ecb-cbc"):
        with Image.open(ROOT / f"docs/assets/{name}.png") as plot:
            plot.verify()
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Verified {len(documents)} Markdown files, 10 executable demos, 10 GIFs and 12 PNGs.")


if __name__ == "__main__":
    main()
