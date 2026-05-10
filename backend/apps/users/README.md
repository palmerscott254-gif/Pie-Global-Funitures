Management commands and utilities for the `users` app.

create_dashboard_admin
- Purpose: create a dashboard/admin user record in the custom `User` table.
- Usage:
```bash
python3 backend/manage.py create_dashboard_admin --email admin@example.com --name "Dashboard Admin" [--password PASSWORD]
```
- Notes:
  - If `--password` is omitted a secure 12-character password will be generated and printed.
  - The command sets `is_staff=True` and `is_superuser=True` on the created user.
  - Ensure your virtualenv is active and migrations have been applied before running.
