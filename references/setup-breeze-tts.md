---
title: Working Breeze TTS 2 setup on Apple Silicon
verified: 2026-09-11
scope: research-non-commercial
---

# Breeze TTS 2: setup and cache repair

Use the existing Swift runtime first. No Python environment or package upgrade required for this route. Check paths before running; a recorded installation is not proof that it still exists.

## Tested configuration

- Source: [Blaizzy/mlx-audio-swift](https://github.com/Blaizzy/mlx-audio-swift/tree/bf14ae0c26e4e85553dd989571cae29d70fa6735), revision `bf14ae0c26e4e85553dd989571cae29d70fa6735`.
- Model: `mlx-community/Breeze-TTS-2-mlx-4bit`; snapshot `3a06d26b172ea4ae1da2f42d708383e9c79d5526`. Retain the upstream quantisation; do not requantise.
- Build: Xcode 26.6 (17F113), separate Metal Toolchain 17F109; release arm64. These are tested versions, not asserted minimums.
- Resolved dependencies: mlx-swift 0.31.4, swift-huggingface 0.8.1, swift-transformers 1.1.9. Preserve the source's `Package.resolved` when reproducing.
- Installed executable: `~/.local/share/mlx-audio-swift/bf14ae0c/mlx-audio-swift-tts`.
- Configured Mac cache root: `~/local-models`; Swift model directory: `mlx-audio/mlx-community_Breeze-TTS-2-mlx-4bit` beneath that root. On another machine, locate its existing cache instead of creating a second one.

## Run from the installed runtime

```sh
breeze_runtime="$HOME/.local/share/mlx-audio-swift/bf14ae0c"
breeze_cache="$HOME/local-models"
test -x "$breeze_runtime/mlx-audio-swift-tts"
test -s "$breeze_cache/mlx-audio/mlx-community_Breeze-TTS-2-mlx-4bit/config.json"
test -s "$breeze_cache/mlx-audio/mlx-community_Breeze-TTS-2-mlx-4bit/model.safetensors"
"$breeze_runtime/mlx-audio-swift-tts" --help
```

If any check fails, stop and resolve that prerequisite; do not continue blindly into a model load. Before first use, also verify the complete tokenizer/nested cache structure described below and the five runtime resource bundles listed under fresh builds.

```sh
breeze_output_dir=$(mktemp -d /private/tmp/breeze-narration.XXXXXX)
HF_HUB_CACHE="$breeze_cache" \
  "$breeze_runtime/mlx-audio-swift-tts" \
  --model mlx-community/Breeze-TTS-2-mlx-4bit \
  --text 'The new speech model is running locally. This is a short test of clear English narration.' \
  --voice 'A clear and calm English narrator with a natural British accent.' \
  --max_tokens 256 --benchmark --output "$breeze_output_dir/narration.wav"
```

For the longer audition passage, use `--max_tokens 640`. These are output caps, not promised durations. Inspect the ending before increasing a cap or joining clips.

The successful run logs `Using cached model at: ...`. Stop an unexpected `Downloading model ...` process before a multi-GB transfer. The CLI may buffer redirected output; do not infer cache use from silence.

## Repair the Swift cache without redownloading

The pinned runtime expects ordinary files under `<HF_HUB_CACHE>/mlx-audio/<owner>_<repo>`. It rejected a directory link to the Python HF snapshot as incomplete and attempted a new download. Its repair code can clear the rejected Swift directory and associated Hub cache: do not experiment against the only copy of model files.

`HF_HUB_OFFLINE=1` did **not** prevent that download attempt. It is not a network-isolation guarantee for this Swift path. If the request strictly prohibits any network transfer, require enforced network isolation before running; cache preflight and log watching alone cannot guarantee that boundary.

1. Stop the exact failed generation process. Preserve the original `models--mlx-community--Breeze-TTS-2-mlx-4bit/blobs` and snapshot directories.
2. Inspect the failed Swift destination. If it exists, move only that exact destination aside to a distinct `retired-...` backup after confirming its identity; do not merge, overwrite or recursively remove it.
3. Use the already verified snapshot. On macOS/APFS, `cp -cRL` resolves its symlinks and uses copy-on-write cloning. Do not fall back silently to a full copy on another filesystem; check space first.

Run the clone only when the destination is absent, including absence of a dangling symlink:

```sh
breeze_snapshot="$breeze_cache/models--mlx-community--Breeze-TTS-2-mlx-4bit/snapshots/3a06d26b172ea4ae1da2f42d708383e9c79d5526"
breeze_model="$breeze_cache/mlx-audio/mlx-community_Breeze-TTS-2-mlx-4bit"
if test -s "$breeze_snapshot/model.safetensors" && \
   test -s "$breeze_snapshot/config.json" && \
   test -d "$breeze_snapshot/audio_tokenizer" && \
   ! test -e "$breeze_model" && ! test -L "$breeze_model"; then
  mkdir -p "$breeze_cache/mlx-audio"
  cp -cRL "$breeze_snapshot" "$breeze_model"
else
  echo 'Stop: inspect the source snapshot and existing Swift destination.'
fi
```

Check regular, nonempty root weights; valid JSON; tokenizer files; and all nested `audio_tokenizer` files. Compare resolved source/destination file hashes before first use. Keep the complete snapshot structure, not just `model.safetensors`.

If weights are genuinely absent and downloading is authorised:

```sh
hf download mlx-community/Breeze-TTS-2-mlx-4bit \
  --revision 3a06d26b172ea4ae1da2f42d708383e9c79d5526 \
  --cache-dir "$breeze_cache"
```

Then verify the snapshot before preparing the Swift layout. The Swift API also exposes `BreezeTTSModel.fromModelDirectory(URL)`; the tested CLI uses a repo ID and the cache layout above, not a local-path `--model` argument.

## Fresh build only when needed

Full **Xcode**, not Apple Developer.app or Command Line Tools alone:

```sh
xcode-select -p
xcodebuild -version
xcodebuild -checkFirstLaunchStatus
xcrun metal --version
```

If Metal is missing, the relevant setup step is `xcodebuild -downloadComponent MetalToolchain`. Obtain authority for installing missing software or changing the global developer directory; do not accept licence agreements silently.

Use a checkout of the pinned upstream source, read its `AGENTS.md`, retain `Package.resolved`, and choose a fresh build directory:

```sh
breeze_build=$(mktemp -d /private/tmp/breeze-swift-build.XXXXXX)
# Run inside the pinned mlx-audio-swift checkout.
xcodebuild -scheme mlx-audio-swift-tts -configuration Release \
  -destination 'platform=macOS,arch=arm64' \
  -derivedDataPath "$breeze_build" build
```

Require `BUILD SUCCEEDED`; `swift build` alone is not the tested route for producing/bundling Metal resources. Preserve `Build/Products/Release/mlx-audio-swift-tts` with these sibling resource bundles in a new, versioned runtime directory:

- `mlx-swift_Cmlx.bundle`
- `swift-transformers_Hub.bundle`
- `swift-crypto_Crypto.bundle`
- `swift-nio-ssl_NIOSSL.bundle`
- `swift-nio_NIOPosix.bundle`

Do not replace an existing runtime in place. Test `--help` **and actual synthesis** from the preserved location; help does not exercise Metal/model loading. Missing metallib errors require checking these resources before rebuilding or downloading weights.

## Verify and report

- Validate a nonempty, finite, non-silent 24 kHz mono WAV. Transcribe/listen and check the ending against the input.
- Use [voice presets](voice-presets-breeze-tts.md) as descriptions, not guaranteed accents or stable speaker IDs. Generic `language` does not change Breeze's prompt; put the language in `--voice`.
- The tested Swift streaming API yields the final waveform as one audio event. Do not describe it as low-latency playable streaming.
- Keep model/runtime/build versions and voice/text with the output. Separate speech success from subjective voice quality and throughput claims.
- September 2026 M4 Max 128 GB observations: 7.68 s audio in 12.43 s generation; a new-process repeat, 7.76 s in 11.45 s. Not warm-process or sustained benchmarks; not promises for other hosts.
- 13 October 2026 smoke check: installed runtime loaded the existing Swift cache and generated a 4.16 s mono 24 kHz WAV in 12.70 s, using the Quiet Observer description and a short test sentence. This reconfirms cache loading and synthesis, not an independent voice-quality assessment.
- Research/non-commercial weights **and self-hosted outputs**; Qwen remains the default. No commercial-use inference from the Swift source licence.
