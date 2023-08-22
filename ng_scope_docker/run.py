import os
from argparse import ArgumentParser
import subprocess as sp

from ng_scope_docker.arfcn_calc import earfcn2freq
from ng_scope_docker.genConfig import gen_config, safe_config


def main():
    parser = ArgumentParser()
    parser.add_argument('-e', '--earfcn', type=int, help='EARFCN to listen to.')
    parser.add_argument('-r', '--rf-number', type=int, help='Number of SDRs.')
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

    freq = earfcn2freq(args.earfcn)
    os.makedirs(args.log, exist_ok=True)
    cfg = gen_config(1, args.earfcn)
    safe_config(cfg, os.path.join(args.log, 'config.cfg'))
    docker_cmd = f'{args.prog} run --name {args.name} -ti --privileged --rm -v {args.log}:/ng-scope/build/ngscope/src/logs/ {args.image}'
    exec_cmd = f'./ngscope > /dev/null; ./ngscope -c logs/config.cfg -s "logs/sibs_{freq}.dump" -o logs/dci_output/'
    cmd = f'{docker_cmd} {exec_cmd}'
    print(cmd)
    try:
        result = sp.run(cmd, shell=True, timeout=timeout)
    except KeyboardInterrupt:
        pass
    except sp.TimeoutExpired:
        pass


if __name__ == '__main__':
    main()
