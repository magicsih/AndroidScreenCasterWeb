# Third-party notices

`web/vendor/reader.js` is copied without modifications from
[MediaMTX v1.21.1](https://github.com/bluenviron/mediamtx/blob/v1.21.1/internal/servers/webrtc/reader.js).
Its MIT license is retained in `web/vendor/LICENSE.mediamtx`.

The stack uses the official MediaMTX `1.21.1-ffmpeg` and NGINX `1.30.5-alpine`
container images, pinned to their multi-platform manifest digests. MediaMTX is
MIT licensed. NGINX uses a BSD-style license. The FFmpeg build in the MediaMTX
image enables GPL components; FFmpeg and its bundled libraries retain their own
licenses in that image. This repository does not relabel those programs under
its project license.

- [MediaMTX source and license](https://github.com/bluenviron/mediamtx/tree/v1.21.1)
- [MediaMTX FFmpeg image recipe](https://github.com/bluenviron/mediamtx/blob/v1.21.1/docker/ffmpeg.Dockerfile)
- [NGINX official images](https://github.com/nginx/docker-nginx)
- [FFmpeg legal information](https://ffmpeg.org/legal.html)
