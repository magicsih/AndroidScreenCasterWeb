# Contributing

Keep the example small and compatible with the released AndroidScreenCaster
TCP/H.264 stream. Describe the behavior you are changing, run the configuration
and browser checks from the README, and record tested environments separately
from assumptions. PRs should include receiver restart and late-viewer checks for
streaming changes. Do not add captured personal screens, secrets, or local `.env`
files. Use deterministic test video or an explicit test screen for screenshots.

Before upgrading MediaMTX, review its configuration and WHEP reader changes;
update the version, image digest, copied reader, license, and validation together.
Dependency availability alone is not proof of working browser playback.

For bugs, include OS/architecture, Docker/Compose versions, Android version and
encoder if known, app settings, browser/version, whether you use LAN or optional
ADB forwarding, and sanitized logs. Usage questions are welcome in Discussions.
