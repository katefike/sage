#!/usr/bin/python3
import os
import smtplib
import pathlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

app_root = str(pathlib.Path(__file__).parent.parent)
env_path = app_root + "/.env"
if not load_dotenv(env_path):
    print(".env failed to load.")
RECEIVING_EMAIL = os.environ.get("RECEIVING_EMAIL")
DOMAIN = os.environ.get("DOMAIN")


sender = "root@localhost"
receivers = f"{RECEIVING_EMAIL}@e{DOMAIN}"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart("alternative")
msg["Subject"] = "Link"
msg["From"] = sender
msg["To"] = receivers

# Create the body of the message
html = """\
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
       Here is the <a href="http://www.python.org">link</a> you wanted.
    </p>
  </body>
</html>
"""

# Record the MIME type
part1 = MIMEText(html, "html")
# Attach the part to the message
msg.attach(part1)

host = ""
port = 25
local_hostname = "localhost"
smtp_conn = smtplib.SMTP(host, port, local_hostname)

try:
    smtp_conn = smtplib.SMTP("localhost")
    smtp_conn.sendmail(sender, receivers, msg.as_string())
    print("Successfully sent email")
except smtplib.SMTPException as error:
    print(f"Error: {error}")
