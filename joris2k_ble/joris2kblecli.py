#!/bin/env python3
""" Cli tool for testing connectivity with Joris2k BLE devices. """
import sys
import logging
import click
import re

from joris2k_ble import smartmeter

pass_dev_smartmeter = click.make_pass_decorator(smartmeter.SmartMeter)

def validate_mac(ctx, param, mac):
    if re.match('^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac) is None:
        raise click.BadParameter(mac + ' is no valid mac address')
    return mac

@click.group(invoke_without_command=True)
@click.option('--mac', envvar="BLE_MAC", required=True, callback=validate_mac)
@click.option('--debug/--normal', default=False)
@click.pass_context
def cli(ctx, mac, debug):
    """ Tool to query and modify the state of Joris2k BLE devices. """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    dev = smartmeter.SmartMeter(mac)
    dev.update()
    ctx.obj = dev

@cli.command()
@pass_dev_smartmeter
def info(dev):
    """ Gets power consumption."""
    click.echo("Current power consuption: %.3f kWh (low: %.3f, normal: %.3f)" \
            % (dev.power_consumption, dev.power_consumption_low, dev.power_consumption_normal))
    click.echo("Current power delivery: %.3f kWh (low: %.3f, normal: %.3f)" \
            % (dev.power_delivery, dev.power_delivery_low, dev.power_delivery_normal))
    click.echo("Tariff: %d" \
            % (dev.current_power_tariff))
    # Currently instantaneous has an issue
    #click.echo("Current power usage: %d kW" \
    #        % (dev.current_power_usage))
    click.echo("Current gas consumption: %.3f m3" \
            % (dev.gas_consumption))

@cli.command()
@pass_dev_smartmeter
def events(dev):
    """Get state using notifications."""
    

cli.add_command(info)

if __name__ == '__main__':
    cli()
