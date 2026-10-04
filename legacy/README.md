# Legacy: Selenium / OpenCV / PyAutoGUI Twitter automation

This folder is the original version of this repository, kept as-is for reference.
It drove the Twitter web app through Selenium XPaths, OpenCV template matching
(`template_images/`) and PyAutoGUI. Twitter/X has since changed its markup, so most
XPaths and templates no longer match.

It is **not** maintained, linted or tested. The new VLM-based Android agent lives in
`../android_automation/`.

## Running it anyway

All imports are relative to this folder, so run from here:

```bash
cd legacy
python3 -m pip install -r requirements.txt
export PYTHONPATH="$PWD"
export DRIVER_PATH=/path/to/chromedriver
export METADATA=/path/to/bot_metadata.json
python3 examples/like.py
```

The cron runners in `automation/*/runner.sh` resolve paths relative to themselves,
so they keep working from their new location.
