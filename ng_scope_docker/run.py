import os
import signal
from argparse import ArgumentParser
import subprocess as sp
from time import sleep

from ng_scope_docker.arfcn_calc import earfcn2freq
from ng_scope_docker.genConfig import gen_config, safe_config


def main():
    parser = ArgumentParser()
    parser.add_argument('-e', '--earfcn', type=int, nargs='+', help='EARFCN to listen to.')
    parser.add_argument('-r', '--rf-number', type=int, default=1, help='Number of SDRs.')
    parser.add_argument('-n', '--name', default='ng-scope', help='Name of container.')
    parser.add_argument('-l', '--log', default=os.getcwd())
    parser.add_argument('-i', '--image', default='docker.io/j0lama/ng-scope:latest')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--docker', action='store_const', dest='prog', const='docker')
    group.add_argument('-p', '--podman', action='store_const', dest='prog', const='podman')
    parser.set_defaults(prog='podman')
    parser.add_argument('-t', '--timeout')
    args = parser.parse_args()

    if args.timeout is not None:
        timestr = args.timeout.lower()
        if timestr[-1] == 'h':
            timeout = float(timestr[:-1]) * 3600
        elif timestr[-1] == 'm':
            timeout = float(timestr[:-1]) * 60
        elif timestr[-1] == 's':
            timeout = float(timestr[:-1])
        else:
            timeout = float(timestr)
    else:
        timeout = None

    os.makedirs(args.log, exist_ok=True)

    for i, earfcn in enumerate(args.earfcn):
        freq = earfcn2freq(earfcn)
        cfg = gen_config(args.rf_number, earfcn)
        safe_config(cfg, os.path.join(args.log, 'config.cfg'))
        docker_cmd = f'{args.prog} run --name {args.name} -ti --privileged --rm -v {args.log}:/ng-scope/build/ngscope/src/logs/ {args.image} bash -c '
        exec_cmd = f'./ngscope > /dev/null; ./ngscope -c logs/config.cfg -s "logs/sibs_{freq}.dump" -o logs/dci_output/'
        exec_cmd = "'" + exec_cmd + "'"
        cmd = f'{docker_cmd} {exec_cmd}'
        p = sp.Popen(cmd, shell=True, stdin=sp.PIPE)
        try:
            # result = sp.run(cmd, shell=True, timeout=timeout)
            # p.communicate(timeout=timeout)
            p.wait(timeout)
        # except KeyboardInterrupt:
        #     pass
        except sp.TimeoutExpired:
            # p.kill()
            # os.kill(p.pid, signal.SIGTERM)
            p.stdin.write(b'\x03')
            p.stdin.flush()
            p.wait()
            if i < len(args.earfcn) - 1:
                sleep(10)

if __name__ == '__main__':
    main()
