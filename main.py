from tools import *

if __name__ == '__main__':
    creds = get_credentials()
    for to_addr in email_list:
        send(creds, to_addr)