# Contributing to AI-Financial-Agent

Thank you for your interest in contributing to the AI-Financial-Agent project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community respectful and inclusive.

## How Can I Contribute?

### Reporting Bugs

- Use the issue tracker to report bugs
- Describe the bug and include specific details to help us reproduce the problem
- Include the steps that you used when you found the bug
- Include any error logs or screenshots

### Suggesting Enhancements

- Use the issue tracker to suggest enhancements
- Provide a clear description of the enhancement
- Explain why this enhancement would be useful to most users
- Include mock-ups if applicable

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`python -m pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

Follow the setup instructions in the README.md to configure your development environment.

## Coding Guidelines

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Add type hints to function parameters and return values
- Write docstrings for all functions, classes, and modules

Example:
```python
def reconcile_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconcile a payment against invoices.
    
    Args:
        payment_data: Dictionary containing payment details
        
    Returns:
        Dictionary with reconciliation results
    """
    # Function implementation
```

### Testing

- Write unit tests for all new code
- Maintain or increase the code coverage percentage
- Run tests before submitting pull requests

### Documentation

- Update documentation when you change code functionality
- Write clear commit messages explaining the changes

## Release Process

1. Version bump following [Semantic Versioning](https://semver.org/)
2. Update CHANGELOG.md with the changes
3. Create a release tag
4. Push to GitHub

## Questions?

If you have any questions, please reach out to the maintainers:

- Project Lead: [Your Name](mailto:your.email@example.com)
- Lead Developer: [Developer Name](mailto:developer.email@example.com)

Thank you for contributing to AI-Financial-Agent!
