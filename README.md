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
- Import the schema and data

		mysql < cfd.mysqldump
- Start the HTTP server

		python3 equipment.py
- You should now be able to access the database through a Web UI locally at
http://localhost:8000.  Remote access will depend on your firewall.
