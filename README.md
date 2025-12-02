
# OpenJDK Upgrade Agent

A cross-platform Python agent designed to detect, backup, and upgrade OpenJDK on various operating systems including Linux, macOS, and Windows.

## Features

*   **Detection**: Identifies existing Java/OpenJDK installations (`JAVA_HOME`).
*   **Dependency Analysis**: Checks which libraries an application is linked against (using `ldd`, `otool`, etc.) when an application path is provided.
*   **Dependency Upgrade**: Identifies and upgrades application dependencies (libraries) using system package managers, with user confirmation. Supports Linux (apt, yum, rpm, dpkg).
*   **Backup**: Automatically backs up the existing `JAVA_HOME` directory before making changes.
*   **Smart Upgrade**:
    *   Uses system package managers (`apt`, `yum`, `brew`, `choco`, `winget`) if available.
    *   Falls back to a "side-install" (manual download/install) if package managers fail (Note: Side-install logic is a placeholder in this version).
*   **Verification**: Runs smoke tests including version checks.
*   **Reporting**: Generates detailed logs and a run report.

## Prerequisites

*   **Python 3.x** installed on the system.
*   **Internet Access**: Required to download OpenJDK packages or binaries.
*   **Administrative Privileges**: Required for installing packages via system package managers (e.g., `sudo` on Linux, Admin Command Prompt on Windows).

## Installation

No special installation is required. Simply download the script `openjdk_upgrade_agent.py` to the target machine.

## Usage

Run the script from the command line using Python 3.

### Basic Usage

To upgrade OpenJDK to a specific version (e.g., 17):

```bash
python3 openjdk_upgrade_agent.py --target-version 17
```

### Dry Run (Recommended First Step)

To see what the agent *would* do without actually making any changes:

```bash
python3 openjdk_upgrade_agent.py --target-version 17 --dry-run
```

### Inspecting an Application

To check which libraries a specific application is using and potentially upgrade them:

```bash
python3 openjdk_upgrade_agent.py --target-version 17 --app-path /path/to/your/application
```

### Upgrading Application Dependencies

When `--app-path` is provided, the agent will also check for system dependencies linked to the application. It will list them and ask for your permission to upgrade them using the system package manager.

### Customizing Directories

You can specify where backups and logs are stored:

```bash
python3 openjdk_upgrade_agent.py \
  --target-version 17 \
  --backup-dir /var/backups/openjdk \
  --log-dir /var/log/openjdk-agent
```

### Health Check

To run a health check (placeholder URL check) after upgrade:

```bash
python3 openjdk_upgrade_agent.py --target-version 17 --health-url example.com
```

## Command Line Arguments

| Argument | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `--target-version` | The OpenJDK version to install (e.g., `17`, `21`). | **Yes** | - |
| `--app-path` | Path to an application binary to inspect for dependencies. | No | `None` |
| `--dry-run` | Simulate the process without making changes. | No | `False` |
| `--backup-dir` | Directory to store backups. | No | `temp/openjdk-backups` |
| `--log-dir` | Directory to store logs and reports. | No | `temp/openjdk-agent-logs` |
| `--health-url` | URL or host for smoke tests (e.g., `example.com`). | No | `None` |
| `--force` | Force destructive actions and skip confirmation prompts. | No | `False` |

## Output

The agent creates a timestamped directory in the `log-dir` containing:
*   `README.md`: A summary report of the run.
*   `commands.log`: A detailed log of all executed commands and their output.

## Rollback

If an upgrade causes issues, you can restore the previous Java installation from the backup created in the `backup-dir`.
