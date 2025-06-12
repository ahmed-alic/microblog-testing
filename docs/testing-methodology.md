# Testing Methodology

This document outlines the comprehensive testing approach used for the Microblog application.

## Testing Layers

### Unit Testing
Unit tests focus on testing individual components in isolation, mocking dependencies where necessary. These tests verify that each function or method performs its expected behavior correctly.

Examples:
- User model password hashing functions
- Email formatting functions
- Search functionality
- Translation services

### Integration Testing
Integration tests verify that different components work together correctly. These tests focus on the interactions between multiple units, such as:

- API endpoints and database models
- Authentication flows
- Form submissions and route handlers

### System Testing
System tests validate end-to-end functionality from a user's perspective. These tests simulate user interactions and verify that complete workflows function correctly:

- User registration and login
- Password reset flow
- Follow/unfollow user functionality
- Timeline content generation

## Test Database Strategy

One of the key challenges in testing the Microblog application was establishing proper database isolation between tests. Our approach includes:

1. **Separate Test Configuration**: Using a dedicated TestConfig class that inherits from the application's Config
2. **Temporary SQLite Databases**: Using in-memory SQLite databases for unit/integration tests and temporary file databases for system tests
3. **Complete Schema Creation**: Ensuring all tables are created before tests run with `db.create_all()`
4. **Transaction Management**: Using SQLAlchemy transactions for test isolation
5. **Proper Relationship Cleanup**: Using direct SQL commands to clean up relationships before deleting users
6. **Connection Disposal**: Explicitly closing database connections to prevent resource leaks

## Key Test Design Patterns

### Fixtures
We use pytest fixtures extensively to set up test environments with the right level of isolation:

- Module-scoped fixtures for system tests
- Function-scoped fixtures for unit tests
- Parametrized fixtures for testing multiple scenarios

### Mocking and Patching
External services like email sending and translation are mocked to ensure tests are:
- Fast
- Deterministic
- Independent of external services

### Assertions
We employ various assertion strategies:
- Direct database state verification
- Response code checking
- HTML content verification using string matching
- JSON response validation

## Test Coverage Strategy

We follow these principles to maximize test coverage:
1. Focus on critical user paths first
2. Test edge cases thoroughly
3. Include error handling scenarios
4. Test both positive and negative cases

The final test suite achieves 91% coverage across the application code, with many modules reaching 100% coverage.
