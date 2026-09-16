import time

from playwright.sync_api import sync_playwright


CAPTCHA_SCRIPT = """
(selector) => {
    const captcha = document.querySelector(selector);

    if (!captcha) {
        console.log("CAPTCHA field not found.");
        return;
    }

    captcha.style.border = "3px solid red";
    captcha.style.boxShadow = "0 0 15px 5px rgba(255, 0, 0, 0.7)";
    captcha.style.backgroundColor = "#fff3f3";

    captcha.scrollIntoView({ behavior: "smooth", block: "center" });
    captcha.focus();

    const warning = document.createElement("div");
    warning.id = "tax-suite-captcha-warning";
    warning.innerHTML = `
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            width: 360px;
            background: white;
            border: 2px solid #ff9800;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.35);
            z-index: 999999;
            font-family: Arial, sans-serif;
        ">
            <div style="
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            ">
                CAPTCHA Required
            </div>
            <div style="
                font-size: 14px;
                line-height: 1.5;
                margin-bottom: 15px;
            ">
                Username and password have been filled automatically.
                <br><br>
                The CAPTCHA field has been highlighted.
                Please enter the CAPTCHA manually.
            </div>
            <button
                onclick="
                    document.getElementById(
                        'tax-suite-captcha-warning'
                    ).remove()
                "
                style="
                    padding: 8px 25px;
                    border: none;
                    border-radius: 5px;
                    background: #333;
                    color: white;
                    cursor: pointer;
                    font-size: 14px;
                "
            >
                OK
            </button>
        </div>
    `;

    document.body.appendChild(warning);
}
"""


def _fill_field(page, field, value, timeout_ms=8000):
    deadline = time.time() + timeout_ms / 1000

    while time.time() < deadline:
        for selector in field["selectors"]:
            try:
                locator = page.locator(selector).first
                if locator.count() and locator.is_visible(timeout=500):
                    locator.fill(value)
                    print(f"Filled {field['label']} using {selector}")
                    return True
            except Exception:
                continue
        page.wait_for_timeout(500)

    return False


def _click_advance(page, advance):
    for selector in advance.get("selectors", []):
        try:
            locator = page.locator(selector).first
            if locator.count() and locator.is_visible(timeout=500):
                locator.click()
                print(f"Clicked '{advance.get('label', selector)}'")
                return True
        except Exception:
            continue
    return False


def _tick_checkbox(page, checkbox):
    for selector in checkbox.get("selectors", []):
        try:
            locator = page.locator(selector).first
            if not (locator.count() and locator.is_visible(timeout=1000)):
                continue

            if locator.is_checked():
                print(f"Checkbox already checked ({selector}).")
                return True

            locator.click(force=True)
            page.wait_for_timeout(300)

            if locator.is_checked():
                print(f"Ticked checkbox ({selector}).")
                return True
        except Exception:
            continue

    try:
        mat = page.locator("mat-checkbox").first
        if mat.count():
            mat.click(force=True)
            print("Ticked checkbox via mat-checkbox.")
            return True
    except Exception:
        pass

    return False


def _click_submit(page, submit):
    for selector in submit.get("selectors", []):
        try:
            locator = page.locator(selector).first
            if locator.count() and locator.is_visible(timeout=1000):
                if not locator.is_disabled():
                    locator.click()
                    print(f"Clicked '{submit.get('label', 'submit')}' button.")
                    return True
        except Exception:
            continue
    return False


def _highlight_captcha(page, selectors):
    try:
        for selector in selectors:
            if page.locator(selector).first.count():
                page.evaluate(CAPTCHA_SCRIPT, selector)
                print(f"Highlighted CAPTCHA using {selector}")
                return True
    except Exception as e:
        print("Could not highlight CAPTCHA:", e)
    return False


BROWSER_ARGS = ["--disable-blink-features=AutomationControlled"]

STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
"""


def run_login(tool, username, password):
    print(f"Starting automatic login for {tool['name']}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=BROWSER_ARGS,
        )
        context = browser.new_context()
        context.add_init_script(STEALTH_SCRIPT)
        page = context.new_page()

        page.goto(tool["portal"], wait_until="domcontentloaded")
        page.wait_for_timeout(tool.get("load_wait", 3000))

        print("Login page opened.")

        for field in tool.get("fields", []):
            value = username if field["kind"] == "username" else password

            if field["kind"] == "password" and tool.get("advance"):
                _click_advance(page, tool["advance"])
                filled = _fill_field(page, field, value, timeout_ms=20000)
            else:
                filled = _fill_field(page, field, value)

            if not filled:
                print(f"Could not fill {field['label']}. Selectors may need updating.")

        if tool.get("checkbox"):
            _tick_checkbox(page, tool["checkbox"])

        captcha_found = _highlight_captcha(
            page,
            tool.get("captcha_selectors", []),
        )

        if not captcha_found and tool.get("submit"):
            page.wait_for_timeout(2000)
            if _click_submit(page, tool["submit"]):
                print("Login submitted automatically.")
            else:
                print("Could not find the login submit button.")

        print("Login flow complete. Browser will stay open.")

        while not page.is_closed():
            page.wait_for_timeout(1000)

        browser.close()


def run_login_in_thread(tool, username, password):
    from threading import Thread

    thread = Thread(target=run_login, args=(tool, username, password), daemon=True)
    thread.start()
    return thread