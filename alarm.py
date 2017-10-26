#!/usr/bin/python3

# TODO: snooze
# TODO: speakers even if aux

import dateparser
import argparse
import datetime
import curses
from time import sleep
import subprocess as proc
import os
from pyautogui import alert as tkalert
import re


DEFAULT_MUSIC_DIR = '/home/ketan/Windows/Music/'
DEFAULT_SONG = 'singles/m_Bach_PreludeToPartitaNo3.mp3'
DEFAULT_FONT = 'future'


def prompt_segment_write(end_time):
    now = datetime.datetime.now()
    timefmt = '%I:%M %p' if now.day == end_time.day else '%I:%M %p, %d %b'
    with open('/tmp/alarm', 'w') as fp:
        fp.write(end_time.strftime(timefmt))


def validate_song(args):
    if not args.dir or not args.song:
        raise ValueError('no song/dir provided')
    dir_slash = (args.dir[-1] == '/')
    song_slash = (args.song[0] == '/')
    if dir_slash and song_slash:
        song = args.dir[:-1] + args.song
    elif dir_slash or song_slash:
        song = args.dir + args.song
    else:
        song = args.dir + '/' + args.song
    if not os.path.exists(song):
        raise ValueError('provided song "{0}" is not valid'.format(song))
    return song


def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-a', '--abs', action='store_true')
    parser.add_argument('abs_rel', choices=['at', 'after'])
    font_choices = [font.split('.')[0]
                    for font in os.listdir('/usr/share/figlet')
                    if font.split('.')[1] == 'tlf']
    parser.add_argument('-f', '--font', default=DEFAULT_FONT,
                        choices=font_choices)
    parser.add_argument('-m', '--msg', default=None)
    # parser.add_argument('-z', '--snooze', type=float, default=2)
    parser_volume = parser.add_mutually_exclusive_group()
    parser_song = parser_volume.add_argument_group()
    parser_song.add_argument('-d', '--dir', default=DEFAULT_MUSIC_DIR)
    parser_song.add_argument('--song', default=DEFAULT_SONG)
    parser_volume.add_argument('-ns', '--silent', action='store_true')
    parser.add_argument('-fg', choices=['black', 'red', 'green', 'yellow',
                                        'blue', 'magenta', 'cyan', 'white'],
                        default='white')
    parser.add_argument('-bg', choices=['black', 'red', 'green', 'yellow',
                                        'blue', 'magenta', 'cyan', 'white'],
                        default='black')
    parser.add_argument('time', nargs='+')
    args = parser.parse_args()
    args.abs = False if args.abs_rel == 'after' else True
    if not args.silent:
        args.song = validate_song(args)
    args.time = ' '.join(args.time)
    color_mapping = {
        'black': curses.COLOR_BLACK,
        'red': curses.COLOR_RED,
        'green': curses.COLOR_GREEN,
        'yellow': curses.COLOR_YELLOW,
        'blue': curses.COLOR_BLUE,
        'magenta': curses.COLOR_MAGENTA,
        'cyan': curses.COLOR_CYAN,
        'white': curses.COLOR_WHITE,
    }
    args.fg = color_mapping[args.fg]
    args.bg = color_mapping[args.bg]
    return args


def parse_time(input_time, delta):
    if not delta:
        return dateparser.parse(input_time)
    else:
        return dateparser.parse(input_time.rstrip() + ' from now')


def toilet(string, font):
    prog = proc.Popen('toilet -f {0}'.format(font).split(),
                      stdin=proc.PIPE, stdout=proc.PIPE)
    b_out = prog.communicate(string.encode('utf-8'))
    out = next(b.decode('utf-8') for b in b_out if b is not None)
    return out.split('\n')


def center(stdscr, string, font, color_pair, oldwin):
    out = toilet(string, font)
    out_cols = max([len(line) for line in out])
    out_lines = len(out)
    win = curses.newwin(out_lines, out_cols,
                        (curses.LINES - out_lines)//2,
                        (curses.COLS - out_cols)//2)
    if oldwin is not None:
        oldwin.clear()
        oldwin.refresh()
    for li, line in enumerate(out):
        win.addstr(li, 0, line, color_pair)
    win.refresh()
    return win


def get_curr_vol():
    mixer_settings = proc.check_output(
        'amixer -D pulse sget Master'.split()
    ).decode('utf-8').split('\n')
    r = re.compile(r'\[(\d+)%\]')
    re_vols = [r.search(line) for line in mixer_settings]
    curr_vol = max(int(m.group(1)) for m in re_vols if m is not None)
    return int(curr_vol)


def change_vol(vol):
    proc.call('amixer -D pulse sset Master {0}%'.format(str(vol)).split(),
              stdout=proc.DEVNULL, stderr=proc.DEVNULL)


def alert(stdscr, args, oldwin):
    msg = args.msg if args.msg is not None else 'Time up!'
    if not args.silent:
        init_vol = get_curr_vol()
        change_vol(100)
        mplayer = proc.Popen('mplayer -loop 0 {0}'.format(args.song).split(),
                             stdout=proc.DEVNULL, stderr=proc.DEVNULL)
        center(stdscr, msg, args.font, curses.color_pair(1), oldwin)
        curses.flushinp()
        stdscr.getkey()
        mplayer.kill()
        change_vol(init_vol)
    else:
        tkalert(msg)


def countdown(stdscr, end_time, font, fg_color, bg_color, msg=None):
    stdscr.clear()
    curses.curs_set(False)
    curses.init_pair(1, fg_color, bg_color)

    now = datetime.datetime.now()
    timefmt = '%I:%M %p' if now.day == end_time.day else '%I:%M %p, %d %b'
    stdscr.addstr(0, 0, 'Alarm set for: ' + end_time.strftime(timefmt))
    stdscr.refresh()

    win = None
    while now < end_time:
        time_left = str(end_time - now).split('.')[0]
        win = center(stdscr, time_left, font, curses.color_pair(1), win)
        sleep(1)
        now = datetime.datetime.now()

    alert(stdscr, args, win)


if __name__ == '__main__':
    args = parse_args()
    end_time = parse_time(args.time, not args.abs)
    prompt_segment_write(end_time)
    try:
        curses.wrapper(countdown,
                       end_time,
                       font=args.font,
                       fg_color=args.fg, bg_color=args.bg,
                       msg=args.msg if not args.silent else None)
    except KeyboardInterrupt:
        exit(0)
