import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to dashboard...")
        await page.goto("http://localhost:43212/dashboard", wait_until="networkidle")
        
        # Look for the publish button and click it
        print("Clicking Publish button...")
        # Need to find the specific publish button or execute window.triggerPublish()
        await page.evaluate("window.triggerPublish(false)")
        
        # Wait a bit for the popup or logs to happen
        await asyncio.sleep(2)
        
        # Capture the SweetAlert content if present
        swal_visible = await page.locator(".swal2-container").is_visible()
        if swal_visible:
            title = await page.locator(".swal2-title").inner_text()
            print(f"SweetAlert popup appeared! Title: {title}")
            # Click cancel
            print("Clicking cancel...")
            cancel_btn = page.locator(".swal2-cancel")
            if await cancel_btn.is_visible():
                await cancel_btn.click()
            else:
                ok_btn = page.locator(".swal2-confirm")
                await ok_btn.click()
        else:
            print("No popup appeared.")
            
        await asyncio.sleep(1)
        await browser.close()

asyncio.run(run())
