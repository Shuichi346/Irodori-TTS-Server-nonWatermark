from __future__ import annotations

import threading
from types import SimpleNamespace

import pytest
import torch

from irodori_openai_tts import runtime as runtime_module
from irodori_openai_tts.config import Settings
from irodori_openai_tts.runtime import RuntimeLoadTimeoutError, RuntimeManager


def test_sampling_steps_default_to_model_default(monkeypatch):
    monkeypatch.delenv("IRODORI_DEFAULT_NUM_STEPS", raising=False)

    assert Settings(_env_file=None).default_num_steps is None


@pytest.mark.parametrize("steps", [4, 40])
def test_sampling_steps_environment_override(monkeypatch, steps):
    monkeypatch.setenv("IRODORI_DEFAULT_NUM_STEPS", str(steps))

    assert Settings(_env_file=None).default_num_steps == steps


def test_runtime_load_timeout_while_another_thread_is_loading(tmp_path, monkeypatch):
    checkpoint = tmp_path / "model.safetensors"
    checkpoint.write_bytes(b"test")
    settings = Settings(
        checkpoint=str(checkpoint),
        model_device="cpu",
        codec_device="cpu",
        model_load_timeout=0.05,
        _env_file=None,
    )
    manager = RuntimeManager(settings)
    started = threading.Event()
    release = threading.Event()
    loaded_runtime = object()
    errors: list[BaseException] = []

    def fake_from_key(_key):
        started.set()
        release.wait(timeout=2)
        return loaded_runtime

    monkeypatch.setattr(
        runtime_module.InferenceRuntime,
        "from_key",
        staticmethod(fake_from_key),
    )

    def load_runtime():
        try:
            assert manager.get() is loaded_runtime
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    thread = threading.Thread(target=load_runtime)
    thread.start()
    assert started.wait(timeout=1)

    with pytest.raises(RuntimeLoadTimeoutError):
        manager.get()

    release.set()
    thread.join(timeout=2)
    assert errors == []
    assert manager.is_loaded
    assert not manager.is_loading


def test_runtime_resolves_local_checkpoint_path(tmp_path):
    checkpoint = tmp_path / "model.safetensors"
    checkpoint.write_bytes(b"test")
    manager = RuntimeManager(Settings(checkpoint=str(checkpoint), _env_file=None))

    assert manager._resolve_checkpoint_path() == str(checkpoint)


def test_runtime_rejects_missing_local_checkpoint(tmp_path):
    manager = RuntimeManager(
        Settings(checkpoint=str(tmp_path / "missing.safetensors"), _env_file=None)
    )

    with pytest.raises(FileNotFoundError, match="Checkpoint not found"):
        manager._resolve_checkpoint_path()


def test_runtime_downloads_hf_checkpoint_when_local_checkpoint_is_unset(monkeypatch):
    manager = RuntimeManager(Settings(hf_checkpoint="owner/repo", _env_file=None))

    def fake_download(repo_id):
        assert repo_id == "owner/repo"
        return "/cache/model.safetensors"

    monkeypatch.setattr(runtime_module, "download_hf_checkpoint", fake_download)

    assert manager._resolve_checkpoint_path() == "/cache/model.safetensors"


@pytest.mark.parametrize(
    ("accelerator_type", "model_device", "codec_device", "expected_cache"),
    [
        (None, "cpu", "cpu", None),
        ("mps", "cpu", "cpu", None),
        ("mps", "mps", "cpu", "mps"),
        ("mps", "cpu", "mps", "mps"),
        ("mps", "mps", "mps", "mps"),
        ("xpu", "xpu:0", "xpu:1", "accelerator"),
    ],
)
def test_runtime_releases_loading_cache_before_serving(
    tmp_path, monkeypatch, accelerator_type, model_device, codec_device, expected_cache
):
    checkpoint = tmp_path / "model.safetensors"
    checkpoint.write_bytes(b"test")
    manager = RuntimeManager(Settings(checkpoint=str(checkpoint), _env_file=None))
    loaded = SimpleNamespace(
        model_device=torch.device(model_device), codec_device=torch.device(codec_device)
    )
    events = []

    def load(_key):
        events.append("loaded")
        return loaded

    def release(cache):
        assert not manager.is_loaded
        events.append(cache)

    monkeypatch.setattr(runtime_module.InferenceRuntime, "from_key", staticmethod(load))
    monkeypatch.setattr(
        torch.accelerator,
        "current_accelerator",
        lambda *, check_available: torch.device(accelerator_type) if accelerator_type else None,
    )
    monkeypatch.setattr(torch.mps, "empty_cache", lambda: release("mps"))
    monkeypatch.setattr(torch.accelerator, "empty_cache", lambda: release("accelerator"))

    assert manager.get() is loaded
    assert manager.is_loaded
    assert manager.get() is loaded
    expected = ["loaded"] if expected_cache is None else ["loaded", expected_cache]
    assert events == expected
