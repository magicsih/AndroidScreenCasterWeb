# Validation

Checked on 2026-10-03. Build/configuration checks, decoded synthetic video,
physical Android streaming, and transport/browser coverage are separate results.

## Environment and completed checks

- macOS ARM64 with Docker Engine 29.5.2 in Colima and Compose 5.6.0.
- Official MediaMTX 1.21.1 FFmpeg image (FFmpeg 8.1.2), NGINX 1.30.5.
- Google Chrome 154 headless, Playwright 1.63.0, in a session-owned browser tab.
- Android API 36 physical Seeker, public AndroidScreenCaster 0.2.0 debug APK,
  hardware `c2.mtk.avc.encoder`, 640×360 / 1 Mbps.
- Compose configuration, MediaMTX configuration validation and `nginx -t` passed.
- Synthetic TCP/H.264 → RTSP → WebRTC decoded changing frames. Late viewer,
  Reconnect button, full screen, sender EOF and a new sender without container
  restart passed. A 360 px wide layout had no horizontal overflow and its controls
  remained usable. No JavaScript page errors were recorded.
- Physical-device capture lasted 160 seconds; the browser reported 3,925 video
  frames and 13 dropped frames. Android Stop ended the session and the native
  instrumentation confirmed no capture/sender threads remained. Another viewer
  joined after the stream had started and decoded it.
- A second 160-second physical session at 1280×720 / 1 Mbps provided **27
  different decoded image samples over 136.26 seconds**, at approximately
  five-second intervals. Every sample reported Live. Late joining and manual
  reconnect passed during this run; the final sample after reconnect reported
  1,929 frames and zero dropped frames (this count is for that browser connection,
  not the total across the whole session). Android Stop again left no workers.
- [Linux x64 CI](https://github.com/magicsih/AndroidScreenCasterWeb/actions/runs/37113611419)
  passed with Playwright Chromium 153, including **UDP WebRTC** negotiation and
  automatic playback after the sender restarts. The page replaces a connection
  after five seconds without decoded frames, rather than waiting for a longer ICE
  timeout. Configuration checks and the complete synthetic test also passed
  locally after this fix.
- The final viewer code also passed a 35-second physical session including a
  return to the sender's static form. Six samples over twelve seconds stayed
  Live while its frame count increased from 104 to 117, and Stop left no workers.

See [recorded frame samples](qa/browser-samples.json) and
[snapshot measurements](qa/latency.json) for numeric evidence.

The physical test used the existing sender's deterministic MotionActivity test
screen; screenshots contain test content rather than unrelated apps.

## Recorded transport and coverage limits

The Mac's `rapportd` occupied TCP 49152. It was left running. The stack published
TCP input on 127.0.0.1:49153 for this check, with optional
`adb reverse tcp:49152 tcp:49153`. This verifies the unchanged APK and actual
browser decoder through the server; **direct Wi-Fi TCP input remains unverified
on this Mac**. The WebRTC connection selected its TCP candidate through Colima.
Direct LAN browser viewing remains unverified. UDP WebRTC was exercised on the
Linux CI runner; the Mac physical-device check selected TCP WebRTC.

Firefox and Safari, other devices/encoders, internet/NAT/TURN, VP8/IVF and legacy
UDP input are not established by these checks. The first version implements only
TCP/H.264 input. H.264 profiles with B-frames may not play in browsers; no automatic
transcoding is performed.

The bridge synthesizes timestamps at 30 fps because raw H.264 input does not
carry the Android per-frame presentation times. The result is not original
capture timing preservation. A particular latency is not guaranteed.

## Snapshot-based delay measurement

Eight pairs of source Android screenshots and decoded browser canvas snapshots
were requested concurrently during the 1280×720 physical session. OCR read the
same MotionActivity elapsed-millisecond clock on both images. The raw clock
differences were **249–331 ms, median 290 ms**. Correcting for each acquisition's
host-clock midpoint gives estimates of **77–164 ms, median 117 ms**, but each
pair's acquisition uncertainty was **179–193 ms**, before the source's 33 ms draw
cadence. Therefore this experiment **does not establish a precise end-to-end
latency value**.

This is a software-snapshot observation through optional ADB forwarding and
Colima/TCP WebRTC, not a camera-based glass-to-glass measurement or a direct
Wi-Fi benchmark. The clocks showed changing recent video throughout the sampled
run; these numbers are not a performance guarantee or advertised latency claim.

## Reproduce

Follow the README's isolated Linux browser test instructions. CI uses
`tools/browser_checks.py` with deterministic synthetic video and saves its JSON,
screenshots and Compose log as an artifact. Device validation requires a fresh
Android consent dialog for each session; do not reset app data or uninstall a
previously installed sender for testing.
