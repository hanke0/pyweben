import importlib
import os
import time
import sys
from multiprocessing import Process

import click
import pandas as pd


@click.group()
def cli():
    pass


@click.option('--config', "-c", "config_file", type=click.File())
@cli.command()
def server(config_file=None):
    from pyweben.config import load_config
    config = load_config(config_file)

    processes = []
    names = {}
    exit_code = 0
    try:
        for section in config.sections():
            if section == 'requests':
                continue
            section_config = config[section]
            module, runner = section_config['runner'].split(':', 1)
            module = importlib.import_module(module)
            runner = getattr(module, runner or f"run_{section}")

            p = Process(target=runner, args=(section_config, ))
            processes.append(p)
            p.start()
            names[p.pid] = section
            print(f"Start {section} server(pid={p.pid}) at port {section_config['port']}")

        for p in processes:
            p.join()
        time.sleep(1)
    finally:
        print("Shutdown server!")
        for p in processes:
            print("kill process", p.pid)
            p.kill()
            p.join()
        print("Bye Bye!")
        sys.exit(exit_code)


@click.option('--config', "-c", "config_file", type=click.Path(exists=True, readable=True))
@click.option("--csv", "--csv-base-name", "csv_base_name", help="Store current request stats to files in CSV format.")
@click.option("-c", "--clients", 'clients', help="Number of concurrent Locust users.")
@click.option("-r", "--hatch-rate", 'hatch_rate', help="The rate per second in which clients are spawned.")
@click.option("-t", "--run-time", 'run_time', help="Stop after the specified amount of time, e.g. (300s,20m, 3h, 1h30m, etc.).")
@click.option("-w", "--web", "web", is_flag=True, help="Run locust web")
@cli.command()
def locust(config_file, clients, hatch_rate, run_time, csv_base_name, web):
    if config_file:
        os.environ["PYWEBEN_CONFIG"] = config_file
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bencher.py')
    from pyweben.utils import run_locust, run_locust_web
    if web:
        return run_locust_web(file)

    clients = clients or 1000
    hatch_rate = hatch_rate or 100
    run_time = run_time or '1h'
    csv_base_name = csv_base_name or 'pyweben'

    return run_locust(file, clients, hatch_rate, run_time, csv_base_name)


@click.option('-f', '--file', 'file',  type=click.Path(exists=True, readable=True))
@cli.command()
def display(file):
    df = pd.read_csv(file)
    df = df.set_index(df.columns[:2])
    df.plot()


if __name__ == '__main__':
    cli()
