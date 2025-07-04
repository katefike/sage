# sage

This app is like Mint, but ~~better~~ actually exists. It privately collects your personal financial data: no one but you can access it. The data is collected from alert emails sent from your financial institutions. The bank alert emails can be directed to your personal email account, such as a Gmail account. Then setup your account to forward the alert emails to your own self-hosted mailserver (MX). The financial data in the emails is extracted, stored, and made viewable to you and you only. 

Thank you @nhopkinson and @whosgonna for their ongoing feedback on this project.

## Abbreviations
- MSG = message
- TXN = transaction
- UID = unique identifier
- STMT = SQL statement
- MX = mailserver
- DB = database

## Production Setup Instructions
*This app is mostly production ready! Enjoy!*

1. Globally install the following software:
  <br> Python 3.7 or higher
  <br> bash
2. Run the first setup script. This will create a .env file using the file .env-example as a template. 
  <br>`bash setup/1_setup_sage_directory.sh`
3. Define the following environment variables in the .env file:
  <br> `DOMAIN`: Buy a domain name.
  <br> `FORWARDING_EMAIL`: Set up the email account that receives the transaction alert emails. This account needs to forward all emails to the receiving email address on the MX. The default receiving email address is incoming@DOMAIN. So if you purchased the domain localhost, the receiving email address would me incoming@localhost
  <br> `RECEIVING_EMAIL_PASSWORD`: The password for the MX account that receives transaction emails. The password is used to access the emails programatically (imap).
  <br> `DO_API_TOKEN`: Create a Digital Ocean API Key. It's located in the "API" portion of their menu.
  <br> `PROD_SSH_PUBLIC_KEY`: Create SSH keys for you to SSH to the production server. Ensure the private key permissions are restricted.For help see the section "Production Setup Troubleshooting." Copy/paste the public key here.
  <br> `PROD_SSH_PRIVATE_KEY_FILE_PATH`: Copy/paste the path to the private key file here.
  <br> `SERVER_USER`: Your user the production server.
  <br> `SERVER_USER_PASSWORD`: Your user's password on the production server.
  <br> `SSH_ALLOWED_PUBLIC_IPS`: List the public IPs that can access to the production server.
  <br> `POSTGRES_PASSWORD`: admin role's password.
  <br> `POSTGRES_ETL_PASSWORD`: etl role's password.
  <br> `POSTGRES_GRAFANA_PASSWORD`: grafanareader role's password
  <br> `POSTGRES_GRAFANA_SSL_MODE`: Change this to "enable".
  <br> `GRAFANA_PASSWORD`: Grafana admin user's password.
4. Define the banks you will be paring data from in the banks_config.yml file.
5. **WARNING: RUNNING THIS SCRIPT CAUSES DIGITAL OCEAN TO START CHARGING YOU MONEY ON A MONTHLY BASIS FOR YOUR PRODUCTION SERVER.**
  <br> Run the script to create a production Digital Ocean Droplet server that runs the application.
  <br> `bash setup/2_create_prod_server.sh`
  <br> If an error occurs, go to Digital Ocean and delete the Droplet and firewall before running the script again.
  <br> It will prompt you for `BECOME password:`; enter your sudo password.
6. Run the script to configure the production Digital Ocean Droplet server.
  <br> `bash setup/3_configure_prod_server.sh`
  <br> This script is idempotent: no matter how many times you run it, the result will be the same. So if an error occurs, simply troubleshoot and run the script again until the error is resolved.
7. **WARNING: CREATING DIGITAL OCEAN VOLUMES ALSO COST MONEY, BUT     THEY'RE HELPFUL FOR DISASTER RECOVERY. AT THIS TIME, THE VOLUMES ARE NOT OPTIONAL FOR THE DEPLOYMENT.** In the Digital Ocean console, go to the "Volumes Block Storage" tab and create two volumes: `sage-db` and `sage-mx`.
8. In the Digital Ocean console, attach each volume to the Droplet. SSH to the Droplet and run the commands Digital Ocean provides to mount each volume.
9. In the Digital Ocean console, create the NS records for the domain name you purchased, corresponding to `$DOMAIN` in the `.env`.
10. In the Digital Ocean console, create an A record for the Droplet using "prod.< $DOMAIN >" as the hostname. For example, if `$DOMAIN` is example.com, then the hostname is prod.example.com. Use the floating IP as the value.
11. In the Digital Ocean console, create a MX record for the Droplet using $DOMAIN as the hostname. For example, if `$DOMAIN` is example.com, then the hostname is prod.example.com.
12. Re-run `bash setup/3_configure_prod_server.sh` to deploy Sage using the mounted volumes. 
  <br> TODO: Create and mount Digital Ocean volumes during automated production deployment https://github.com/katefike/sage/issues/145
13. Go to the Grafana login URL https://prod.< $DOMAIN >. For example, my $DOMAIN is example.com, so the URL is https://prod.example.com. At this URL, you should see "Welcome to Grafana" with a login prompt.

## Additional Documentation
All additional documentation can be found in the `docs/` directory.
- [Local Development](docs/local_development.md): Provides local development setup instructions, how to create an ephemeral version of Sage for deployment testing (this part costs money), and using Pytest.
- [Local Architecture .drawio Diagram](docs/local_architecture.drawio)
- [Prod Architecture .drawio Diagram](docs/prod_architecture.drawio)
- [Disaster Recovery](docs/disaster_rcovery.md): Provides disaster recovery instructions. This is helpful for when something is deeply wrong with your current Sage deployment, but you have data in the MX and/or DB that you don't want to lose. The guide describes how to create a brand new Sage deployment and attach your existing data to it.
- [Troubleshooting](docs/troubleshooting.md): Provides troubleshooting advice applicable in both local and prod. If you don't see what you're looking for, it may be in the env specific [local troubleshooting](docs/local_troubleshooting.md) or [prod troubleshooting](docs/prod_troubleshooting.md) files.
    - Lists locations of important log files
    - Common _Help!_ scenarios
    - How to manually test MX operations
        - Retrieving emails
    - Useful commands for troubleshooting problems with the following
        - Digital Ocean Droplet VM
        - Ansible
        - Docker
        - Python
        - MX Container (running Postfix and Dovecot)
        - Postgres Container
- [Local Troubleshooting](docs/local_troubleshooting.md):
    - Environment Variables
    - How to manually test MX operations
        - Sending emails
        - Getting an mbox file from your Gmail account
- [Prod Troubleshooting](docs/prod_troubleshooting.md):
    - Lists locations of important log files
    - Common _Help!_ scenarios
    - How to manually test MX operations
        - Sending emails
        - Getting your Maildir directory from the MX
