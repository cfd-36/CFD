# CFD
Carlisle, MA Fire Department equipment checks

## Getting Started

### Installation prerequisites
- Python 3
    - MySQLdb (python3-mysqldb on Debian and derivatives like Ubuntu)
- MySQL or MariaDB
    - Create a CFD user with no password and grant it all permissions on the
CFD database

			CREATE USER 'CFD'@'localhost' IDENTIFIED BY '';

			GRANT ALL ON CFD.* TO 'CFD'@'localhost';

### Setup
- Import the schema and data into the CFD database as user CFD

		mysql -D CFD -u CFD < cfd.mysqldump
- Start the HTTP server

		python3 equipment.py
- You should now be able to access the database through a Web UI locally at
http://localhost:8000.  Remote access will depend on your firewall.

## TODO
- Add a UI to import data
- Add a UI for the officers to see
    - where we have failed readiness checks and how long those checks have been failing
    - how long it has been since someone has gone over a given truck
    - how long it has been since a given person has gone over a truck
- truck_check should force the values in the OK column to be undetermined on page load.  Firefox will remember form settings, and set inputs to the last values that it saw.
