# PyUdisk

PyUdisk is a python module to generate S.M.A.R.T metrics for all drives/partitions on a host machine.

![Python][label-pyversion]

![Platform][label-platform]

[![pypi][label-actions-pypi]][gha_pypi]

[![Pypi][label-pypi]][pypi]
[![Pypi-format][label-pypi-format]][pypi-files]
[![Pypi-status][label-pypi-status]][pypi]

### Installation

**Recommendations**

- Install `python` [3.10] or [3.11]
- Use a dedicated [virtual environment]

For monitoring and reporting, use
```shell
pip install PyUdisk[standard]
```

For basic functionality, use
```shell
pip install PyUdisk
```

### Usage

**IDE**
```python
import pyudisk

if __name__ == '__main__':
    pyudisk.monitor()
```

**CLI**
```shell
pyudisk start
```

> Use `pyudisk --help` for usage instructions.

## Environment Variables

<details>
<summary><strong>Sourcing environment variables from an env file</strong></summary>

> _By default, `PyUdisk` will look for a `.env` file in the current working directory._
</details>

- **SMART_LIB**: Path to the S.M.A.R.T CLI library. Uses `udisksctl` for Linux and `smartctl` for macOS/Windows.
- **DISK_LIB**: Path to disk util library. Uses `lsblk` for Linux, `diskutil` for macOS, and `pwsh` for Windows.
- **METRICS**: List of metrics to monitor. Default: `[]`
- **GMAIL_USER**: Gmail username to authenticate SMTP library.
- **GMAIL_PASS**: Gmail password to authenticate SMTP library.
- **RECIPIENT**: Email recipient for email notifications.
- **PHONE**: Phone number for SMS notifications.
- **NTFY_URL**: URL for Ntfy notifications.
- **NTFY_TOPIC**: Topic for Ntfy notifications.
- **NTFY_USERNAME**: Username for Ntfy notifications.
- **NTFY_PASSWORD**: Password for Ntfy notifications.
- **TELEGRAM_BOT_TOKEN**: Telegram bot token for Telegram notifications.
- **TELEGRAM_CHAT_ID**: Telegram chat ID for Telegram notifications.
- **TELEGRAM_THREAD_ID**: Telegram thread ID for Telegram notifications.
- **DISK_REPORT**: Boolean flag to send disk report via email.
- **REPORT_DIR**: Directory to save disk reports. Default: `report`
- **REPORT_FILE**: Filename for disk reports. Default format: `disk_report_%m-%d-%Y_%I:%M_%p.html`

## Linting
`pre-commit` will ensure linting

**Requirement**
```shell
python -m pip install pre-commit
```

**Usage**
```shell
pre-commit run --all-files
```

## Pypi Package
[![pypi-module][label-pypi-package]][pypi-repo]

[https://pypi.org/project/PyUdisk/][pypi]

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License][license]

[license]: https://github.com/thevickypedia/PyUdisk/blob/master/LICENSE
[label-pypi-package]: https://img.shields.io/badge/Pypi%20Package-PyUdisk-blue?style=for-the-badge&logo=Python
[label-pyversion]: https://img.shields.io/badge/python-3.10%20%7C%203.11-blue
[label-platform]: https://img.shields.io/badge/Platform-Linux|macOS|Windows-1f425f.svg
[label-actions-pypi]: https://github.com/thevickypedia/PyUdisk/actions/workflows/main.yaml/badge.svg
[label-pypi]: https://img.shields.io/pypi/v/PyUdisk
[label-pypi-format]: https://img.shields.io/pypi/format/PyUdisk
[label-pypi-status]: https://img.shields.io/pypi/status/PyUdisk
[gha_pypi]: https://github.com/thevickypedia/PyUdisk/actions/workflows/main.yaml
[pypi]: https://pypi.org/project/PyUdisk
[pypi-files]: https://pypi.org/project/PyUdisk/#files
[pypi-repo]: https://packaging.python.org/tutorials/packaging-projects/
