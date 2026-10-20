# Software Security Assignment I

## Booking Management System — Requirements

### 1. Purpose

The application manages bookings for multiple users.
It demonstrates how a multi-component application can
provide useful functionality while protecting resources
owned by different users.

The application uses synthetic data and three separate
services that communicate through HTTP APIs.

### 2. Users and Roles

- Alice: ordinary user who owns her own bookings.
- Bob: ordinary user who owns his own bookings.
- Admin: privileged user who can manage bookings
  according to the access-control policy.

### 3. Functional Requirements

FR1: Users can authenticate using valid credentials.

FR2: An authenticated user can view their own bookings.

FR3: An authenticated user can request a booking summary.

FR4: An administrator can view and manage bookings
according to the defined access-control policy.

FR5: The application can generate a booking summary
using the processing service and helper package.

### 4. Security Requirements

SEC1: Every protected operation requires authentication.

SEC2: Ordinary users cannot access another user's bookings.

SEC3: Administrator-only actions are restricted to
authorized administrators.

SEC4: The resource service enforces permissions on
the resources it owns.

SEC5: Each component receives only the permissions
necessary for its responsibilities.

SEC6: Missing, invalid or insufficient authorization
results in access being denied.

SEC7: The application validates input and handles errors
without exposing sensitive information.

SEC8: The application documents and tests at least three
intentionally planted vulnerabilities from the course
catalog and one additional composition vulnerability.

### 5. Non-Functional Requirements

NFR1: The three application components run as separate
processes and communicate through explicit interfaces.

NFR2: The application can be built and tested locally.

NFR3: Functional and security tests are automated.

NFR4: Jenkins runs the required build, analysis and tests
on pushes and pull requests.

NFR5: Test and analysis results are saved as artifacts.

NFR6: The project includes documentation and reproducible
commands for setup, seeding, execution and testing.

### 6. Initial Scope

The application uses synthetic booking data.

User registration, real payments, email delivery, public
hosting and a graphical user interface are not required.

The application will use Python and HTTP APIs.

### 7. Initial Security Principles

- Least privilege.
- Complete mediation.
- Fail-safe defaults.

Each principle will be connected to an implementation
decision and supporting test evidence.
