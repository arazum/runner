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

            print ('----------')
            print ('Running job sumbitted {}.\nWorking directory: {}\n'.format(dt, cwd))
            print ('{} {}'.format(command, ' '.join(arguments)))
            print ('----------')
            print ('\n\n')
            
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
    parser = argparse.ArgumentParser(description='''Run blocking jobs. When a job is ran its environment is taken from the host process (run subcommand) and working directory from where the job was added (add subcommand).''')
    parser.add_argument('-q', '--queue', default=DEFAULT_QUEUE_FILE, metavar='FILE', help='''Queue file to use in subcommands. Default is '.queue' in current directory.''')
    subparsers = parser.add_subparsers(help='''Available subcommands. Use 'runner.py {subcommand} --help' for more details.''')

    parser_r = subparsers.add_parser('run', help='''Start runner host. The runner is reading jobs from the specified queue file (see -q flag).''')
    parser_r.set_defaults(func=command_run)

    parser_a = subparsers.add_parser('add', help='''Add a new job to the queue. Job will be run with the working directory from which it was added. Job is added to the specified queue file (see -q flag).''')
    parser_a.set_defaults(func=command_add)
    parser_a.add_argument('command', help='command to run')
    parser_a.add_argument('args', nargs=argparse.REMAINDER, help='command arguments')

    parser_l = subparsers.add_parser('list', help='''List queued jobs.''')
    parser_l.set_defaults(func=command_list)

    args = parser.parse_args()

    if not os.path.isfile(args.queue):
        with open(args.queue, 'w') as f:
            json.dump([], f)

    args.func(args)
