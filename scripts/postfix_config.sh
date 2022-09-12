#!/bin/bash
# postconf -e "home_mailbox = Maildir/"
postconf -e "mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128, localhost"
postconf -e "smtpd_relay_restrictions = reject"
postconf -e "smtpd_recipient_restrictions = permit_mynetworks, permit_sasl_authenticated"
postconf -e "alias_maps = hash:/etc/aliases"
postconf -e "mydestination = $myhostname, example.com, localhost.example.com, localhost.localdomain, localhost"