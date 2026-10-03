"""End-to-end synthetic video check for an isolated CI runner.

The caller starts Compose first. No Android device or account is needed.
On the developer's computer, use a session-owned browser for manual/device QA.
"""
import argparse
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def check(page, late, url, compose, artifacts):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    await page.goto(url)
    await page.locator('#status[data-state="waiting"]').wait_for()
    assert await page.locator("#fullscreen").is_disabled()
    assert (await page.request.post(url + "/screen/whip")).status == 404
    assert (await page.request.get(url + "/v3/paths/list")).status == 404

    async def send(seconds):
        return await asyncio.create_subprocess_exec(
            *compose, "run", "--rm", "--no-deps", "-T", "--entrypoint", "ffmpeg", "media",
            "-nostdin", "-hide_banner", "-loglevel", "error", "-re",
            "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30",
            "-t", str(seconds), "-an", "-c:v", "libx264", "-profile:v", "baseline",
            "-preset", "ultrafast", "-tune", "zerolatency", "-g", "30",
            "-f", "h264", "tcp://media:49152",
        )

    async def live(target):
        await target.locator('#status[data-state="live"]').wait_for(timeout=25000)
        assert await target.locator("#video").evaluate("v => v.videoWidth") == 640

    async def sample(target):
        return await target.locator("#video").evaluate("""v => {
            const c = document.createElement('canvas'); c.width=160; c.height=90;
            c.getContext('2d').drawImage(v,0,0,160,90);
            return {frames:v.getVideoPlaybackQuality().totalVideoFrames,
                    image:c.toDataURL()};
        }""")

    first = await send(18)
    try:
        await live(page)
        samples = []
        for _ in range(4):
            samples.append(await sample(page))
            await asyncio.sleep(1)
        assert samples[-1]["frames"] > samples[0]["frames"] + 30
        assert len({s["image"] for s in samples}) == 4, "decoded frames did not change"
        # Join after publication has begun; do not rely on the first SPS/PPS/IDR.
        await late.goto(url)
        await live(late)
        await late.close()
        await page.locator("#reconnect").click()
        await live(page)
        await page.locator("#fullscreen").click()
        await page.wait_for_function("() => document.fullscreenElement !== null")
        await page.evaluate("() => document.exitFullscreen()")
        assert await first.wait() == 0
        await page.locator('#status[data-state="waiting"]').wait_for(timeout=20000)
        assert await page.locator("#fullscreen").is_disabled()
    finally:
        if first.returncode is None:
            first.terminate()
            await first.wait()

    # A new sender should work without restarting containers or reloading the viewer.
    await asyncio.sleep(3)
    second = await send(8)
    try:
        await live(page)
        restart_sample = await sample(page)
        await asyncio.sleep(1)
        assert (await sample(page))["frames"] > restart_sample["frames"]
        await page.screenshot(path=str(artifacts / "synthetic-live.png"), full_page=True)
        assert await second.wait() == 0
    finally:
        if second.returncode is None:
            second.terminate()
            await second.wait()

    # Inspect a narrow layout with the receiver offline.
    await page.set_viewport_size({"width": 360, "height": 740})
    await page.reload()
    assert await page.evaluate("() => document.documentElement.scrollWidth <= innerWidth")
    await page.locator("#reconnect").scroll_into_view_if_needed()
    assert await page.locator("#reconnect").is_visible()
    await page.screenshot(path=str(artifacts / "narrow-waiting.png"), full_page=True)
    assert not errors, errors
    return {"changing_frames": len(samples), "first_frame_count": samples[0]["frames"],
            "last_frame_count": samples[-1]["frames"], "late_join": True,
            "reconnect_button": True, "sender_restart": True, "fullscreen": True,
            "narrow_layout": True, "page_errors": errors}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--project", default="ascweb-ci")
    args = parser.parse_args()
    Path("artifacts").mkdir(exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            context = await browser.new_context(viewport={"width": 1280, "height": 900})
            result = await check(await context.new_page(), await context.new_page(),
                                 args.url.rstrip("/"), ["docker", "compose", "-p", args.project], Path("artifacts"))
            result["browser"] = browser.version
            Path("artifacts/synthetic-check.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result))
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
