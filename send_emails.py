#!/usr/bin/python3
import smtplib

host = ''
port = 25
local_hostname = 'localhost'
smtp_conn = smtplib.SMTP(host, port, local_hostname)

sender = 'root@localhost'
receivers = ['incoming@example.com']

message = """From: From Person <root@localhost>
To: To Person <incoming@example.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""

try:
   smtp_conn = smtplib.SMTP('localhost')
   smtp_conn.sendmail(sender, receivers, message)         
   print("Successfully sent email")
except smtplib.SMTPException:
   print("Error: unable to send email")