#!/usr/bin/python3
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender = "root@localhost"
receivers = "incoming@example.com"

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
