#!/bin/bash
postconf -e "smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem"
postconf -e "smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key"
postconf -# "smtpd_tls_security_level"

postconf -# "smtp_tls_CApath"
postconf -# "smtp_tls_security_level"
postconf -# "smtp_tls_session_cache_database"


postconf -# "smtpd_relay_restrictions"
postconf -e "myhostname = mail.example.com"
postconf -e "alias_maps = hash:/etc/aliases"
postconf -e "alias_database = hash:/etc/aliases"
postconf -e "mydestination = $myhostname, example.com, localhost.example.com, localhost.localdomain, localhost"
postconf -e "relayhost = "
postconf -e "mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128"
postconf -e "mailbox_size_limit = 0"
postconf -e "recipient_delimiter = +"
postconf -e "inet_interfaces = all"
postconf -e "inet_protocols = all"
postconf -e "myorigin = example.com"
postconf -e "maillog_file = /var/log/mail.log"
postconf -# "smtpd_sasl_auth_enable"
postconf -# "broken_sasl_auth_clients"
postconf -# "smtpd_recipient_restrictions"
postconf -e "home_mailbox = Maildir/"

# Initialize a user
apt-get update
yes | apt install mailutils
useradd -m -s /bin/bash incoming
examplepassword | passwd incoming