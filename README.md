# Fit-Out Manager

Local operational demonstration based on the UAE Paint and Fit Out PRD. Requires Python 3.12 or later; no packages or external services required.

Run `python app.py` from this directory. The local server listens on port 8000. SQLite data persists in `fitout.sqlite3` (ignored by Git). Override the database with `FITOUT_DB` and port with `PORT`.

Run tests with `python -m unittest discover -s tests -v`.

Includes three sample companies, customer/project/purchase/draft quotation records, the PRD paint-demand calculator, stock receipts/consumption with negative-stock prevention, and duplicate-safe site reports. Company selection filters views; it is not an authorization boundary.

This is a demonstration, not a production ERP. Authentication, server-enforced company permissions, document approvals, full BOQs, inventory locations/reservations/batches, finance, payroll, offline sync, Arabic, migration and deployment remain future work. Do not enter confidential or real business information. Site reports do not represent accepted or billable progress. Incoming supply in the calculator is manually entered, not allocated by the procurement system.

## Public demo on Render

The included `render.yaml` defines a Docker web service with a health check. In Render, choose New → Blueprint, connect this GitHub repository, and deploy the blueprint. No secrets or build commands are required. Review the selected free plan before creating the service; hosting availability and terms depend on Render.

Public visitors share the demonstration database and can add sample records. The database on this configuration is ephemeral: data can reset when the service restarts or redeploys. Do not enter real company, customer, employee, or bank data. For local testing of the hosting configuration, set HOST=0.0.0.0 and PORT to the selected port before running `python app.py`.
