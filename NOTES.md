# Notes

## 2026-11-11 — Upstream sync and Python 3.13

The server sync incorporates upstream revision `ce06beb`. Runtime loading releases the allocator cache before making the runtime available. On Apple Silicon it uses the MPS allocator API. On other active accelerators it uses PyTorch's shared accelerator API. CPU-only loads skip cache release. The periodic post-synthesis release remains independent.

Verification used Python 3.13.15 on macOS arm64. A clean locked install confirmed that the Git dependency resolved to the published nonWatermark commit `0d742c1` and that `silentcipher` was absent. The server suite passed all 115 tests, including mocked allocator checks. Requests to `/v1/audio/speech` using Irodori-TTS v4.1-Small-MF returned 48 kHz mono WAV on both CPU and MPS model devices with the CPU codec. The MPS run confirmed cache release before synthesis. Docker Compose configuration and Linux x86-64 lock sync dry-runs passed for the CPU, cu128, and ROCm extras. Docker builds and Linux accelerator execution were unavailable on the test host.

## 2026-10-23 — Inference fork dependency

The inference dependency is `Shuichi346/Irodori-TTS-nonWatermark`. Its distribution name (`irodori-tts`) and Python namespace (`irodori_tts`) match upstream, so the server's imports and runtime integration require no changes. `Aratako/...` identifiers in `src/irodori_openai_tts/config.py` and `.env.example` identify Hugging Face model and codec assets, not the Git library source.

`uv.lock` pins the fork commit and is consumed by Docker's `uv sync --locked` steps. Changing only `pyproject.toml` would leave those builds inconsistent. Regeneration removed `silentcipher`, `blinker`, `flask`, `itsdangerous`, and `pyaml` without changing the versions of retained packages. uv 0.13.5 also updated the lockfile format and normalized dependency markers.

Migration verification passed: 109 tests, Ruff checks, bytecode compilation, and `uv lock --check --offline`. The installed distribution's Git origin and commit, required runtime symbols, absence of the `silentcipher` package, and absence of watermark references in the installed inference runtime were checked. Actual model synthesis and performance benchmarks were not run.
