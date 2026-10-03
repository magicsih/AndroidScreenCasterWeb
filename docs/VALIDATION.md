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

The physical test used the existing sender's deterministic MotionActivity test
screen; screenshots contain test content rather than unrelated apps.

## Recorded transport and coverage limits

The Mac's `rapportd` occupied TCP 49152. It was left running. The stack published
TCP input on 127.0.0.1:49153 for this check, with optional
`adb reverse tcp:49152 tcp:49153`. This verifies the unchanged APK and actual
browser decoder through the server; **direct Wi-Fi TCP input remains unverified
on this Mac**. The WebRTC connection selected its TCP candidate through Colima.
Direct LAN viewing and the UDP WebRTC candidate are separate coverage items.

Firefox and Safari, other devices/encoders, internet/NAT/TURN, VP8/IVF and legacy
UDP input are not established by these checks. The first version implements only
TCP/H.264 input. H.264 profiles with B-frames may not play in browsers; no automatic
transcoding is performed.

The bridge synthesizes timestamps at 30 fps because raw H.264 input does not
carry the Android per-frame presentation times. The result is not original
capture timing preservation. A particular latency is not guaranteed.

Further physical frame sampling and snapshot-based delay measurement are being
recorded before the initial implementation is merged.

## Reproduce

Follow the README's isolated Linux browser test instructions. CI uses
`tools/browser_checks.py` with deterministic synthetic video and saves its JSON,
screenshots and Compose log as an artifact. Device validation requires a fresh
Android consent dialog for each session; do not reset app data or uninstall a
previously installed sender for testing.
