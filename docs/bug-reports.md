# Bug Reports and Fixes

This document details the bugs identified during testing and the fixes implemented.

## Bug 1: SQLAlchemy WriteOnlyMapped Relationship Teardown Error

**Description**: System tests were failing with SQLAlchemy InvalidRequestError related to WriteOnlyMapped relationships during test teardown.

**Root Cause**: SQLAlchemy ORM doesn't support iteration over WriteOnlyMapped collections during instance deletion, causing errors when User objects with relationships were being deleted in test teardown.

**Test that Exposed the Bug**:
- `test_follow_timeline_flow.py` - Follow/unfollow system test

**Fix Implemented**:
- Used direct SQL DELETE statements to clean up relationships before deleting user objects
- Implemented explicit disposal of SQLAlchemy engine connections before file deletion
- Added transaction-based isolation for test database operations

**Commit Link**: [Fix SQLAlchemy WriteOnlyMapped relationship teardown errors](#)

## Bug 2: Windows-Specific File Lock Issues

**Description**: On Windows, tests were failing with "PermissionError: The process cannot access the file because it is being used by another process" when trying to delete temporary database files.

**Root Cause**: SQLAlchemy connections to the database file were not being properly closed before attempting to delete the file, a particularly problematic issue on Windows.

**Test that Exposed the Bug**:
- Multiple system tests using temporary file databases

**Fix Implemented**:
- Added explicit connection disposal with `db.engine.dispose()`
- Implemented try-except block for file deletion to gracefully handle potential permission errors
- Added proper cleanup sequence to ensure connections are closed before file operations

**Commit Link**: [Fix Windows file lock issues in test teardown](#)

## Bug 3: Nested App Context Issues

**Description**: Tests were failing with "RuntimeError: Working outside of application context" or "AssertionError: Popped wrong app context" errors.

**Root Cause**: When fixtures or tests create nested Flask application contexts incorrectly, it causes conflicts during context cleanup.

**Test that Exposed the Bug**:
- Various integration tests

**Fix Implemented**:
- Restructured fixtures to avoid creating nested app contexts
- Used app_context() as a context manager consistently
- Ensured each test has the proper scope of fixtures to avoid context conflicts

**Commit Link**: [Fix app context management in tests](#)

## Bug 4: Test Database Schema Initialization Issues

**Description**: Tests were failing with SQLAlchemy errors related to missing tables in the test database.

**Root Cause**: The test configuration wasn't properly ensuring that database tables were created before tests ran.

**Test that Exposed the Bug**:
- System tests requiring a fully initialized database

**Fix Implemented**:
- Created a TestConfig class that properly inherits from the app's Config
- Added explicit `db.create_all()` calls within app contexts in fixtures
- Ensured each test suite had proper database initialization before tests ran

**Commit Link**: [Fix test database initialization](#)

## Bug 5: Follow Count Display Issues

**Description**: Assertions for follower/following counts were brittle and failing due to HTML structure changes.

**Root Cause**: Tests were using overly specific HTML string matching that was sensitive to whitespace and markup changes.

**Test that Exposed the Bug**:
- `test_follow_count_display` in system tests

**Fix Implemented**:
- Implemented more flexible HTML content checking
- Used case-insensitive substring matching instead of exact matching
- Added more robust assertions that focused on semantic content rather than specific markup

**Commit Link**: [Improve HTML assertions in follow tests](#)
