# AGENTS.md

Repository-specific maintenance instructions for this server fork.

- Use `Shuichi346/Irodori-TTS-nonWatermark` as the `irodori-tts` Git dependency in `pyproject.toml`; preserve the fork's removal of audio watermark processing.
- Regenerate `uv.lock` after changing dependency declarations and verify it with `uv lock --check`. Docker builds install dependencies with `uv sync --locked`.
- Keep the `irodori_tts` import namespace. The Hugging Face model and codec repository identifiers are separate from the Git dependency and must not be renamed merely to match this fork.
- See `NOTES.md` for the migration rationale and verification limits.
