"""Configuration: YAML file -> pydantic models, with dotted-key overrides from the CLI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from android_automation.coords import CoordinateSpace

CONFIG_ENV = "ANDROID_AUTOMATION_CONFIG"
ENV_PREFIX = "ANDROID_AUTOMATION__"
DEFAULT_CONFIG_PATH = Path("configs/default.yaml")

DEFAULT_APPS = {
	"x": "com.twitter.android",
	"twitter": "com.twitter.android",
	"youtube": "com.google.android.youtube",
	"whatsapp": "com.whatsapp",
	"instagram": "com.instagram.android",
	"telegram": "org.telegram.messenger",
	"chrome": "com.android.chrome",
	"gmail": "com.google.android.gm",
	"maps": "com.google.android.apps.maps",
	"google maps": "com.google.android.apps.maps",
	"play store": "com.android.vending",
	"settings": "com.android.settings",
}


class _Base(BaseModel):
	model_config = ConfigDict(extra="forbid", protected_namespaces=(), coerce_numbers_to_str=True)


class ImageConfig(_Base):
	"""Screenshots are resized Qwen-style before being sent: sides divisible by
	``factor`` and area within [min_pixels, max_pixels]."""

	factor: int = 32
	min_pixels: int = 64 * 32 * 32
	max_pixels: int = 1568 * 32 * 32
	format: Literal["PNG", "JPEG"] = "JPEG"


class ModelConfig(_Base):
	backend: Literal["openai", "transformers"] = "openai"
	model: str = "Hcompany/Holo-3.1-4B"
	# openai backend: any OpenAI-compatible /v1/chat/completions server
	base_url: str = "http://localhost:8000/v1"
	api_key_env: str = "VLM_API_KEY"
	timeout: float = 120.0
	max_retries: int = 2
	structured_output: Literal["json_schema", "json_object", "none"] = "json_schema"
	extra_body: dict[str, Any] = Field(default_factory=dict)
	# both backends
	temperature: float = 0.0
	max_tokens: int = 1024
	coordinate_space: CoordinateSpace = "normalized_1000"
	chat_template_kwargs: dict[str, Any] = Field(default_factory=dict)
	image: ImageConfig = Field(default_factory=ImageConfig)
	# transformers backend
	dtype: str = "bfloat16"
	device_map: str = "auto"

	def api_key(self) -> str:
		return os.environ.get(self.api_key_env, "") or "EMPTY"


class DeviceConfig(_Base):
	serial: str | None = None
	adb_path: str = "adb"
	text_input: Literal["auto", "input", "adbkeyboard"] = "auto"
	timeout: float = 30.0


class AgentConfig(_Base):
	max_steps: int = 30
	# Screenshots per prompt: 1 = current only, 2 = previous + current, ...
	history_images: int = Field(default=1, ge=1, le=5)
	# Past actions (with execution feedback) listed in the prompt.
	history_actions: int = 12
	max_parse_retries: int = 2
	# After each action: wait, then poll screenshots until the screen stops changing.
	settle_seconds: float = 1.0
	stable_timeout: float = 3.0
	# Fraction of the screen that must change for an action to count as having an effect.
	change_threshold: float = 0.001
	# Same action repeated this many times with no visible effect -> warn; twice that -> stop.
	stuck_threshold: int = 3
	record_dir: str | None = "runs"


class Config(_Base):
	model: ModelConfig = Field(default_factory=ModelConfig)
	# Optional second model that turns an element description into coordinates.
	# Lets a strong planner (any VLM) team up with a specialised grounding model.
	grounder: ModelConfig | None = None
	device: DeviceConfig = Field(default_factory=DeviceConfig)
	agent: AgentConfig = Field(default_factory=AgentConfig)
	apps: dict[str, str] = Field(default_factory=dict)

	def app_aliases(self) -> dict[str, str]:
		return {**DEFAULT_APPS, **{k.lower(): v for k, v in self.apps.items()}}


def _parse_value(raw: str) -> Any:
	return yaml.safe_load(raw) if raw != "" else ""


def set_dotted(data: dict[str, Any], key: str, value: Any) -> None:
	node = data
	parts = key.split(".")
	for part in parts[:-1]:
		nxt = node.get(part)
		if not isinstance(nxt, dict):
			nxt = {}
			node[part] = nxt
		node = nxt
	node[parts[-1]] = value


def load_config(
	path: str | Path | None = None,
	overrides: dict[str, Any] | None = None,
	sets: list[str] | None = None,
) -> Config:
	"""Load ``path`` (or $ANDROID_AUTOMATION_CONFIG, or ./configs/default.yaml when present),
	then apply, in increasing precedence: environment variables named
	``ANDROID_AUTOMATION__SECTION__KEY`` (e.g. ``ANDROID_AUTOMATION__MODEL__BASE_URL``),
	``overrides`` (dotted key -> value; None values are skipped) and ``sets`` (``key=value``
	strings). Environment and ``sets`` values are parsed as YAML."""
	if path is None:
		env = os.environ.get(CONFIG_ENV)
		path = Path(env) if env else (DEFAULT_CONFIG_PATH if DEFAULT_CONFIG_PATH.exists() else None)
	data: dict[str, Any] = {}
	if path is not None:
		loaded = yaml.safe_load(Path(path).read_text()) or {}
		if not isinstance(loaded, dict):
			raise ValueError(f"{path}: top level must be a mapping")
		data = loaded
	for name, raw in sorted(os.environ.items()):
		if name.startswith(ENV_PREFIX) and len(name) > len(ENV_PREFIX):
			key = ".".join(part.lower() for part in name[len(ENV_PREFIX) :].split("__"))
			set_dotted(data, key, _parse_value(raw))
	for k, v in (overrides or {}).items():
		if v is not None:
			set_dotted(data, k, v)
	for item in sets or []:
		if "=" not in item:
			raise ValueError(f"override {item!r} must look like key=value")
		k, v = item.split("=", 1)
		set_dotted(data, k.strip(), _parse_value(v.strip()))
	return Config.model_validate(data)
