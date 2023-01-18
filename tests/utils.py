import subprocess

from . import ENV


def fresh_inbox(mbox_name: str):
    """
    Re-create the user's Maildir. Then reads a directory
    containing an Mbox format mailbox and creates a Maildir format mailbox.

    The command doveadm expunge -u {EN['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all
    is insufficient because it does not restart incrementing of the UIDs
    at 1.
    """
    container = "docker exec sage-mailserver-1"
    maildir_path = f"/home/{ENV['RECEIVING_EMAIL_USER']}/Maildir/"
    mbox_path = f"/home/{ENV['RECEIVING_EMAIL_USER']}/test_data/example_data"
    try:
        subprocess.call(
            f"{container} rm -r {maildir_path} && mkdir {maildir_path}",
            shell=True,
        )
        print("Recreated Maildir/.")
        subprocess.call(
            f"{container} mb2md -s {mbox_path}/{mbox_name} -d {maildir_path}",
            shell=True,
        )
        subprocess.call(
            f"{container} chmod -R 777 {maildir_path}",
            shell=True,
        )
        print("Successfully loaded emails from mbox file.")
    except Exception as error:
        print(f"CRITICAL: Failed to create an inbox from an mbox: {error}")


def delete_emails():
    try:
        container = "docker exec sage-mailserver-1"
        subprocess.call(
            f"{container} doveadm expunge -u {ENV['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all",
            shell=True,
        )
        print("Successfully deleted all emails in the inbox.")
    except Exception as error:
        print(f"CRITICAL: Failed to delete emails: {error}")
