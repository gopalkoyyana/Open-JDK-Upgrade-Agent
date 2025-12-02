# OpenJDK Upgrade Agent - Examples

This document provides practical examples of using the OpenJDK Upgrade Agent.

## Example 1: Basic Dry Run

Check what the agent would do before making any changes:

```bash
python openjdk_upgrade_agent.py --target-version 17 --dry-run
```

**Expected Output:**
- Detects current Java installation
- Shows which package manager would be used
- Simulates the upgrade process
- Generates a report in `temp/openjdk-agent-logs/run_TIMESTAMP/README.md`

## Example 2: Upgrade to OpenJDK 21

Upgrade to the latest LTS version:

```bash
python openjdk_upgrade_agent.py --target-version 21
```

**What happens:**
1. Detects current Java installation and JAVA_HOME
2. Creates a backup of existing Java installation
3. Attempts to install OpenJDK 21 using system package manager
4. Verifies the installation
5. Generates a detailed report with rollback instructions

## Example 3: Analyze Application Dependencies

Check which libraries your application uses and upgrade them:

```bash
python openjdk_upgrade_agent.py --target-version 17 --app-path /path/to/your/app
```

**What happens:**
1. Upgrades Java to version 17
2. Analyzes the application binary for dependencies (using ldd, otool, or dumpbin)
3. Identifies system packages for those dependencies
4. Asks for your permission to upgrade them
5. Upgrades approved packages

## Example 4: Custom Backup and Log Directories

Specify where to store backups and logs:

```bash
python openjdk_upgrade_agent.py \
  --target-version 17 \
  --backup-dir /var/backups/java \
  --log-dir /var/log/java-upgrades
```

## Example 5: Force Upgrade (Skip Confirmations)

Use with caution - skips all user prompts:

```bash
python openjdk_upgrade_agent.py --target-version 17 --force
```

## Example 6: Health Check After Upgrade

Verify connectivity after upgrade:

```bash
python openjdk_upgrade_agent.py \
  --target-version 17 \
  --health-url example.com
```

## Example 7: Complete Production Upgrade

Full upgrade with all safety features:

```bash
# Step 1: Dry run to see what will happen
python openjdk_upgrade_agent.py \
  --target-version 17 \
  --app-path /opt/myapp/bin/myapp \
  --backup-dir /backup/java \
  --log-dir /var/log/java-agent \
  --health-url myapp.example.com \
  --dry-run

# Step 2: Review the generated report
cat /var/log/java-agent/run_TIMESTAMP/README.md

# Step 3: Perform actual upgrade
python openjdk_upgrade_agent.py \
  --target-version 17 \
  --app-path /opt/myapp/bin/myapp \
  --backup-dir /backup/java \
  --log-dir /var/log/java-agent \
  --health-url myapp.example.com
```

## Platform-Specific Examples

### Linux (Ubuntu/Debian)

```bash
# Uses apt-get
sudo python3 openjdk_upgrade_agent.py --target-version 17
```

### Linux (RHEL/CentOS)

```bash
# Uses yum
sudo python3 openjdk_upgrade_agent.py --target-version 17
```

### macOS

```bash
# Uses Homebrew
python3 openjdk_upgrade_agent.py --target-version 17
```

### Windows (PowerShell as Administrator)

```powershell
# Uses Chocolatey or Winget
python openjdk_upgrade_agent.py --target-version 17
```

## Rollback Example

If something goes wrong, use the backup:

### Linux/macOS

```bash
# Find the backup path in the report
tar -xzf /path/to/backup/openjdk_backup_TIMESTAMP.tar.gz -C /path/to/restore

# Update JAVA_HOME
export JAVA_HOME=/path/to/restored/java
```

### Windows

```powershell
# Extract the backup ZIP file
Expand-Archive -Path C:\path\to\backup\openjdk_backup_TIMESTAMP.zip -DestinationPath C:\path\to\restore

# Update JAVA_HOME environment variable
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\path\to\restored\java', 'Machine')
```

## Troubleshooting

### Issue: Package manager not found

**Solution:** Install manually or use the fallback method:
- The agent will attempt to download from Adoptium API
- Check the logs for download URL and manual installation instructions

### Issue: Permission denied

**Solution:** Run with appropriate privileges:
- Linux/macOS: Use `sudo`
- Windows: Run PowerShell as Administrator

### Issue: Dependency upgrade fails

**Solution:** Review the packages list and upgrade manually:
```bash
# Linux (apt)
sudo apt-get install --only-upgrade package-name

# macOS (Homebrew)
brew upgrade package-name

# Windows (Chocolatey)
choco upgrade package-name -y
```
