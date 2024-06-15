# sage

This app is like Mint, but ~~better~~ actually exists. It collects all of your personal financial data. The data is collected from alert emails sent from your financial institutions. The bank alert emails can be directed to your personal email account, such as a Gmail account. Then setup your account to forward the alert emails to a self-hosted MX. The financial data in the emails is extracted, stored, and made viewable. 

Thank you @nhopkinson and @whosgonna for their ongoing feedback on this project.

## Abbreviations
- msg = message
- txn = transaction
- uid = unique identifier
- mx = mailserver
- db = database

## Production Setup Instructions
*This app is production ready! For questions, problems and enhancements, open a github issue.*

1. Globally install the following software:
  <br> Python 3.7 or higher
2. Run the first setup script. This will create a .env file using the file .env-example as a template. 
  <br>`bash setup/1_setup_sage_directory.sh`
3. Define the following environment variables in the .env file:
  <br> `ISDEV`: Change to "False"
  <br> `DOMAIN`: Buy a domain name.
  <br> `FORWARDING_EMAIL`: Set up the email account that receives the transaction alert emails. This account needs to forward all emails to the receiving email address on the MX. The default receiving email address is incoming@DOMAIN. So if you purchased the domain example.com, the receiving email address would me incoming@example.com
  <br> `DO_API_TOKEN`: Create a Digital Ocean API Key. It's located in the "API" portion of their menu.
  <br> `PROD_SSH_PUBLIC_KEY`: Create SSH keys for you to SSH to the production server. Ensure the private key permissions are restricted.For help see the section "Production Setup Troubleshooting." Copy/paste the public key here.
  <br> `PROD_SSH_PRIVATE_KEY_FILE_PATH`: Copy/paste the path to the private key file here.
  <br> `SERVER_USER`: Your user the production server.
  <br> `SERVER_USER_PASSWORD`: Your user's password on the production server.
  <br> `SSH_ALLOWED_PUBLIC_IPS`: List the public IPs that can access to the production server.
4. **WARNING: RUNNING THIS SCRIPT CAUSES DIGITAL OCEAN TO START CHARGING YOU MONEY ON A MONTHLY BASIS FOR YOUR PRODUCTION SERVER.**
<br> Run the script to create a production Digital Ocean Droplet server that runs the application.
<br> `bash setup/2_create_prod_server.sh`
<br> If an error occurs, go to Digital Ocean and delete the Droplet and firewall before running the script again.
<br> It will prompt you for `BECOME password:`; enter your sudo password.
4. Run the script to configure the production Digital Ocean Droplet server.
<br> `bash setup/3_configure_prod_server.sh`
<br> This script is idempotent: no matter how many times you run it, the result will be the same. So if an error occurs, simply troubleshoot and run the script again until the error is resolved.
5. **WARNING: CREATING DIGITAL OCEAN VOLUMES ALSO COST MONEY, BUT THEY'RE HELPFUL FOR DISASTER RECOVERY. AT THIS TIME, THE VOLUMES ARE NOT OPTIONAL FOR THE DEPLOYMENT.** In the Digital Ocean console, go to the "Volumes Block Storage" tab and create two volumes: `sage-db` and `sage-mailserver`.
6. In the Digital Ocean console, attach each volume to the Droplet. SSH to the Droplet and run the commands Digital Ocean provides to mount each volume.
7. Re-run `bash setup/3_configure_prod_server.sh` to deploy Sage using the mounted volumes. 
<br> TODO: Create and mount Digital Ocean volumes during automated production deployment https://github.com/katefike/sage/issues/145

## Additional Documentation
All additional documentation can be found in the `docs/` directory.
- [Troubleshooting](docs/troubleshooting.md): 
    - Lists locations of important log files
    - How to troubleshoot common scenarios
    - How to manually test MX operations
        - Sending emails
        - Retrieving emails
    - Useful commands for troubleshooting problems with the following
        - Server
        - Postfix
        - Dovecot
        - MX Container
        - Postgres Container
        - Docker
        - Python
- [Local Development](docs/local_development.md): Provides local development setup instructions, how to create an ephemeral version of Sage for deployment testing (this part costs money), and using Pytest.
- [Disaster Recovery](docs/disaster_rcovery.md): Provides disaster recovery instructions. This is helpful for when something is deeply wrong with your current Sage deployment, but you have data in the MX and/or DB that you don't want to lose. The guide describes how to create a brand new Sage deployment and attach your existing data to it. 