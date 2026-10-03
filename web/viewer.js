"use strict";

const video = document.querySelector("#video");
const status = document.querySelector("#status");
const placeholder = document.querySelector("#placeholder");
const message = document.querySelector("#message");
const fullscreen = document.querySelector("#fullscreen");
let reader = null;
let generation = 0;
let lastFrameAt = 0;
let frameCallback = null;

function show(state, label, detail) {
  status.dataset.state = state;
  status.textContent = label;
  placeholder.hidden = state === "live";
  fullscreen.disabled = state !== "live";
  if (detail) message.textContent = detail;
}

function clearVideo() {
  if (frameCallback !== null) video.cancelVideoFrameCallback(frameCallback);
  frameCallback = null;
  if (video.srcObject) video.srcObject.getTracks().forEach((track) => track.stop());
  video.srcObject = null;
  lastFrameAt = 0;
}

function stop() {
  generation++;
  if (reader) reader.close();
  reader = null;
  clearVideo();
}

function connect() {
  stop();
  const current = generation;
  show("waiting", "Waiting for your phone", "Ready when you are");
  if (!window.RTCPeerConnection || !video.requestVideoFrameCallback) {
    show("error", "Browser not supported", "Use a current browser with WebRTC video support");
    return;
  }
  reader = new MediaMTXWebRTCReader({
    url: new URL("/screen/whep", window.location.href).href,
    onError: (error) => {
      if (current !== generation) return;
      // Keep protocol errors in the console; offer an actionable state to viewers.
      console.warn(error);
      clearVideo();
      show("waiting", "Waiting for your phone · reconnecting", "Stream disconnected or unavailable");
    },
    onTrack: (event) => {
      if (current !== generation || event.track.kind !== "video") return;
      clearVideo();
      video.srcObject = event.streams[0] || new MediaStream([event.track]);
      const stream = video.srcObject;
      const frame = () => {
        if (current !== generation || video.srcObject !== stream) return;
        lastFrameAt = performance.now();
        show("live", "Live · " + video.videoWidth + " × " + video.videoHeight);
        frameCallback = video.requestVideoFrameCallback(frame);
      };
      frameCallback = video.requestVideoFrameCallback(frame);
      video.play().catch(() => {
        if (current === generation) show("error", "Playback paused", "Select Reconnect to start playback");
      });
    },
  });
}

// A negotiated track is not proof that decoded video has arrived.
window.setInterval(() => {
  if (lastFrameAt && performance.now() - lastFrameAt > 5000) {
    // UDP peers can stay nominally connected after the sender stops. Replace the
    // stale connection so a new sender is visible before ICE's longer timeout.
    connect();
    show("waiting", "Waiting for your phone · reconnecting", "No recent video frames");
  }
}, 1000);

document.querySelector("#reconnect").addEventListener("click", connect);
fullscreen.addEventListener("click", () => {
  document.querySelector("#stage").requestFullscreen().catch((error) => {
    console.warn(error);
    show("error", "Full screen unavailable", "Continue viewing in this window");
  });
});
window.addEventListener("pagehide", stop);
window.addEventListener("pageshow", (event) => { if (event.persisted) connect(); });
connect();
