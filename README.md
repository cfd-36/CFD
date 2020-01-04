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
    - how long it has been since a given person has gone over a truck
- truck_check should force the values in the OK column to be undetermined on page load.  Firefox will remember form settings, and set inputs to the last values that it saw.
- The use of timestamps needs to be rethought.  With this schema, every inspection of a piece of equipment is timestamped, so that you can tell exactly when a truck's halagan, for example, was looked at.  What this schema doesn't let you do is see that, for example, firefighter 36 went over E3 from 2 to 3 PM yesterday.  That would be more useful.  So, I think we should add an inspections table saying who went over a truck, and when they did it.  Updating the readiness of a piece of equipment would refer to that table instead of having its own timestamp.  Then, you'd be able to see that the E3 halagan was looked at between 2 and 3 PM yesterday by firefighter 36.
- truck_check should order the compartments in some reasonable order, so that it takes you in some reasonable path around the truck.  To do this, we'll need to add some ordering information somewhere.  The relative order of the compartments can inferred from their names, but the location of bottle slots can't really be inferred automatically.
