# Copilot Instructions for `uas-o-matic` Selenium Automation

## Project Overview
This project automates browser interactions with the PUC Goiás education platform using Python and Selenium. The main script is `teste.py`, which logs in, navigates to course content, and interacts with dynamic UI panels.

## Key Files & Structure
- `teste.py`: Main automation script. Contains all navigation and interaction logic.
- `requeriments.txt`: Lists required Python packages for the automation environment.
- `.venv/`: Local Python virtual environment (do not edit).

## Developer Workflow
- **Environment Setup**: Install dependencies using `pip install -r requeriments.txt` inside the `.venv`.
- **Run Automation**: Execute `python teste.py` from the project root or use the full path to the Python executable in `.venv`.
- **Debugging**: Screenshots are saved as `error_screenshot.png` on exceptions for troubleshooting UI issues.

## Selenium Patterns & Conventions
- **Explicit Waits**: Always use `WebDriverWait` and `expected_conditions` for dynamic elements. Example:
  ```python
  wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'information-card__slots')))
  ```
- **Panel Expansion**: To interact with collapsible panels, first scroll into view, then click using JavaScript. If intercepted, fallback to `ActionChains`:
  ```python
  driver.execute_script("arguments[0].click();", panel_header)
  if not wait.until(EC.element_attribute_to_include((By.XPATH, ...), "aria-expanded")):
      actions = ActionChains(driver)
      actions.move_to_element(panel_header).click().perform()
  ```
- **Error Handling**: All major UI actions are wrapped in try/except blocks. On failure, a screenshot is captured and the error is printed.
- **Sensitive Data**: Credentials are hardcoded in `teste.py` for demonstration. For production, use environment variables or secure vaults.

## External Dependencies
- Uses `webdriver-manager` for automatic ChromeDriver management.
- Relies on the structure and classes of the PUC Goiás platform (may break if the site changes).

## Customization & Extension
- To automate other panels or actions, replicate the explicit wait and click patterns found in `teste.py`.
- For new dependencies, add them to `requeriments.txt` and reinstall in `.venv`.

## Example: Adding a New Panel Interaction
```python
panel_header = wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Novo Painel')]/ancestor::button")))
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", panel_header)
driver.execute_script("arguments[0].click();", panel_header)
```

## Troubleshooting
- If elements are not clickable, check for overlays or modals and close them before proceeding.
- Use screenshots for diagnosing UI state at failure points.

---
_If any section is unclear or missing, please provide feedback to improve these instructions._
