import praw
import schedule
from halo import Halo
from time import sleep
import datetime
import configparser


class C:
    W, G, R, P, Y, C = '\033[0m', '\033[92m', '\033[91m', '\033[95m', '\033[93m', '\033[36m'


print(f"""{C.Y}
╦═╗╔═╗╔╦╗╔╦╗╔═╗╦  ╦╔═╗╦═╗
╠╦╝║╣  ║║ ║║║ ║╚╗╔╝║╣ ╠╦╝
╩╚═╚═╝═╩╝═╩╝╚═╝ ╚╝ ╚═╝╩╚═ V1
{C.W}""")


def get_now(plus):
    return (datetime.datetime.now() + datetime.timedelta(minutes=plus)).strftime('%d/%m/%Y %H:%M:%S')


def spin_text(text):
    spinner.text = text


def main():
    t = 0
    c = 0

    if test_mode:
        test = '[TEST MODE] '
    else:
        test = ''

    for submission in reddit.subreddit(target_sub).new(limit=limit):
        t += 1
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            c += 1
            spin_text(f'{C.P}{test}{C.W}Checked {C.G}{str(c)}{C.W} comments in {C.C}{str(t)}{C.W} threads')
            score = comment.score
            body = comment.body
            if score <= downvotes and body != '[removed]':
                spin_text(f'{C.R}{test}{C.W}Removing comment with score of {C.R}{score}{C.W}')
                sleep(.5)
                if delete:
                    comment.delete()
                else:
                    comment.mod.remove(spam=True)

    spin_text(f'Sleeping until {get_now(sleep_timer)}')


config = configparser.ConfigParser()
config.read('config.ini')
client_id = config.get('REDDIT', 'client_id')
client_secret = config.get('REDDIT', 'client_secret')
reddit_user = config.get('REDDIT', 'reddit_user')
reddit_pass = config.get('REDDIT', 'reddit_pass')
target_sub = config.get('SETTINGS', 'target_sub')
downvotes = int(config.get('SETTINGS', 'downvotes'))
delete = int(config.get('SETTINGS', 'delete'))
limit = int(config.get('SETTINGS', 'limit'))
sleep_timer = int(config.get('SETTINGS', 'sleep_timer'))
test_mode = int(config.get('TEST_MODE', 'test_mode'))


reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='Downvoted comment remover (by /u/impshum)',
                     username=reddit_user,
                     password=reddit_pass)

downvotes = - abs(downvotes)
schedule.every(sleep_timer).minutes.do(main)
spinner = Halo(text='Booting up...', spinner='dots')
spinner.start()


if __name__ == '__main__':
    try:
        main()
        while True:
            schedule.run_pending()
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        spinner.succeed(f'Stopped {get_now(0)}')
        print()
