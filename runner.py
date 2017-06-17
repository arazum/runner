#! /usr/bin/env python

import argparse
import json
import arrow
import os
import subprocess
import time


DEFAULT_QUEUE_FILE = '.queue'
TIME_FORMAT = ''
SLEEP = 1


def process_queue(path, function):
    with open(path, 'r+') as f:
        jobs = json.load(f)
        value,jobs = function(jobs)

        f.seek(0)
        f.truncate()
        json.dump(jobs, f)

    return value

def command_run(args):
    def process(jobs):
        first = None
        if jobs:
            first = jobs.pop()

        return first,jobs

    while True:
        job = process_queue(args.queue, process)

        if job:
            command = job['command']
            arguments = job['args']
            cwd = job['cwd']
            dt = arrow.get(job['time']).humanize()

            print ('Running job:')
            print ('{} ({})'.format(dt, cwd))
            print ('{} {}\n\n'.format(command, arguments))
            
            cmd = [command] + arguments
            subprocess.call(cmd, cwd=cwd)

            print ('\n')

        time.sleep(1)

def command_add(args):
    job = {
            'command': args.command,
            'args': args.args,
            'cwd': os.getcwd(),
            'time': arrow.now().timestamp,
            }

    def process(jobs):
        jobs.append(job)
        return None,jobs

    process_queue(args.queue, process)

def command_list(args):
    with open(args.queue) as f:
        jobs = json.load(f)

    for i,job in enumerate(jobs):
        dt = arrow.get(job['time']).humanize()

        print ('[{} / {}] {} ({})'.format(i + 1, len(jobs), dt, job['cwd']))
        print ('{} {}\n'.format(job['command'], job['args']))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--queue', default=DEFAULT_QUEUE_FILE, metavar='FILE')
    subparsers = parser.add_subparsers()

    parser_r = subparsers.add_parser('run')
    parser_r.set_defaults(func=command_run)

    parser_a = subparsers.add_parser('add')
    parser_a.set_defaults(func=command_add)
    parser_a.add_argument('command')
    parser_a.add_argument('args', nargs=argparse.REMAINDER)

    parser_l = subparsers.add_parser('list')
    parser_l.set_defaults(func=command_list)

    args = parser.parse_args()

    if not os.path.isfile(args.queue):
        with open(args.queue, 'w') as f:
            json.dump([], f)

    args.func(args)
