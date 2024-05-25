# Local Development
## Setup Instructions
1. Globally install the following software:
  - Docker
    - Use [these instructions](https://docs.docker.com/engine/install/) to install 
  - Python 3.7 or higher
2. Run the first setup script. This will create a .env file using the file .env-example as a template. 
  <br>`bash setup/1_setup_sage_directory.sh`
3. Run a setup script for setting up the virtual environment and Python dependencies.
  <br>`source setup/local_development/1_setup_venv.sh`
4. Start Docker
`docker compose -f docker-compose.dev.yml up -d`
5. Manually kick off the script to parse transactions from emails. Execute the command from the project root. For example, if the project is located in `/home/kfike/Projects/` then execute `(.venv) kfike@pop-os:~/Projects/sage$ python3 -m sage`. 


### Creating/Deleting an ephemeral server instance
1. **WARNING: RUNNING THIS SCRIPT CAUSES DIGITAL OCEAN TO START CHARGING YOU MONEY ON A MONTHLY BASIS (IF YOU DON'T DELETE THE SERVER).**
<br> Run the script to create an ephemeral Digital Ocean Droplet server that runs the application. The server is emphemeral in that it is intended to be created and deleted rapidly.
<br> `bash setup/local_development/2_create_sageEphem_server.sh`
<br> It will prompt you for `BECOME password:`; enter your sudo password.
2. Run the script to configure the server.
<br> `bash setup/local_development/3_configure_sageEphem_server.sh`
3. Run the script to delete the server.
<br> `bash server/setup_scripts/ansible_delete_droplet_ephem.sh`

### Pytest
Run the full test suite, stop after the first failure. Docker must be started for pytests to be successful.

`(venv) $ pytest -xv`


See code coverage of the tests

`(venv) $ coverage run --source=sage -m pytest -v tests/ && coverage report -m`