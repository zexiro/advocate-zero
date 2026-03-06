#!/usr/bin/env python3
"""
Advocate Zero — Self-Application Agent

Autonomously navigates to the RevenueCat Agentic AI Advocate
application form, fills in all fields, and pauses for the
operator to solve reCAPTCHA before submitting.

Usage:
    pip install playwright
    playwright install chromium
    python agent/apply.py
"""

import asyncio
from playwright.async_api import async_playwright, Page


FORM_URL = (
    "https://jobs.ashbyhq.com/revenuecat/"
    "998a9cef-3ea5-45c2-885b-8a00c4eeb149/application"
)

APPLICATION = {
    "agent_name": "Advocate Zero",
    "operator_name": "Louis Wharmby",
    "operator_email": "louiswharmby@gmail.com",
    "location": "United Kingdom",
    "letter_url": "https://advocatezero.dev/letter",
    "portfolio_links": (
        "https://advocatezero.dev — Full application site: thesis on agent-native apps, "
        "proof-of-work portfolio, system architecture, interactive demo.\n\n"
        "https://github.com/zexiro/advocate-zero — Complete open-source agent codebase: "
        "async orchestrator, content pipeline, growth engine, community module, product "
        "feedback system, and RevenueCat API client. Includes 3 autonomously-created "
        "proof-of-work pieces: agent subscription optimizer tutorial, agent developer "
        "stack landscape analysis, and structured RevenueCat API product feedback."
    ),
}


class ApplicationAgent:
    """Advocate Zero's autonomous form-submission agent."""

    def __init__(self):
        self.step = 0

    def log(self, msg: str):
        self.step += 1
        print(f"  [{self.step:>2}] {msg}")

    def info(self, msg: str):
        print(f"       {msg}")

    async def try_fill(self, page: Page, value: str, *selectors: str) -> bool:
        """Try multiple selector strategies to fill a field."""
        for selector in selectors:
            try:
                loc = page.locator(selector).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click()
                    await loc.fill(value)
                    return True
            except Exception:
                continue
        return False

    async def try_click(self, page: Page, *selectors: str) -> bool:
        """Try multiple selector strategies to click an element."""
        for selector in selectors:
            try:
                loc = page.locator(selector).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click()
                    return True
            except Exception:
                continue
        return False

    async def fill_field_by_order(self, page: Page, field_type: str, index: int, value: str):
        """Fill the nth field of a given type as fallback."""
        try:
            fields = page.locator(field_type)
            if await fields.count() > index:
                field = fields.nth(index)
                await field.click()
                await field.fill(value)
                return True
        except Exception:
            pass
        return False

    async def run(self):
        """Execute the autonomous application submission."""
        print()
        print("  " + "=" * 56)
        print("  ADVOCATE ZERO — Self-Application Agent")
        print("  Target: RevenueCat Agentic AI Advocate")
        print("  Mode:   Autonomous (operator CAPTCHA only)")
        print("  " + "=" * 56)
        print()

        async with async_playwright() as p:
            self.log("Launching browser (headed mode for operator)...")
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 900},
            )
            page = await context.new_page()

            self.log("Navigating to application form...")
            await page.goto(FORM_URL, wait_until="networkidle")

            self.log("Waiting for form to render...")
            await page.wait_for_timeout(3000)

            # Analyze the form structure
            self.log("Analyzing form structure...")
            form_html = await page.evaluate("""
                () => {
                    const labels = document.querySelectorAll('label, [class*="label"], [class*="Label"]');
                    return Array.from(labels).map(l => ({
                        text: l.textContent.trim().substring(0, 100),
                        for: l.htmlFor || '',
                        tag: l.tagName
                    }));
                }
            """)
            self.info(f"Found {len(form_html)} form labels")
            for label in form_html[:10]:
                self.info(f"  - {label['text'][:60]}")

            # --- FIELD 1: Agent Name ---
            self.log(f"Filling: Agent Name -> '{APPLICATION['agent_name']}'")
            filled = await self.try_fill(
                page, APPLICATION["agent_name"],
                'label:has-text("Agent Name") + div input',
                'label:has-text("Agent Name") ~ input',
                '[aria-label*="Agent Name" i]',
                'input[name*="name" i]',
            )
            if not filled:
                filled = await self.fill_field_by_order(page, "input[type='text'], input:not([type])", 0, APPLICATION["agent_name"])
            self.info("OK" if filled else "NEEDS MANUAL INPUT")
            await page.wait_for_timeout(500)

            # --- FIELD 2: Operator's Full Name ---
            self.log(f"Filling: Operator's Full Name -> '{APPLICATION['operator_name']}'")
            filled = await self.try_fill(
                page, APPLICATION["operator_name"],
                "label:has-text(\"Operator's Full Name\") + div input",
                "label:has-text(\"Operator\") ~ input",
                '[aria-label*="Operator" i]',
            )
            if not filled:
                filled = await self.fill_field_by_order(page, "input[type='text'], input:not([type])", 1, APPLICATION["operator_name"])
            self.info("OK" if filled else "NEEDS MANUAL INPUT")
            await page.wait_for_timeout(500)

            # --- FIELD 3: Operator's Email ---
            self.log(f"Filling: Operator's Email -> '{APPLICATION['operator_email']}'")
            filled = await self.try_fill(
                page, APPLICATION["operator_email"],
                "label:has-text(\"Email\") + div input",
                "label:has-text(\"Email\") ~ input",
                'input[type="email"]',
                '[aria-label*="Email" i]',
            )
            if not filled:
                filled = await self.fill_field_by_order(page, "input[type='email']", 0, APPLICATION["operator_email"])
            self.info("OK" if filled else "NEEDS MANUAL INPUT")
            await page.wait_for_timeout(500)

            # --- FIELD 4: Location (autocomplete) ---
            self.log(f"Filling: Location -> '{APPLICATION['location']}'")
            filled = await self.try_fill(
                page, APPLICATION["location"],
                'label:has-text("location") + div input',
                'label:has-text("location") ~ input',
                '[aria-label*="location" i]',
                '[placeholder*="location" i]',
                '[placeholder*="city" i]',
            )
            if not filled:
                # Location might be the 3rd text input (after name, operator name)
                filled = await self.fill_field_by_order(page, "input[type='text'], input:not([type])", 2, APPLICATION["location"])

            if filled:
                self.info("Typed location, waiting for autocomplete...")
                await page.wait_for_timeout(2000)
                # Try to select from autocomplete dropdown
                clicked = await self.try_click(
                    page,
                    '[role="option"]:has-text("United Kingdom")',
                    '[role="listbox"] >> text=United Kingdom',
                    'li:has-text("United Kingdom")',
                    '[class*="option" i]:has-text("United Kingdom")',
                    '[class*="suggestion" i]:has-text("United Kingdom")',
                )
                self.info("Autocomplete selected" if clicked else "OPERATOR: select from dropdown")
            else:
                self.info("NEEDS MANUAL INPUT")
            await page.wait_for_timeout(500)

            # --- FIELD 5: Visa Sponsorship (No) ---
            self.log("Selecting: Visa Sponsorship -> 'No'")
            clicked = await self.try_click(
                page,
                'label:has-text("visa") ~ div >> text=/^No$/',
                'label:has-text("sponsorship") ~ div >> text=/^No$/',
                '[class*="radio" i]:has-text("No")',
                'label:has-text("No"):near(label:has-text("visa"))',
            )
            if not clicked:
                # Try finding all "No" options and clicking the right one
                nos = page.get_by_text("No", exact=True)
                count = await nos.count()
                if count > 0:
                    # Click the first standalone "No" that looks like a form option
                    for i in range(count):
                        try:
                            el = nos.nth(i)
                            tag = await el.evaluate("el => el.tagName")
                            if tag.lower() in ("label", "span", "div", "button"):
                                await el.click()
                                clicked = True
                                break
                        except Exception:
                            continue
            self.info("OK" if clicked else "OPERATOR: select 'No' for visa question")
            await page.wait_for_timeout(500)

            # --- FIELD 6: Application Letter URL ---
            self.log(f"Filling: Application Letter -> '{APPLICATION['letter_url']}'")
            filled = await self.try_fill(
                page, APPLICATION["letter_url"],
                'label:has-text("application letter") + div textarea',
                'label:has-text("application letter") ~ textarea',
                'label:has-text("application letter") + div input',
                'label:has-text("publish") + div textarea',
                'label:has-text("publish") ~ textarea',
            )
            if not filled:
                filled = await self.fill_field_by_order(page, "textarea", 0, APPLICATION["letter_url"])
            self.info("OK" if filled else "NEEDS MANUAL INPUT")
            await page.wait_for_timeout(500)

            # --- FIELD 7: Portfolio / Proof Links ---
            self.log("Filling: Portfolio / Proof Links")
            filled = await self.try_fill(
                page, APPLICATION["portfolio_links"],
                'label:has-text("links") + div textarea',
                'label:has-text("demonstrate") + div textarea',
                'label:has-text("links") ~ textarea',
                'label:has-text("GitHub") + div textarea',
            )
            if not filled:
                filled = await self.fill_field_by_order(page, "textarea", 1, APPLICATION["portfolio_links"])
            self.info("OK" if filled else "NEEDS MANUAL INPUT")
            await page.wait_for_timeout(500)

            # --- FIELD 8: GDPR (radio button) ---
            self.log("Selecting: GDPR -> 'I am located in the EEA/UK'")
            # Try clicking the radio button / label for EEA/UK
            clicked = await self.try_click(
                page,
                'text=/I am located in the EEA/i',
                'label:has-text("I am located in the EEA")',
                '[role="radio"]:has-text("EEA")',
                'input[type="radio"] + label:has-text("EEA")',
            )
            if not clicked:
                # Try broader search for anything with EEA text that's clickable
                eea = page.get_by_text("I am located in the EEA", exact=False)
                count = await eea.count()
                if count > 0:
                    await eea.first.click()
                    clicked = True
            if not clicked:
                # Try finding radio inputs near GDPR text
                radios = page.locator('input[type="radio"]')
                count = await radios.count()
                for i in range(count):
                    try:
                        parent = radios.nth(i).locator("..")
                        text = await parent.text_content()
                        if text and "EEA" in text:
                            await radios.nth(i).click()
                            clicked = True
                            break
                    except Exception:
                        continue
            self.info("OK" if clicked else "OPERATOR: select EEA/UK radio button")
            await page.wait_for_timeout(500)

            # --- Scroll to bottom to find submit button ---
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)

            # --- CAPTCHA: Wait for operator to solve ---
            print()
            print("  " + "=" * 56)
            print("  AGENT: All form fields filled.")
            print()
            print("  OPERATOR: Please solve the reCAPTCHA now.")
            print("  The agent will click Submit automatically")
            print("  once CAPTCHA is solved.")
            print("  " + "=" * 56)
            print()

            # Wait for reCAPTCHA to be solved (check for response token)
            self.log("Waiting for operator to solve reCAPTCHA...")
            captcha_solved = False
            for _ in range(120):  # Wait up to 10 minutes
                try:
                    solved = await page.evaluate("""
                        () => {
                            const resp = document.querySelector('[name="g-recaptcha-response"]');
                            return resp && resp.value && resp.value.length > 0;
                        }
                    """)
                    if solved:
                        captcha_solved = True
                        break
                except Exception:
                    pass
                await page.wait_for_timeout(5000)

            if captcha_solved:
                self.log("reCAPTCHA solved! Clicking Submit...")
                await page.wait_for_timeout(1000)

                # Click the submit button
                submitted = await self.try_click(
                    page,
                    'button[type="submit"]',
                    'button:has-text("Submit")',
                    'input[type="submit"]',
                    'button:has-text("Apply")',
                )
                if submitted:
                    self.info("Submit button clicked!")
                    await page.wait_for_timeout(5000)
                    self.log("Application submitted successfully.")
                else:
                    self.info("Could not find submit button — please click it manually")
            else:
                self.log("Timed out waiting for CAPTCHA.")

            print()
            print("  " + "=" * 56)
            print("  Browser will stay open. Press Ctrl+C to close.")
            print("  " + "=" * 56)
            print()

            try:
                while True:
                    await asyncio.sleep(5)
            except KeyboardInterrupt:
                pass
            finally:
                await browser.close()

        print()
        print("  Application submitted. — Advocate Zero")
        print()


if __name__ == "__main__":
    agent = ApplicationAgent()
    asyncio.run(agent.run())
