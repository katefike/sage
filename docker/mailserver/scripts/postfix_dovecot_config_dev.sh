#!/bin/bash

# Loads test data into the mailbox
if [[ -f /home/$RECEIVING_EMAIL_USER/test_data/$PRE_LOAD_MBOX ]]; then
  # Convert mbox (mb) file to Maildir (md)
  # docs found out https://github.com/dovecot/tools/blob/main/mb2md.pl
  mb2md -s /home/$RECEIVING_EMAIL_USER/test_data/$PRE_LOAD_MBOX -d /home/$RECEIVING_EMAIL_USER/Maildir/
fi

# Configures /etc/postfix/main.cf, /etc/postfix/master.cf,
# and /etc/dovecot/dovecot.conf for development

# Here are the docs on the postconf arguments: https://www.postfix.org/postconf.1.html
# Diable TLS for delivering mail (outbound/SMTP)
# TODO: Figure out if any smtp config is needed at all; 
# current purpose is receiving/inbound only.
postconf -# "smtp_tls_CApath"
postconf -# "smtp_tls_security_level"
postconf -# "smtp_tls_session_cache_database"
# Diable TLS for  for receiving mail (inbound/SMTPD)
postconf -# "smtpd_tls_cert_file"
postconf -# "smtpd_tls_key_file"
postconf -# "smtpd_tls_security_level"
postconf -# "smtpd_relay_restrictions"