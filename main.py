import schedule
import time
from tools import *

def job():
    try:
        creds = get_credentials()
        for to_addr in email_list:
            send(creds, to_addr)
        print('Success at {}.'.format(time.ctime()))
    except:
        print('Failure at {}.'.format(time.ctime()))

if __name__ == '__main__':
    schedule.every().day.at("06:30").do(job)
    print('Started daily emails...')
    while True:
        schedule.run_pending()
        time.sleep(30)