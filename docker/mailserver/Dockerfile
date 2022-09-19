FROM ubuntu:20.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt install -y postfix dovecot-core dovecot-imapd \ 
    supervisor sasl2-bin opendkim opendkim-tools iptables fail2ban cron rsyslog \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/bin/supervisord"]