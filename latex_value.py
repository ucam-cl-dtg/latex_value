#!/usr/bin/env python3
import uncertainties
import os
from math import floor, log10

# When incorporating values into a latex document it is useful to be able to include
# a file which contains all the values as named commands
# This module faciliates doing this.


set_latex_value_filename = 'latex.tex'
set_latex_value_prefix = ''


def latex_value_filename(filename):
    global set_latex_value_filename
    if None == filename:
        raise ValueError('Filename must not be None')
    set_latex_value_filename = filename


def latex_value_prefix(prefix):
    global set_latex_value_prefix
    if None == prefix:
        raise ValueError('Prefix must not be None')
    set_latex_value_prefix = prefix


def set_latex_value(key, value, t=None, filename=None, prefix=None):
    r'''Create or update a command in the output file of the form:
    \newcommand{\$prefix$key}{$value}'''
    # Get the file
    if filename == None:
        filename = set_latex_value_filename
    if prefix == None:
        prefix = set_latex_value_prefix
    if not os.path.exists(filename):
        open(filename, 'a').close()  # Create file if it does not exist
    # Mangle the value
    if t == 'perc':
        if isinstance(value, float):
            svalue = '{}\%'.format(display_num(value * 100))
        elif isinstance(value, uncertainties.UFloat):
            set_latex_value(key + 'Nominal', value.nominal_value, t=t, filename=filename, prefix=prefix)
            svalue = '${:.2L}\%$'.format(value * 100)
        elif isinstance(value, int):
            svalue = '{}\%'.format(display_num(value))
        else:
            raise ValueError("Not a percentage")
    elif t == 'small':
        svalue = r'\num{{{0:.3g}}}'.format(value)
    else:
        if isinstance(value, float):
            svalue = '{}'.format(display_num(value))
        elif isinstance(value, uncertainties.UFloat):
            set_latex_value(key + 'Nominal', value.nominal_value, t=t, filename=filename, prefix=prefix)
            svalue = '${:.2L}$'.format(value)
        elif isinstance(value, int):
            svalue = display_num(value)
        else:
            svalue = str(value)
    # Set the contents
    kv_line = r'\newcommand{''\\' + prefix + key + r'}{' + svalue + r'}'
    k_part = r'\newcommand{''\\' + prefix + key + r'}'
    with open(filename) as rf:
        sf = rf.read()
    start_index = sf.find(k_part)
    if start_index >= 0:  # if already set, update
        startofvalue = start_index + len(k_part) + 1  # 1 for the {
        endofvalue = sf.find('}\n', startofvalue)
        sf = sf[:startofvalue] + svalue + sf[endofvalue:]
    else:
        sf += kv_line + '\n'
    # Write the updated file
    with open(filename, 'w') as wf:
        wf.write(sf)


def display_num(num, sig_figs=3):
    rounded = round_num(num, sig_figs)
    return '{:,}'.format(rounded).replace(',',r'\,')


def round_num(num, sig_figs):
    if isinstance(num, int):
        if len(str(abs(num))) < sig_figs:
            return num
        else:
            return floor((round(num, -int(floor(log10(abs(num)))) + (sig_figs -1))))
    if isinstance(num, float):
        logged = floor(log10(abs(num)))
        rounded = round(num, -int(logged) + (sig_figs -1))
        if logged >= sig_figs:#We don't want a spurious .0 if that is below the sig_figs
            rounded = floor(rounded)
        return rounded
    else:
        raise TypeError("unimplemented")


def num2word(n):
    # https://stackoverflow.com/questions/3154460/python-human-readable-large-numbers/3155023#3155023
    millnames = ['', 'Thousand', 'Million', 'Billion', 'Trillion']
    n = float(n)
    millidx = max(0, min(len(millnames) - 1, int(floor(log10(abs(n)) / 3))))
    return '%.0f %s' % (n / 10 ** (3 * millidx), millnames[millidx])
