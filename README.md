# PyUdisk

PyUdisk is a python module to generate a S.M.A.R.T metrics for all drives/partitions on macOS and Linux machines.

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

- **SMART_LIB**: Path to the S.M.A.R.T CLI library. Uses `udisksctl` for Linux and `smartctl` for macOS.
- **DISK_LIB**: Path to disk util library. Uses `lsblk` for Linux and `diskutil` for macOS.
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
