# Incident.io take-home challenge: on-call scheduling system - Ruby

## Requirements
- **Python Version**: this project requires Python 3.6 or higher.
- No external dependency is used for this project

## Instructions on running the code
1. navigate to the directory of the script:
```bash
cd path/to/script
```
2. ensure you have Python installed. You can check your Python version by running the following (replace python3 with apropriate aliases):
```bash
python3 --version
```
3. execute the file
- option 1: make the script executable and execute the script by running (this method assumes you have python installed as python3, configured with the shebang line `#!/usr/bin/env python3`):
```bash
chmod +x render-schedule

./render-schedule \
    --schedule=schedule.json \
    --overrides=overrides.json \
    --from='2025-11-07T17:00:00Z' \
    --until='2025-11-21T17:00:00Z'
```
- option 2: if the above does not work for any reason, please run it with the standard python execution by running the following (again, replace python3 with appropriate aliases):
```bash
python3 render-schedule \
    --schedule=schedule.json \
    --overrides=overrides.json \
    --from='2025-11-07T17:00:00Z' \
    --until='2025-11-21T17:00:00Z'
```
4. (optional) run the tests by running:
``` bash
python3 -m unittest test_schedule.py
```

### Troubleshooting
If you receive a "command not found" error when trying to run the script, ensure that Python 3 is installed and accessible in your PATH.
Check your command to run Python (e.g. python3, python, py) and change the shebang line at the top of the script to ensure it is set to your alias if you want to run the file with `./render-schedule`.


## Notes
link to video: https://www.loom.com/share/7ca3e84e667849ba82d41296c3844f18
