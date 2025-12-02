# Quick Start Guide - OpenJDK Upgrade Agent

Get started with the OpenJDK Upgrade Agent in 5 minutes!

## Prerequisites

- Python 3.x installed
- Administrative/sudo privileges
- Internet connection

## Installation

No installation needed! Just download the script:

```bash
# Clone or download the repository
cd Open-JDK-Upgrade-Agent
```

## Quick Start

### Step 1: Check What Would Happen (Dry Run)

```bash
python openjdk_upgrade_agent.py --target-version 17 --dry-run
```

This shows you exactly what the agent will do without making any changes.

### Step 2: Review the Report

Check the generated report:

```bash
# Linux/macOS
cat temp/openjdk-agent-logs/run_*/README.md

# Windows
type temp\openjdk-agent-logs\run_*\README.md
```

### Step 3: Run the Actual Upgrade

If the dry run looks good, run the actual upgrade:

```bash
# Linux/macOS (may need sudo)
python3 openjdk_upgrade_agent.py --target-version 17

# Windows (run PowerShell as Administrator)
python openjdk_upgrade_agent.py --target-version 17
```

## Common Use Cases

### Upgrade to Latest LTS (Java 21)

```bash
python openjdk_upgrade_agent.py --target-version 21
```

### Upgrade and Check Application Dependencies

```bash
python openjdk_upgrade_agent.py \
  --target-version 17 \
  --app-path /path/to/your/application
```

### Upgrade with Health Check

```bash
python openjdk_upgrade_agent.py \
  --target-version 17 \
  --health-url your-app.example.com
```

## What Happens During Upgrade?

1. **Detects** your current Java installation
2. **Backs up** your existing Java (to `temp/openjdk-backups/`)
3. **Installs** the new version using your system's package manager
4. **Verifies** the installation was successful
5. **Generates** a detailed report with rollback instructions

## If Something Goes Wrong

### Rollback to Previous Version

The agent creates a backup before making changes. To rollback:

**Linux/macOS:**
```bash
# Find your backup
ls temp/openjdk-backups/

# Extract it
tar -xzf temp/openjdk-backups/openjdk_backup_TIMESTAMP.tar.gz -C /path/to/restore
```

**Windows:**
```powershell
# Find your backup
dir temp\openjdk-backups\

# Extract it
Expand-Archive -Path temp\openjdk-backups\openjdk_backup_TIMESTAMP.zip -DestinationPath C:\path\to\restore
```

## Getting Help

### View All Options

```bash
python openjdk_upgrade_agent.py --help
```

### Check Logs

All actions are logged in:
```
temp/openjdk-agent-logs/run_TIMESTAMP/commands.log
```

### Run Tests

Validate the agent is working correctly:

```bash
python test_agent.py
```

## Tips

✓ **Always run with `--dry-run` first** to see what will happen

✓ **Keep backups** - they're stored in `temp/openjdk-backups/`

✓ **Review reports** - detailed logs are in `temp/openjdk-agent-logs/`

✓ **Test in dev first** - try on a development machine before production

✓ **Use health checks** - add `--health-url` to verify connectivity

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [EXAMPLES.md](EXAMPLES.md) for more usage examples
- Review [DEVELOPMENT.md](DEVELOPMENT.md) for architecture details

## Support

For issues or questions:
1. Check the generated report in `temp/openjdk-agent-logs/`
2. Review the command logs
3. Run with `--dry-run` to diagnose issues

---

**Ready to upgrade?** Start with a dry run and you'll be up and running in minutes!
