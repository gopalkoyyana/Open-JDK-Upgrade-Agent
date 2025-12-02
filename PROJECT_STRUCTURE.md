# OpenJDK Upgrade Agent - Project Structure

## Directory Layout

```
Open-JDK-Upgrade-Agent/
│
├── openjdk_upgrade_agent.py    # Main agent script (22KB)
├── test_agent.py                # Automated test suite (4.6KB)
│
├── README.md                    # Main documentation
├── QUICKSTART.md                # Quick start guide
├── EXAMPLES.md                  # Usage examples
├── DEVELOPMENT.md               # Development documentation
├── PROJECT_STRUCTURE.md         # This file
│
└── temp/                        # Generated at runtime
    ├── openjdk-backups/         # Java installation backups
    │   └── openjdk_backup_TIMESTAMP.{tar.gz|zip}
    │
    └── openjdk-agent-logs/      # Run logs and reports
        └── run_TIMESTAMP/
            ├── README.md        # Run report
            └── commands.log     # Detailed command log
```

## File Descriptions

### Core Files

#### `openjdk_upgrade_agent.py` (22KB)
**Purpose**: Main agent implementation

**Key Components**:
- `OpenJDKUpgradeAgent` class - Core agent logic
- `setup_logging()` - Logging infrastructure
- `main()` - Entry point and argument parsing

**Key Methods**:
- `detect_current_java()` - Find existing Java installation
- `backup_java()` - Create timestamped backups
- `install_openjdk()` - Main installation orchestrator
- `try_package_manager_install()` - Package manager strategy
- `manual_install()` - Adoptium API fallback
- `verify_installation()` - Post-install checks
- `health_check()` - Connectivity validation
- `detect_dependencies()` - Analyze app dependencies
- `resolve_packages()` - Map files to packages
- `upgrade_dependencies()` - Upgrade with user consent
- `generate_report()` - Create summary reports

**Dependencies**:
- Standard library only (no external packages required)
- `argparse`, `logging`, `subprocess`, `platform`, `urllib`, `json`, etc.

#### `test_agent.py` (4.6KB)
**Purpose**: Automated testing suite

**Test Coverage**:
- Help message display
- Dry run functionality
- Health check integration
- Error handling
- Custom directory configuration
- Invalid input handling

**Usage**: `python test_agent.py`

### Documentation Files

#### `README.md` (3.9KB)
**Purpose**: Main user documentation

**Sections**:
- Features overview
- Prerequisites
- Installation instructions
- Usage examples
- Command-line arguments
- Output description
- Rollback instructions

**Audience**: End users

#### `QUICKSTART.md` (3.5KB)
**Purpose**: Fast onboarding guide

**Sections**:
- 5-minute quick start
- Common use cases
- Rollback guide
- Tips and best practices

**Audience**: New users wanting to get started quickly

#### `EXAMPLES.md` (4.5KB)
**Purpose**: Practical usage examples

**Sections**:
- Basic examples
- Advanced scenarios
- Platform-specific examples
- Production upgrade workflow
- Troubleshooting

**Audience**: Users looking for specific use cases

#### `DEVELOPMENT.md` (7.4KB)
**Purpose**: Technical documentation

**Sections**:
- Architecture overview
- Feature implementation details
- Class structure
- Execution flow
- Platform support matrix
- Future enhancements

**Audience**: Developers and technical users

#### `PROJECT_STRUCTURE.md` (This file)
**Purpose**: Project organization reference

**Sections**:
- Directory layout
- File descriptions
- Workflow diagrams
- Integration points

**Audience**: Contributors and maintainers

### Generated Files (Runtime)

#### `temp/openjdk-backups/openjdk_backup_TIMESTAMP.{tar.gz|zip}`
**Purpose**: Backup of existing Java installation

**Format**:
- Linux/macOS: `.tar.gz` compressed archive
- Windows: `.zip` archive

**Naming**: `openjdk_backup_YYYYMMDD_HHMMSS.{tar.gz|zip}`

**Contents**: Complete JAVA_HOME directory

#### `temp/openjdk-agent-logs/run_TIMESTAMP/README.md`
**Purpose**: Run summary report

**Contents**:
- Timestamp and metadata
- Target version
- Operating system
- Run status
- Rollback instructions
- Complete action log

#### `temp/openjdk-agent-logs/run_TIMESTAMP/commands.log`
**Purpose**: Detailed execution log

**Contents**:
- All executed commands
- Command output (stdout/stderr)
- Timestamps
- Log levels (INFO, WARNING, ERROR)

## Workflow Diagrams

### Installation Workflow

```
┌─────────────────────┐
│  Parse Arguments    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Setup Logging      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Detect Java        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Backup Java        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Try Package Mgr    │
└──────────┬──────────┘
           │
           ├─Success──┐
           │          │
           ▼          │
┌─────────────────────┐│
│  Manual Install     ││
│  (Adoptium API)     ││
└──────────┬──────────┘│
           │           │
           ▼           │
┌─────────────────────┐│
│  Verify Install     │◄┘
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Health Check       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Detect Deps        │
│  (if app-path)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Upgrade Deps       │
│  (with consent)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generate Report    │
└─────────────────────┘
```

### Dependency Analysis Workflow

```
┌─────────────────────┐
│  App Path Provided? │
└──────────┬──────────┘
           │ Yes
           ▼
┌─────────────────────┐
│  Detect Platform    │
└──────────┬──────────┘
           │
     ┌─────┴─────┬─────────┐
     │           │         │
     ▼           ▼         ▼
┌────────┐  ┌────────┐  ┌────────┐
│  ldd   │  │ otool  │  │dumpbin │
│ (Linux)│  │ (macOS)│  │(Windows)│
└────┬───┘  └───┬────┘  └───┬────┘
     │          │           │
     └──────────┴───────────┘
                │
                ▼
     ┌─────────────────────┐
     │  Extract Lib Paths  │
     └──────────┬──────────┘
                │
                ▼
     ┌─────────────────────┐
     │  Resolve Packages   │
     └──────────┬──────────┘
                │
          ┌─────┴─────┬─────────┐
          │           │         │
          ▼           ▼         ▼
     ┌────────┐  ┌────────┐  ┌────────┐
     │  dpkg  │  │  brew  │  │ choco  │
     │  rpm   │  │ (Cellar)│  │(manual)│
     └────┬───┘  └───┬────┘  └───┬────┘
          │          │           │
          └──────────┴───────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  User Confirmation  │
          └──────────┬──────────┘
                     │ Yes
                     ▼
          ┌─────────────────────┐
          │  Upgrade Packages   │
          └─────────────────────┘
```

## Integration Points

### Package Managers

| Platform | Primary | Secondary | Fallback |
|----------|---------|-----------|----------|
| Linux (Debian/Ubuntu) | apt-get | dpkg | Adoptium API |
| Linux (RHEL/CentOS) | yum | rpm | Adoptium API |
| macOS | brew | - | Adoptium API |
| Windows | winget | choco | Adoptium API |

### Dependency Tools

| Platform | Detection | Resolution |
|----------|-----------|------------|
| Linux | ldd | dpkg -S / rpm -qf |
| macOS | otool -L | Cellar path parsing |
| Windows | dumpbin | Manual review |

### External APIs

- **Adoptium API**: `https://api.adoptium.net/v3/assets/latest/{version}/hotspot`
  - Used for: Downloading OpenJDK binaries when package managers fail
  - Returns: JSON with download URLs for various platforms/architectures

## Version Information

- **Agent Version**: 1.0.0
- **Python Required**: 3.x
- **Supported JDK Versions**: 8, 11, 17, 21 (any version supported by Adoptium)
- **Supported Platforms**: Linux, macOS, Windows

## Maintenance

### Adding New Platform Support

1. Update `os_type` detection in `__init__()`
2. Add platform-specific logic in:
   - `try_package_manager_install()`
   - `detect_dependencies()`
   - `resolve_packages()`
   - `upgrade_dependencies()`
3. Update documentation
4. Add tests in `test_agent.py`

### Adding New Features

1. Implement method in `OpenJDKUpgradeAgent` class
2. Update `run()` method to call new feature
3. Add command-line argument if needed
4. Update documentation
5. Add tests

## Contributing

When contributing to this project:

1. Maintain backward compatibility
2. Add tests for new features
3. Update all relevant documentation
4. Follow existing code style
5. Test on multiple platforms

## License

[Specify license here]

## Contact

[Specify contact information here]
