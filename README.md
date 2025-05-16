# Optilogic API Tests

This repository contains automated tests for the Optilogic API, specifically focused on the `database_create` functionality so far.

## Setup

1. Clone the repository
2. Create a `.env` file with your API key: OPTILOGIC_APP_KEY=op_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
3. Install dependencies: pip install -r requirements.txt

## Running Tests

Run all tests with: pytest

Tests automatically clean up any databases they create. Invalid or edge-case scenarios are also covered.

## Notes

- Ensure your API key is valid and has the correct permissions.
- Database names are generated dynamically to avoid collisions.





