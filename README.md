# Software Security Assignment I

This repository contains a small multi-tier Booking Management System developed for Software Security Assignment I.

The system is implemented in Python and consists of three separate application services communicating over HTTP. It demonstrates authentication, authorization, protected resources, secure design principles, automated security testing, and CI/CD security gates.

## Architecture

The application consists of three separate services:

### API Service

- Runs on port `5000`
- Entry point for users
- Handles authentication and sessions
- Determines the authenticated user's identity and role
- Coordinates requests to the other services

### Resource Service

- Runs on port `5001`
- Owns the booking and summary data
- Uses SQLite for storage
- Enforces authorization on protected resources
- Performs ownership and role checks

### Processing Service

- Runs on port `5002`
- Generates booking summaries
- Communicates with the Resource Service
- Uses the separately installed `booking-helper` package

The summary workflow uses all three application components:

User
|
v
API Service
|
v
Processing Service
|
v
Resource Service
|
v
Processing Service + booking-helper
|
v
Resource Service
|
v
API Service
|
v
User

## Requirements

- Python 3.11+
- pip
- Git

Jenkins is required only for running the CI pipeline.

## Setup

Clone the repository:

git clone https://github.com/bassamsalou/software-security-assignment.git
cd software-security-assignment

Create a virtual environment.

### Windows

py -m venv .venv
.venv\Scripts\Activate.ps1

Upgrade the packaging tools:

python -m pip install --upgrade pip setuptools

Install the project dependencies:

python -m pip install -r requirements.txt

Install the custom helper package:

python -m pip install -e .\helper-package

## Seeded Data

The application uses synthetic users and booking data for the assignment.

The following synthetic accounts are available:

| Username | Password   | Role          |
| -------- | ---------- | ------------- |
| `john`   | `john123`  | User          |
| `doe`    | `doe123`   | User          |
| `admin`  | `admin123` | Administrator |

These credentials are intentionally hardcoded synthetic test accounts for the local assignment environment. They are not production credentials.

Example seeded bookings include bookings owned by John and Doe.

No registration process is required.

### Seeding the Database

No separate seed command is required. The Resource Service automatically creates and seeds the SQLite database when it is started:

python .\resource-service\app.py

This initializes the local database with the synthetic booking data used by the assignment.

## Running the Application

The three services run as separate processes.

Open three terminals from the repository root.

### Terminal 1 — Resource Service

Activate the virtual environment if necessary:

.venv\Scripts\Activate.ps1

Then run:

python .\resource-service\app.py

Runs at:

http://127.0.0.1:5001

### Terminal 2 — Processing Service

Activate the virtual environment if necessary:

.venv\Scripts\Activate.ps1

Then run:

python .\processing-service\app.py

Runs at:

http://127.0.0.1:5002

### Terminal 3 — API Service

Activate the virtual environment if necessary:

.venv\Scripts\Activate.ps1

Then run:

python .\api-service\app.py

Runs at:

http://127.0.0.1:5000

## Running Automated Tests

### API, Resource and Authorization Tests

python -m pytest tests/test_api.py tests/test_resource.py -v

Expected result:

21 passed

### Integration Tests

The integration test suite automatically starts and stops all three application services. The services therefore do not need to be started manually before running this command.

python -m pytest tests/test_integration.py -v

Expected result:

8 passed

The project currently contains 29 automated tests across these test suites.

To run the complete test suite:

python -m pytest tests/test_api.py tests/test_resource.py tests/test_integration.py -v

Expected result:

29 passed

## Static Security Analysis

Bandit is used for static security analysis.

Run the full analysis:

python -m bandit -r api-service resource-service processing-service helper-package

The current implementation contains three Low severity findings caused by the intentionally hardcoded synthetic passwords used for seeded assignment accounts.

The CI security gate checks Medium and High severity findings with:

python -m bandit -r api-service resource-service processing-service helper-package -ll

A Medium or High severity finding causes the Jenkins security stage to fail.

## Dependency Security Analysis

Dependency vulnerabilities are checked using `pip-audit`:

python -m pip_audit

The current dependency audit reports no known vulnerabilities.

The local `booking-helper` package may be reported as skipped because it is a local project package and is not available on PyPI.

## Security Model

The system has two authorization roles:

- `User`
- `Administrator`

Ordinary users may access their own protected resources but may not access resources belonging to another user.

Administrators may access and manage bookings belonging to users.

Authorization is enforced by the Resource Service at the protected resource boundary rather than relying only on decisions made by upstream services.

The implementation applies three secure design principles:

- Least privilege
- Complete mediation
- Fail-safe defaults

## Security Vulnerability Investigations

Four intentional security issues were investigated during development.

### CWE-862 — Missing Authorization

A protected operation was intentionally implemented without the required authorization check. The vulnerability was demonstrated and then fixed by enforcing authorization at the protected resource boundary.

### CWE-89 — SQL Injection

A booking search operation was intentionally implemented using unsafe SQL construction. The vulnerability was demonstrated and fixed using parameterized SQL queries.

### CWE-20 — Improper Input Validation

Booking status modification was intentionally implemented without sufficient validation. The vulnerability was demonstrated and fixed using explicit validation and an allowlist of permitted status values.

### Composition Vulnerability — Stale Authorization

The multi-service summary workflow intentionally demonstrated a stale-authorization problem.

A user could initially be authorized for a booking, after which the booking ownership could change before a protected write occurred. The vulnerable implementation trusted previously obtained ownership information.

The fix applies complete mediation. The Resource Service re-fetches the current booking state and revalidates ownership at the protected write boundary before storing the summary.

Regression tests verify the fixes.

## Jenkins CI Pipeline

The repository contains a `Jenkinsfile` defining the CI security pipeline.

The pipeline performs:

1. Environment validation
2. Creation of a fresh Python virtual environment
3. Dependency installation
4. Separate installation of `booking-helper`
5. Python build/compilation validation
6. API, resource and authorization tests
7. Three-service integration tests
8. Bandit static security analysis
9. `pip-audit` dependency analysis
10. Test-result recording
11. Security and test artifact archiving

The current pipeline executes all 29 automated tests.

Jenkins is configured using SCM polling to automatically detect changes pushed to the configured repository branch and start the pipeline.

### Security Gates

The build is blocked when:

- Environment/build validation fails
- Any automated test fails
- Bandit identifies a Medium or High severity issue
- `pip-audit` identifies a known vulnerable dependency

Low severity Bandit findings are recorded but do not block the build.

## CI Evidence

Jenkins generates and archives the following evidence:

artifacts/unit-tests.xml
artifacts/integration-tests.xml
artifacts/bandit-report.json
artifacts/pip-audit-report.json

JUnit test results are also recorded by Jenkins.

## Project Structure

software-security-assignment/
|
|-- api-service/
| `-- app.py
|
|-- resource-service/
|   |-- app.py
|   `-- database.py
|
|-- processing-service/
| `-- app.py
|
|-- helper-package/
|   |-- booking_helper/
|   `-- pyproject.toml
|
|-- tests/
| |-- test_api.py
| |-- test_resource.py
| `-- test_integration.py
|
|-- security/
|-- artifacts/
|-- documentation/
|
|-- Jenkinsfile
|-- requirements.txt
|-- README.md
`-- .gitignore

## Documentation

Security planning and design documentation is stored in the `documentation` directory.

This includes the initial Security Lifecycle Plan covering:

- Requirements and scope
- Asset register
- Architecture and trust boundaries
- Access-control matrix
- STRIDE threat analysis
- Secure design principles
- Implementation and build activities
- Testing and CI activities
- Release and deployment considerations

The final assignment report describes the implemented architecture, security decisions, vulnerability investigations, testing, CI/CD pipeline, evidence, and production considerations.

## Scope

This project is intended for local educational use.

The project deliberately uses:

- Synthetic users
- Synthetic booking data
- Local SQLite storage
- Local HTTP services
- Command-line/API interaction

Production concerns such as public hosting, registration, payment processing, email delivery, high availability, and large-scale deployment are outside the scope of the assignment.

The optional supply-chain attack experiment was not attempted.
