# Microblog Testing Project

## Original Source Attribution

This project is based on Miguel Grinberg's [Microblog Flask application](https://github.com/miguelgrinberg/microblog), featured in his [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world). The original code is © 2017-2024 Miguel Grinberg and is licensed under the [MIT License](LICENSE).

## Project Overview

This repository contains the Microblog Flask application with an enhanced, comprehensive test suite developed as part of a Software Verification, Validation, and Testing course project. The test suite demonstrates various testing techniques and achieves 91% code coverage across the application.

### Application Features

The Microblog application is a Twitter-like social platform with the following key features:

* **User Authentication**: Registration, login, password reset functionality
* **User Profiles**: Customizable profiles with avatars and about-me sections
* **Posts**: Users can create, view, and browse text posts
* **Social Network**: Follow/unfollow users, personalized timelines
* **Private Messaging**: Direct messaging between users
* **Notifications**: Real-time notification system for messages
* **Search**: Full-text search functionality
* **API**: RESTful API for programmatic access
* **Internationalization**: Multi-language support
* **Export**: Data export capabilities

## Deployed Application

[Live Application URL](https://microblog-testing.onrender.com) 

### Deployment Information

The application is deployed on Render.com using Docker containerization.

### Live Application

The application is live at [https://microblog-testing.onrender.com](https://microblog-testing.onrender.com)

Defaulted login credentials:
* Username: `demo`
* Password: `demo1234`

### Deployment Configuration

The deployment uses a Docker-based approach with the following configuration:

1. **Dockerfile**: Uses Python 3.9 and installs necessary build dependencies for C extensions
2. **Environment Variables**:
   - `FLASK_APP`: Set to `microblog.py`
   - `SECRET_KEY`: Randomly generated for security
   - `DATABASE_URL`: Database connection string (SQLite is used by default)
3. **Persistent Storage**:
   - Docker volume mounted at `/data` for database persistence
   - SQLite database stored at `/data/app.db`
   - Note: On free tier services, data may not persist during extended inactive periods

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

Detailed test design information is available in the project report document.

### Regression Testing

A robust regression testing strategy ensures that new changes don't break existing functionality. The process includes:

- Automated test runs after code changes
- CI/CD integration for continuous testing
- Specific test paths for targeted regression testing

Regression tests are consolidated in `tests/test_core_regression.py` for comprehensive verification.

### Test Coverage

The test suite achieves **91% code coverage** across the application, with many modules reaching 100% coverage.

- HTML coverage reports are generated in the `htmlcov` directory
- Coverage is measured using pytest-cov
- Areas needing coverage improvement are documented in the project report

### Security Analysis

Security testing using Bandit has identified several potential vulnerabilities and recommendations:

- Command injection risks in CLI commands
- Use of weak cryptographic hash functions
- Missing timeouts in network requests

These findings are addressed in the project's comprehensive test documentation.

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
- Tests are categorized into unit, integration, system, and static analysis types

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
# Run all tests
pytest

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov=app

# Run specific test categories
.\venv\Scripts\python -m pytest tests\unit -v
.\venv\Scripts\python -m pytest tests\integration -v
.\venv\Scripts\python -m pytest tests\system -v
.\venv\Scripts\python -m pytest tests\static_analysis -v
```

### Test Database Configuration

Tests use isolated databases to prevent interference with production data:
- Unit tests: SQLite in-memory database (`sqlite:///:memory:`) 
- Integration tests: Temporary file-based SQLite database
- System tests: Temporary file-based SQLite database

## Test Documentation

Detailed documentation of the testing approach, test cases, and results can be found in the comprehensive PROJECT_REPORT_WITH_APPENDIX.md file.

## Troubleshooting

### Common Issues

1. **Database Persistence on Render Free Tier**:
   - Free tier services may lose data after inactivity periods
   - Solution: Upgrade to paid tier or use external database service

2. **SQLAlchemy Errors with Python 3.13**:
   - Some SQLAlchemy versions have compatibility issues with Python 3.13
   - Solution: Use Python 3.9 as specified in the Dockerfile

3. **Missing Flake8**:
   - Static analysis tests may fail if flake8 is not installed
   - Solution: `pip install -r requirements-test.txt`

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
