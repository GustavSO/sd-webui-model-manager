import launch

if not launch.is_installed("browser-cookie3"):
    launch.run_pip("install browser-cookie3", "requirements for Model Manager")
if not launch.is_installed("selenium"):
        launch.run_pip("install selenium", "requirements for Model Manager")
if not launch.is_installed("webdriver-manager"):
        launch.run_pip("install webdriver-manager", "requirements for Model Manager")
if not launch.is_installed("blake3"):
        launch.run_pip("install blake3", "[Model Manager] - Installing blake3 for hashing")
