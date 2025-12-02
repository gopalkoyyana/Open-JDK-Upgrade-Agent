# Contributing to OpenJDK Upgrade Agent

Thank you for your interest in contributing to the OpenJDK Upgrade Agent! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, Java version)
- Relevant log files from `temp/openjdk-agent-logs/`

### Suggesting Features

Feature requests are welcome! Please create an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternative solutions you've considered
- How this benefits other users

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   python test_agent.py
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Testing

- All new features must include tests
- Ensure all existing tests pass
- Test on multiple platforms when possible

### Documentation

Update relevant documentation files:
- `README.md` - User-facing changes
- `EXAMPLES.md` - New usage examples
- `DEVELOPMENT.md` - Technical changes
- Code comments - Complex logic

### Platform Support

When adding platform-specific code:
- Test on the target platform
- Add fallback behavior when possible
- Update platform support matrix in documentation
- Consider edge cases

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

## Questions?

Feel free to open an issue for any questions about contributing!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
