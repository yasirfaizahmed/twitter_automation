"""Per-run trajectory recording: screenshots, annotated actions, raw model output and
execution results. The JSONL + PNG layout doubles as a fine-tuning dataset."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image


def _field(label: str, value: str | None) -> str:
	return f"<p><b>{label}</b> {html.escape(value)}</p>" if value else ""


def _slug(text: str, limit: int = 40) -> str:
	return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:limit] or "run"


class Recorder:
	def __init__(self, root: str | Path, goal: str, meta: dict[str, Any] | None = None):
		stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
		self.dir = Path(root) / f"{stamp}_{_slug(goal)}"
		self.dir.mkdir(parents=True, exist_ok=True)
		self.goal = goal
		self._rows: list[dict[str, Any]] = []
		(self.dir / "meta.json").write_text(
			json.dumps({"goal": goal, "started_at": stamp, **(meta or {})}, indent=2, default=str)
		)

	def step(
		self,
		index: int,
		screenshot: Image.Image,
		annotated: Image.Image | None,
		record: dict[str, Any],
	) -> None:
		shot_name = f"step_{index:03d}.png"
		screenshot.save(self.dir / shot_name)
		row = {"index": index, "screenshot": shot_name, **record}
		if annotated is not None:
			ann_name = f"step_{index:03d}_action.png"
			annotated.save(self.dir / ann_name)
			row["annotated"] = ann_name
		self._rows.append(row)
		with (self.dir / "steps.jsonl").open("a") as f:
			f.write(json.dumps(row, default=str) + "\n")

	def finish(self, result: dict[str, Any], final_screenshot: Image.Image | None = None) -> None:
		if final_screenshot is not None:
			final_screenshot.save(self.dir / "final.png")
		(self.dir / "result.json").write_text(json.dumps(result, indent=2, default=str))
		(self.dir / "report.html").write_text(self._html(result, final_screenshot is not None))

	def _html(self, result: dict[str, Any], has_final: bool) -> str:
		esc = html.escape
		cards = []
		for row in self._rows:
			img = row.get("annotated", row["screenshot"])
			step = row.get("step") or {}
			plan = "".join(f"<li>{esc(p)}</li>" for p in step.get("plan", []))
			cards.append(
				f"""<section><img src="{esc(img)}" loading="lazy"><div>
<h2>Step {row["index"] + 1}</h2>
{_field("Observation", step.get("observation"))}{_field("Thought", step.get("thought"))}
{f"<ol>{plan}</ol>" if plan else ""}{_field("Note", step.get("note"))}
<p><b>Action</b> <code>{esc(row.get("action", ""))}</code></p>
<p><b>Result</b> {esc(row.get("feedback", ""))}</p>
<details><summary>raw model output</summary><pre>{esc(row.get("raw", ""))}</pre></details>
</div></section>"""
			)
		final = (
			'<section><img src="final.png"><div><h2>Final screen</h2></div></section>'
			if has_final
			else ""
		)
		return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Run report</title><style>
:root{{color-scheme:light dark;--bg:#fafafa;--fg:#1a1a1a;--card:#fff;--line:#ddd}}
@media (prefers-color-scheme:dark){{:root{{--bg:#121212;--fg:#eee;--card:#1e1e1e;--line:#333}}}}
body{{font:15px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg);margin:0 auto;max-width:1000px;padding:16px}}
section{{display:flex;gap:16px;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0}}
img{{width:240px;height:auto;border-radius:4px;flex:none}} pre{{white-space:pre-wrap;font-size:12px}}
@media (max-width:600px){{section{{flex-direction:column}} img{{width:100%}}}}
</style></head><body>
<h1>{esc(self.goal)}</h1>
<p><b>Status</b> {esc(str(result.get("status")))} &middot; <b>Steps</b> {esc(str(result.get("steps")))}
&middot; {esc(str(result.get("answer") or result.get("reason") or ""))}</p>
{"".join(cards)}{final}
</body></html>"""
