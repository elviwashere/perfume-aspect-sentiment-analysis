from playwright.sync_api import sync_playwright
import pandas as pd


def scrape_product(page, brand, product_name, url, max_reviews=300):

    page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    # =====================================
    # Tutup overlay/popup kalau ada (cookie consent, modal, dsb)
    # =====================================
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
    except:
        pass

    for selector_popup in [
        "button[aria-label='Close']",
        "[data-testid='btnModalClose']",
        "button:has-text('Tutup')",
    ]:
        try:
            popup = page.locator(selector_popup)
            if popup.count() > 0:
                popup.first.evaluate("el => el.click()")
                page.wait_for_timeout(500)
        except:
            pass

    data = []
    page_number = 1

    while True:

        print(f"\nScraping halaman {page_number}")

        # =====================================
        # Klik semua tombol "Selengkapnya"
        # =====================================
        while True:

            tombol = page.get_by_text("Selengkapnya", exact=True)

            jumlah = tombol.count()

            if jumlah == 0:
                break

            for i in range(jumlah):

                try:
                    el = tombol.nth(i)
                    el.scroll_into_view_if_needed(timeout=1000)
                    el.evaluate("el => el.click()")
                except:
                    pass

            page.wait_for_timeout(800)

            sisa = page.get_by_text("Selengkapnya", exact=True).count()

            # kalau jumlah tombol yg masih ada gak berkurang sama sekali
            # setelah 1 putaran klik, anggap stuck -> stop biar gak infinite
            if sisa >= jumlah:
                if sisa > 0:
                    print(f"  [!] {sisa} tombol 'Selengkapnya' gagal diklik, dilewati.")
                break

        # =====================================
        # Ambil review
        # =====================================

        cards = page.locator("article")

        # snapshot review pertama di halaman ini, buat verifikasi nanti
        # kalau pagination beneran pindah atau tidak
        try:
            signature_before = cards.nth(1).locator(
                '[data-testid="lblItemUlasan"]'
            ).inner_text(timeout=2000)
        except:
            signature_before = ""

        for i in range(1, cards.count()):

            card = cards.nth(i)

            try:
                username = card.locator(".name").inner_text()
            except:
                username = ""

            try:
                rating = card.locator(
                    '[data-testid="icnStarRating"]'
                ).get_attribute("aria-label")

                rating = rating.replace("bintang ", "")
            except:
                rating = ""

            try:
                tanggal = card.locator(
                    "p.css-1rpz5os-unf-heading"
                ).inner_text()
            except:
                tanggal = ""

            try:
                review = card.locator(
                    '[data-testid="lblItemUlasan"]'
                ).inner_text()
            except:
                review = ""

            data.append({
                "brand": brand,
                "product": product_name,
                "username": username,
                "rating": rating,
                "tanggal": tanggal,
                "review": review
            })

            if len(data) >= max_reviews:
                break

        print(f"Total review sementara: {len(data)}")

        if len(data) >= max_reviews:
            print(f"Limit {max_reviews} review tercapai, lanjut ke produk berikutnya.")
            break

        # =====================================
        # NEXT PAGE
        # =====================================

        try:

            page.locator("nav").last.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)

            next_button = page.locator(
                'button[aria-label="Laman berikutnya"]'
            )

            if next_button.count() == 0:
                print("Sudah halaman terakhir")
                break

            if not next_button.is_enabled():
                print("Sudah halaman terakhir")
                break

            print(f"Pindah ke halaman {page_number + 1}")

            next_button.evaluate("el => el.click()")

            # verifikasi halaman beneran ganti (bukan cuma nunggu fix timeout)
            pindah_sukses = False

            for percobaan in range(6):  # coba sampai ~9 detik total

                page.wait_for_timeout(1500)

                try:
                    signature_after = page.locator("article").nth(1).locator(
                        '[data-testid="lblItemUlasan"]'
                    ).inner_text(timeout=2000)
                except:
                    signature_after = ""

                if signature_after and signature_after != signature_before:
                    pindah_sukses = True
                    break

            if not pindah_sukses:
                print("  [!] Halaman tidak berubah setelah diklik, dianggap sudah halaman terakhir / stuck. Berhenti.")
                break

            page_number += 1

        except Exception as e:

            print("Pagination berhenti:", e)
            break

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["username", "tanggal", "review"], keep="first")

    return df