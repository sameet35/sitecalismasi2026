import asyncio
import random
import logging
import sys
import os
from datetime import datetime
from playwright.async_api import async_playwright

# --- AYARLAR ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Görünüm alanlarını sadeleştirdim (GitHub sunucusu için en verimli olanlar)
DESKTOP_VIEWPORTS = [{'width': 1920, 'height': 1080}, {'width': 1440, 'height': 900}]
MOBILE_VIEWPORTS = [{'width': 390, 'height': 844}, {'width': 412, 'height': 915}]

def basarili_kaydet(link, tiklama_oldu):
    with open("ziyaret_basarili.txt", "a", encoding="utf-8") as f:
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        durum = "Linke Tiklandi" if tiklama_oldu else "Sadece Gezindi"
        f.write(f"{tarih} | {durum} | Link: {link}\n")

def dosya_oku(dosya_adi):
    if not os.path.exists(dosya_adi): return []
    with open(dosya_adi, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and "." in line]

async def human_interaction(page, base_url):
    tiklama_yapildi = False
    try:
        await asyncio.sleep(random.randint(3, 6))
        # Rastgele kaydırma
        for i in range(random.randint(2, 4)):
            scroll_dist = random.randint(300, 600)
            await page.evaluate(f"window.scrollBy(0, {scroll_dist})")
            await asyncio.sleep(random.uniform(1, 3))
        
        # %40 Tıklama Şansı
        if random.random() <= 0.40:
            domain = base_url.split("//")[-1].split("/")[0]
            valid_links = await page.query_selector_all(f'a[href*="{domain}"]')
            
            if valid_links:
                target = random.choice(valid_links[:5])
                if await target.is_visible():
                    await target.click(timeout=5000, force=True)
                    tiklama_yapildi = True
                    await asyncio.sleep(5)
    except: pass
    return tiklama_yapildi

async def send_hit(target_url, user_agent):
    async with async_playwright() as p:
        is_mobile = any(x in user_agent for x in ["Mobile", "Android", "iPhone"])
        viewport = random.choice(MOBILE_VIEWPORTS if is_mobile else DESKTOP_VIEWPORTS)
        
        print(f"\nZİYARET BAŞLADI: {target_url}")
        print(f"CİHAZ: {'MOBİL' if is_mobile else 'MASAÜSTÜ'}")

        browser = await p.chromium.launch(headless=True) # GitHub için headless=True olmalı
        context = await browser.new_context(user_agent=user_agent, viewport=viewport)
        page = await context.new_page()
        
        # Bot korumasını gizle
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            tiklama_oldu = await human_interaction(page, target_url)
            basarili_kaydet(target_url, tiklama_oldu)
            print("Ziyaret Başarılı.")
        except Exception as e:
            print(f"Hata oluştu: {e}")
        finally:
            await browser.close()

async def main():
    urls = dosya_oku("linklerim.txt")
    uas = dosya_oku("user-agents.txt")
    
    if not urls:
        print("HATA: linklerim.txt bulunamadı veya boş!")
        return

    # GitHub Actions'da 'while True' yerine belirli sayıda tur atmak daha iyidir
    # Çünkü Actions'ın bir süre sınırı vardır. Örn: 5 tur.
    for _ in range(5): 
        target = random.choice(urls)
        ua = random.choice(uas) if uas else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0"
        await send_hit(target, ua)
        await asyncio.sleep(random.randint(5, 10))

if __name__ == "__main__":
    asyncio.run(main())