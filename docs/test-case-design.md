# Test Case Design

This document outlines the test case design techniques used for the Microblog application.

## Boundary Value Analysis

Boundary value analysis was used for testing input validation, particularly in form submissions:

| Test Case ID | Field | Boundary Values Tested |
|-------------|-------|------------------------|
| TC-BVA-01 | Username Length | Empty, 1 char (min), 64 chars (max), 65 chars (max+1) |
| TC-BVA-02 | Password Length | Empty, 7 chars (min-1), 8 chars (min), 128 chars |
| TC-BVA-03 | Post Content | Empty, 1 char (min), 140 chars (max), 141 chars (max+1) |

## Equivalence Partitioning

Equivalence classes were identified for user authentication and post creation:

### User Authentication
| Equivalence Class | Representative Values | Expected Behavior |
|------------------|---------------------|-------------------|
| Valid credentials | Username: "john", Password: "correctpass" | Successful login |
| Invalid username | Username: "nonexistent", Password: any | Failed login with appropriate message |
| Invalid password | Username: "john", Password: "wrongpass" | Failed login with appropriate message |
| Empty credentials | Username: "", Password: "" | Validation error messages |

### Post Creation
| Equivalence Class | Representative Values | Expected Behavior |
|------------------|---------------------|-------------------|
| Valid posts | 1-140 characters | Post created, redirected to timeline |
| Empty posts | Empty string | Validation error message |
| Oversized posts | > 140 characters | Validation error message |
| Posts with special characters | Posts with HTML, JavaScript, etc. | Post created with proper escaping |

## Decision Table Testing

Decision table testing was applied to test the follow/unfollow functionality:

| Test Case | User Logged In | Target User Exists | Self-Follow | Expected Outcome |
|-----------|--------------|------------------|-----------|----------------|
| TC-DT-01 | Yes | Yes | No | Follow/Unfollow successful |
| TC-DT-02 | Yes | No | N/A | 404 Not Found |
| TC-DT-03 | No | Yes | N/A | Redirect to login |
| TC-DT-04 | Yes | Yes | Yes | Self-follow prevented |

## State Transition Testing

State transition testing was used for the password reset flow:

| Current State | Event | Next State | Test Case |
|--------------|-------|-----------|-----------|
| Logged out | Request password reset | Reset email sent | TC-ST-01 |
| Reset email sent | Click valid reset link | Reset form displayed | TC-ST-02 |
| Reset email sent | Click expired reset link | Error message | TC-ST-03 |
| Reset form displayed | Submit valid new password | Password changed | TC-ST-04 |
| Reset form displayed | Submit invalid new password | Validation error | TC-ST-05 |

## Code Path Coverage

Code path coverage analysis guided our testing of complex functions, such as the search functionality:

| Test Case ID | Function | Path Description | Coverage |
|-------------|---------|------------------|----------|
| TC-CP-01 | User.search | Index exists, matches found | Covered |
| TC-CP-02 | User.search | Index exists, no matches | Covered |
| TC-CP-03 | User.search | Index missing | Covered |
| TC-CP-04 | Post.search | Search all available fields | Covered |

This structured approach to test case design helped ensure comprehensive coverage of the application's functionality and edge cases.
