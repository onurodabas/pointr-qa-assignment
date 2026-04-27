"""
Behave environment hooks for the UI automation suite.
Handles browser setup/teardown and selects Chrome or Firefox via
the BROWSER environment variable (default: chrome).
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import os


def before_all(context):
    """Set up the output directory and pick the browser."""
    context.output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'output'
    )
    # Create output directory with write permissions
    os.makedirs(context.output_dir, exist_ok=True)
    # Ensure directory is writable (fixes permission issues on some systems)
    try:
        os.chmod(context.output_dir, 0o755)
    except OSError:
        pass  # If chmod fails (e.g., Windows), continue anyway

    # Use the BROWSER env var, default to Chrome.
    # Example: BROWSER=firefox behave
    context.browser_name = os.environ.get('BROWSER', 'chrome').lower()

    print(f"\nBrowser: {context.browser_name.upper()}")
    print(f"Output directory: {context.output_dir}")


def before_scenario(context, scenario):
    """Start a fresh browser instance for each scenario for test isolation."""
    if context.browser_name == 'chrome':
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-notifications')

        service = ChromeService(ChromeDriverManager().install())
        context.driver = webdriver.Chrome(service=service, options=chrome_options)

    elif context.browser_name == 'firefox':
        firefox_options = FirefoxOptions()

        service = FirefoxService(GeckoDriverManager().install())
        context.driver = webdriver.Firefox(service=service, options=firefox_options)
        context.driver.maximize_window()

    else:
        raise ValueError(
            f"Unknown browser '{context.browser_name}'. Use 'chrome' or 'firefox'."
        )

    context.driver.implicitly_wait(10)
    print(f"\nStarting scenario: {scenario.name}")


def after_scenario(context, scenario):
    """Quit the browser after each scenario."""
    if hasattr(context, 'driver'):
        context.driver.quit()

    print(f"Scenario '{scenario.name}' - {scenario.status}")


def after_all(context):
    print("\n" + "=" * 60)
    print("All tests completed")
    print(f"Results saved to: {context.output_dir}")
    print("=" * 60)
