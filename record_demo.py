import asyncio
import os
import shutil
from playwright.async_api import async_playwright

async def record_demo():
    video_dir = "/config/Desktop/Session1/my-simple-agent/demo_output"
    os.makedirs(video_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            record_video_dir=video_dir,
            record_video_size={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        print("Navigating to Recipe Concierge frontend...")
        await page.goto("http://localhost:8080", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Prompt 1: What recipes can I make with my pantry?
        print("Executing Prompt 1: What recipes can I make with my pantry?")
        chips = await page.query_selector_all(".prompt-chip")
        if chips and len(chips) > 0:
            await chips[0].click()
        else:
            await page.fill("#input", "What recipes can I make with my pantry?")
            await page.click("button.send-btn")
            
        # Wait for bot reply
        await page.wait_for_selector(".msg.bot", timeout=60000)
        await page.wait_for_timeout(6000)
        
        # Prompt 2: Rich prompt (image generation / database lookup)
        print("Executing Prompt 2: Generate an image of avocado toast")
        if chips and len(chips) >= 3:
            await chips[2].click()
        else:
            await page.fill("#input", "Generate an image of avocado toast")
            await page.click("button.send-btn")
            
        # Wait for bot reply with image / card
        await page.wait_for_timeout(10000)
        
        video_path = await page.video.path()
        await context.close()
        await browser.close()
        
        print(f"Video recorded at: {video_path}")
        target_video = "/config/Desktop/Session1/my-simple-agent/recipe_concierge_demo.webm"
        shutil.copyfile(video_path, target_video)
        print(f"Demo video saved to: {target_video}")

if __name__ == "__main__":
    asyncio.run(record_demo())
