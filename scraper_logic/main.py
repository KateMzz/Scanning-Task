import json
import logging
import asyncio
from typing import Optional, Dict

from playwright.async_api import (
    async_playwright,
    Error,
    Page,
    Route,
    BrowserContext,
    Response,
)
from data_extraction import extract_data
from user_scheme import Employee
from user_creds import user_data
import sys


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("my_logger")


BLOCK_RESOURCE_TYPES = [
    "beacon",
    "csp_report",
    "font",
    "image",
    "imageset",
    "media",
    "object",
    "texttrack",
]

BLOCK_RESOURCE_NAMES = [
    "adzerk",
    "analytics",
    "cdn.api.twitter",
    "doubleclick",
    "exelator",
    "facebook",
    "fontawesome",
    "google",
    "google-analytics",
    "googletagmanager",
]

args = [
    "--deny-permission-prompts",
    "--no-default-browser-check",
    "--no-first-run",
    "--deny-permission-prompts",
    "--disable-popup-blocking",
    "--ignore-certificate-errors",
    "--no-service-autorun",
    "--window-size=640,480",
    "--disable-audio-output",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

MAX_RETRIES = 3
LOGIN_PAGE = "https://www.upwork.com/ab/account-security/login"
PROFILE_CONTACT_INFO = "https://www.upwork.com/freelancers/settings/api/v1/contactInfo"


async def block_resources(route: Route) -> None:
    """It checks if the requested resource type or URL contains any blocked items
    and either allows the resource to continue loading or aborts it to block it."""
    if route.request.resource_type in BLOCK_RESOURCE_TYPES:
        logger.info(
            f'blocking background resource {route.request} blocked type "{route.request.resource_type}"'
        )
        return await route.abort()
    if any(key in route.request.url for key in BLOCK_RESOURCE_NAMES):
        logger.info(
            f"blocking background resource {route.request} blocked name {route.request.url}"
        )
        return await route.abort()
    return await route.continue_()


async def on_page_crash(event) -> None:
    """logs an error message when a web page crashes"""
    logger.error("Page crashed with reason:", event["message"])


async def to_json(page: Page) -> Optional[Dict]:
    """Extracts JSON data from a web page"""
    html = await page.evaluate('document.querySelector("pre").innerText')
    if html:
        try:
            response_json = json.loads(html)
            logger.info("converted to JSON")
            return response_json
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON data")
    else:
        logger.error("No <pre> tag found in the HTML content")


async def page_retry(page: Page, context: BrowserContext, max_retries: int) -> None:
    """Retrying the login with new page"""
    await context.clear_cookies()
    logger.info(f"Retrying, the page: {max_retries}")
    await page.close()
    max_retries -= 1
    await login(context, max_retries)


async def page_reload(response: Response, page: Page, max_retries: int = MAX_RETRIES) -> bool:
    """Reloading the page with several tries"""
    for _ in range(max_retries):
        if response.ok:
            return True
        else:
            await page.reload()
            logger.info(f"Reloading the page {_}")
            await page.wait_for_load_state()
    logger.error(f"Couldn't reload the page")
    await page.close()
    return False


async def login_process(page: Page, context: BrowserContext, max_retries: int) -> None:
    """Loging into the user profile"""

    try:
        response = await page.goto(LOGIN_PAGE)
        if not response.ok:
            await page_retry(page, context, max_retries)
        await page.fill("input#login_username", user_data[0]["Username"])
        logger.info("Login page response is 200, filling the form for username")
        await page.click('text="Continue with Email"')
        await asyncio.sleep(2)
        if await page.locator('//*[@id="username-message"]').count() > 0:
            logger.warning("the username is incorrect")
            await page_retry(page, context, max_retries)
        logger.info("filling the password")
        await page.locator("#login_password").fill(user_data[0]["Password"])
        await page.click('text="Log in"')
        await asyncio.sleep(2)
        if await page.locator("#password-message").count() > 0:
            logger.warning("the password is incorrect")
            await page_retry(page, context, max_retries)

        await asyncio.sleep(6)
        logger.info("Username and password are correct")

        if await page.locator("//*[@id='login']/div/div/div[1]/p").count() > 0:
            logger.info("answering the additional question")
            await page.wait_for_selector(".air3-input")
            await page.fill("input.air3-input", user_data[0]["Secret_answer"])
            await page.click("#login_control_continue")
            await asyncio.sleep(3)

            if await page.locator("//*[@id='login']/div/div/div[1]/div[1]/h1[1]").count() > 0:
                logger.error("Wrong additional question answer")
                await page_retry(page, context, max_retries)
    except Error as e:
        logger.error(f"Error: {e}")


async def load_profile(page: Page) -> str | None:
    """Getting profile id for further extraction"""
    if await page.locator("#fwh-sidebar-profile").count() > 0:
        logger.info("on the profile page")
        profile_url = await page.locator('//*[@id="fwh-sidebar-profile"]/div/h3/a').get_attribute(
            "href"
        )
        profile_id = profile_url.rsplit("/", 1)[-1]
        data = {
            "account": profile_id,
        }
        file_path = "../data.json"
        with open(file_path, "w") as f:
            json.dump(data, f)
        logger.info("data.json is ready")
        return profile_id
    else:
        logger.error("Failed to load the profile page after submitting the password")


async def login(context: BrowserContext, max_retries: int) -> str | bool:
    """log into the profile page"""
    page = await context.new_page()
    await page.route("**/*", block_resources)
    page.on("crash", on_page_crash)
    if max_retries == 0:
        logger.error("Can't login, check the credentials")
        await page.close()
        return False
    try:
        await login_process(page, context, max_retries)
        profile_id = await load_profile(page)
        return profile_id
    except Error as e:
        logger.error(f"Error: {e}")


async def parse_profile(profile_id: str, context: BrowserContext) -> Dict:
    """request API that contains all profile's info"""
    page = await context.new_page()
    await page.route("**/*", block_resources)
    response = await page.goto(
        f"https://www.upwork.com/freelancers/api/v1/freelancer/profile/{profile_id}/details"
    )
    await page_reload(response, page)
    profile_response_json = await to_json(page)
    return profile_response_json


async def parse_contact_info(context: BrowserContext) -> Dict:
    """get contact info from another api request"""
    page = await context.new_page()
    await page.route("**/*", block_resources)
    response = await page.goto(PROFILE_CONTACT_INFO)
    await page_reload(response, page)
    address_response_json = await to_json(page)
    return address_response_json


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=args)
        context = await browser.new_context()
        profile_id = await login(context, max_retries=MAX_RETRIES)
        if profile_id:
            try:
                profile_response_json = await parse_profile(profile_id, context)
                address_response_json = await parse_contact_info(context)
                await browser.close()
                finale_data = await extract_data(
                    address_response_json, profile_response_json, profile_id
                )
                data_to_object = Employee(**finale_data)
                print(data_to_object)
            except (KeyError, ValueError, Error, TypeError) as e:
                logger.error("Some errors happened: %s", e)
        else:
            logger.error("Can't get profile id, check the login function")


if __name__ == "__main__":
    asyncio.run(main())
