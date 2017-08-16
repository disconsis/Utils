#!/usr/bin/python3
# TODO: speakers even if aux
# TODO: fix song file checking
# TODO: ncurses
# TODO: put back volume setting
# TODO: silent mode

# Features:
#   Relative and absolute times
#   Popup message
#   Snooze
#   Song flexibility
#   (mostly) PEP8-compliant

import sys
import argparse
import os
import time
import datetime
import pyautogui

HOME = "/home/ketan"
MUSIC_DEFAULT_DIR = "/home/ketan/Windows/Music/"

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--absolute', help='absolute time',
                    action='store_true')
parser.add_argument('-Y', '--year', type=int)
parser.add_argument('-M', '--month', type=int)
parser.add_argument('-D', '--day', type=int)
parser.add_argument('-hr', '--hour', type=int)
parser.add_argument('-m', '--minute', type=int)
parser.add_argument('-s', '--second', type=int)
parser.add_argument("-msg", "--message")
parser.add_argument('-z', '--snooze', type=float, help="snooze time, in min")
with open("{}/bin/default_alarm.txt".format(HOME), "r") as fp:
    default_alarm = fp.read()
parser.add_argument('-d', '--dir', help='base directory for songs',
                    default=MUSIC_DEFAULT_DIR)
parser.add_argument('--song',
                    default=default_alarm,
                    help="path of the song; base directory is ~/Windows/Music")
parser.add_argument('-f',
                    '--failsafe',
                    action="store_true",
                    help="alarm sounds in case of an error, if set")
args = parser.parse_args()

MUSIC_DIR = args.dir


def playAlarm(args):
    os.system('amixer -D pulse sset Master 100% 1>/dev/null 2>&1')
    cmd = "mplayer '{}{}' 1>/dev/null 2>&1".format(MUSIC_DIR, args.song[:-1])
    os.system(cmd)
    if args.message is not None:
        pyautogui.alert(args.message)
    if args.snooze is not None:
        snooze_time = max(int(args.snooze * 60), 30)  # a min of 30 sec snooze
        next_snooze = args.snooze / 2
        cmd = "alarm -s {} -z {}".format(snooze_time, next_snooze)
        os.system(cmd)


try:
    os.chdir(MUSIC_DIR)
    # if not os.path.exists("'" + MUSIC_DIR + args.song[:-1] + "'"):
    #     print("Didn't find that song... you sure you typed that in right?")
    #     print("You gave me: " + "'" + MUSIC_DIR + args.song[:-1] + "'")
    #     exit()

    if len(sys.argv) == 1:
        parser.print_help()
        exit()

    if args.absolute:  # abs time
        now = datetime.datetime.now()
        now_dt = now
        date = list()
        for arg in ("year", "month", 'day'):
            if getattr(args, arg) is not None:
                date.append(getattr(args, arg))
            else:
                date.append(getattr(now, arg))
        for arg in ('hour', 'minute', 'second'):
            if getattr(args, arg) is not None:
                date.append(getattr(args, arg))
            else:
                date.append(0)
        now = datetime.datetime(now.year,
                                now.month,
                                now.day,
                                now.hour,
                                now.minute,
                                now.second)
        try:
            then = datetime.datetime(date[0],
                                     date[1],
                                     date[2],
                                     date[3],
                                     date[4],
                                     date[5])
        except ValueError:
            print("You tried to set an UNACCEPTABLE date")
            exit()
        except Exception as err:
            print("Couldn't set the date :/")
            print(err)
            exit()
        if then <= now:
            print("Can't change the past")
            exit()

    else:  # rel time
        now = time.time()
        now_dt = datetime.datetime.now()
        addtime = list()
        for arg in ('year', 'month', 'day', 'hour', 'minute', 'second'):
            if getattr(args, arg):
                addtime.append(getattr(args, arg))
            else:
                addtime.append(0)
        addedtime = (addtime[0] * 365 * 30 * 24 * 60 * 60   # year
                     + addtime[1] * 30 * 24 * 60 * 60       # month
                     + addtime[2] * 24 * 60 * 60            # day
                     + addtime[3] * 60 * 60                 # hour
                     + addtime[4] * 60                      # minute
                     + addtime[5])                          # second
        if addedtime <= 0:
            print("Can't change the past")
            exit()
        then = datetime.datetime.fromtimestamp(now + addedtime)

    try:
        # for prompt segment
        if then.day == now_dt.day or then.day - now_dt.day == 1:
            fmt = "%I:%M %p"
        elif then.year == now_dt.year:
            fmt = "%d %b, %I:%M %p"
        else:
            fmt = "%d/%b/%Y, %I:%M %p"
        with open('/tmp/alarm', 'w') as fp:
            fp.write(then.strftime(fmt))

        # for actual terminal printing
        print('Alarm set for ' + then.strftime('%c'))
        print('Time left:')
        diff = ''
        while datetime.datetime.now() < then:
            print('\b' * len(diff), end='')
            diff = str(then - datetime.datetime.now()).split('.')[0].rjust(50)
            print(diff, end='', flush=True)
            time.sleep(1)

        print('\b' * len(diff), end='')
        print('  ' * len(diff), end='')
        print('\b' * len(diff), end='')
        print('Time\'s up!')
        playAlarm(args)
    except KeyboardInterrupt as err:
        print('\nAlarm stopped'.rjust(50))

except Exception as err:
    print('Something fucked up')
    print(err)
    if args.failsafe:
        playAlarm(args)
