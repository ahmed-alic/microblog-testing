# Microblog Testing Project

## Original Source Attribution

This project is based on Miguel Grinberg's [Microblog Flask application](https://github.com/miguelgrinberg/microblog), featured in his [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world). The original code is © 2017-2024 Miguel Grinberg and is licensed under the [MIT License](LICENSE).

## Project Overview

This repository contains the Microblog Flask application with an enhanced, comprehensive test suite developed as part of a Software Verification, Validation, and Testing course project. The test suite demonstrates various testing techniques and achieves 91% code coverage across the application.

## Deployed Application

[Live Application URL](https://microblog-testing.onrender.com) 

### Deployment Information

The application is deployed on Render.com using Docker containerization.

### Live Application

The application is live at [https://microblog-testing.onrender.com](https://microblog-testing.onrender.com)

### Deployment Configuration

The deployment uses a Docker-based approach with the following configuration:

1. **Dockerfile**: Uses Python 3.9 and installs necessary build dependencies for C extensions
2. **Environment Variables**:
   - `FLASK_APP`: Set to `microblog.py`
   - `SECRET_KEY`: Randomly generated for security
   - `DATABASE_URL`: Database connection string (SQLite is used by default)

### Deployment Challenges

Several challenges were encountered during deployment:

1. **Python Version Compatibility**: Python 3.13 (Render's default) has compatibility issues with greenlet and SQLAlchemy
2. **C Extensions**: Packages like greenlet and psycopg2-binary require specific system dependencies
3. **Docker Solution**: The final solution uses Docker with Python 3.9 and necessary build tools

This approach successfully resolves the compatibility issues and provides a stable deployment environment.

## Testing Strategy

This project implements a comprehensive testing approach incorporating industry-standard verification, validation, and testing techniques:

1. **Unit Tests**: Testing individual components in isolation
   - Located in `tests/unit/`
   - Focus on models, utilities, and helper functions
   - Uses pytest fixtures for test isolation

2. **Integration Tests**: Testing interactions between multiple components
   - Located in `tests/integration/`
   - Tests API endpoints, authentication flows, and database interactions
   - Uses Flask test client to simulate HTTP requests

3. **System Tests**: End-to-end testing of complete user flows
   - Located in `tests/system/`
   - Tests complete user journeys like registration, posting, and following
   - Validates the application as a cohesive system

4. **Static Analysis**: Code quality and security verification
   - Located in `tests/static_analysis/`
   - Uses multiple tools:
     - Flake8: Python style guide enforcement
     - Bandit: Security vulnerability detection
     - Radon: Code complexity analysis

### Test Design Techniques

The test suite employs several test design techniques:

- **Boundary Value Analysis**: Testing at input boundaries (e.g., password length limits)
- **Equivalence Partitioning**: Testing representative values from input classes
- **State Transition Testing**: Validating behavior as system changes states
- **Decision Table Testing**: Testing different input combinations

For detailed information on test design, see [TEST_PLAN.md](TEST_PLAN.md).

### Regression Testing

A robust regression testing strategy ensures that new changes don't break existing functionality. The process includes:

- Automated test runs after code changes
- CI/CD integration for continuous testing
- Specific test paths for targeted regression testing

For detailed information on regression testing, see [REGRESSION_TESTING.md](REGRESSION_TESTING.md).

### Test Coverage

The test suite achieves **91% code coverage** across the application, with many modules reaching 100% coverage.

- HTML coverage reports are generated in the `htmlcov` directory
- Coverage is measured using pytest-cov
- Areas needing coverage improvement are documented

For detailed coverage analysis, see [COVERAGE_REPORT.md](COVERAGE_REPORT.md).

### Security Analysis

Security testing using Bandit has identified several potential vulnerabilities and recommendations:

- Command injection risks in CLI commands
- Use of weak cryptographic hash functions
- Missing timeouts in network requests

For detailed security findings, see [security_report.md](security_report.md).

Key testing features:
- Test isolation using SQLite in-memory and temporary file databases
- Fixture-based test setup and teardown
- Mocking of external services
- Transaction-based database cleanup
- Comprehensive assertion strategies

## Test Coverage

Overall test coverage: **91%**

Highlights:
- 100% coverage of tasks.py, email.py, search.py, translate.py, and more
- Robust system tests for critical user flows (authentication, following, posts)
- Error handling and edge cases thoroughly tested

## Installation and Setup

### Prerequisites

- Python 3.6+
- pip package manager

### Setup Instructions

1. Clone this repository:
   ```
   git clone https://github.com/ahmed-alic/microblog-testing.git
   cd microblog-testing
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # For testing dependencies
   ```

4. Set environment variables:
   ```
   # On Linux/Mac
   export FLASK_APP=microblog.py
   
   # On Windows
   set FLASK_APP=microblog.py
   ```

5. Initialize the database:
   ```
   flask db upgrade
   ```

## Running the Application

```
flask run
```

Visit `http://localhost:5000` in your web browser.

## Running Tests

```
pytest        # Run all tests
pytest -v     # Verbose output
pytest --cov=app  # Generate coverage report
```

## Test Documentation

Detailed documentation of the testing approach, test cases, and results can be found in the [docs](docs/) directory.

## GitHub Features

This project demonstrates proper use of GitHub for software testing and quality assurance:

- **Issue Templates**: Standardized templates for [bug reports](.github/ISSUE_TEMPLATE/bug_report.md) and [test cases](.github/ISSUE_TEMPLATE/test_case.md)
- **Continuous Integration**: Automated test runs via [GitHub Actions](.github/workflows/run-tests.yml) on every push
- **Pull Request Template**: Enforces quality standards for code contributions using our [PR template](.github/pull_request_template.md)
- **GitHub Pages**: Test documentation published at [project pages site](https://ahmed-alic.github.io/microblog-testing/) (activate in repository settings)
- **Issues and Project Board**: Track testing progress through categorized and labeled issues
- **Branch Strategy**: Feature branches for different test categories merged via pull requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Original code © 2017-2024 Miguel Grinberg. Test suite and modifications © 2025 Ahmed Alic.
