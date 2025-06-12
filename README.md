# Microblog Testing Project

## Original Source Attribution

This project is based on Miguel Grinberg's [Microblog Flask application](https://github.com/miguelgrinberg/microblog), featured in his [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world). The original code is © 2017-2024 Miguel Grinberg and is licensed under the [MIT License](LICENSE).

## Project Overview

This repository contains the Microblog Flask application with an enhanced, comprehensive test suite developed as part of a Software Verification, Validation, and Testing course project. The test suite demonstrates various testing techniques and achieves 91% code coverage across the application.

## Deployed Application

[Live Application URL] - *Coming soon*

## Testing Strategy

This project implements a multi-layered testing approach:

1. **Unit Tests**: Testing individual components in isolation
2. **Integration Tests**: Testing interactions between multiple components
3. **System Tests**: End-to-end testing of complete user flows
4. **Static Analysis**: Using flake8 to identify potential code quality issues

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Original code © 2017-2024 Miguel Grinberg. Test suite and modifications © 2025 Ahmed Alic.
