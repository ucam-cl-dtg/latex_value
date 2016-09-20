#!/usr/bin/env python3
import uncertainties
import os
import fcntl
import datetime
import re
import decimal
from math import floor, log10, copysign

# When incorporating values into a latex document it is useful to be able to include
# a file which contains all the values as named commands
# This module faciliates doing this.


set_latex_value_filename = 'latex.tex'
set_latex_value_prefix = ''
default_sig_figs = 3
default_decimal_places = -1 # No limit

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


def set_latex_value(key, value, t=None, filename=None, prefix=None, sig_figs=default_sig_figs, decimal_places=default_decimal_places):
    r'''Create or update a command in the output file of the form:
    \newcommand{\$prefix$key}{$value}'''
    # Get the file
    if filename == None:
        filename = set_latex_value_filename
    if prefix == None:
        prefix = set_latex_value_prefix
    if not os.path.exists(filename):
        open(filename, 'a').close()  # Create file if it does not exist

    # Turn Decimals to floats
    if isinstance(value, decimal.Decimal):
        value = float(value)

    # Mangle the value
    if t == 'perc':
        if isinstance(value, float):
            svalue = '{}\%'.format(display_num(value * 100, sig_figs=sig_figs, decimal_places=decimal_places))
        elif isinstance(value, uncertainties.UFloat):
            set_latex_value(key + 'Nominal', value.nominal_value, t=t, filename=filename, prefix=prefix, sig_figs=sig_figs, decimal_places=decimal_places)
            svalue = r'${}\%$'.format(display_num(value * 100, sig_figs=sig_figs, decimal_places=decimal_places)[1:-1])#Strip starting and ending $s to put a % inside
        elif isinstance(value, int):
            svalue = '{}\%'.format(display_num(value, sig_figs=sig_figs, decimal_places=decimal_places))
        else:
            raise ValueError("Not a percentage" + str(type(value)))
    elif t == 'bareperc':
        if isinstance(value, float):
            svalue = display_num(value * 100, sig_figs=sig_figs, decimal_places=decimal_places)
        elif isinstance(value, uncertainties.UFloat):
            set_latex_value(key + 'Nominal', value.nominal_value, t=t, filename=filename, prefix=prefix, sig_figs=sig_figs, decimal_places=decimal_places)
            svalue = display_num(value * 100, sig_figs=sig_figs, decimal_places=decimal_places)
        elif isinstance(value, int):
            svalue = display_num(value, sig_figs=sig_figs, decimal_places=decimal_places)
        else:
            raise ValueError("Not a percentage" + str(type(value)))
    elif t == 'small':
        svalue = r'\num{{{0:.3g}}}'.format(value)
    elif t == 'days':
        # Produce a years subkey and call ourself again
        set_latex_value(key + 'Years', value/365, filename=filename, prefix=prefix, sig_figs=sig_figs, decimal_places=decimal_places)
        set_latex_value(key, value, filename=filename, prefix=prefix, sig_figs=sig_figs, decimal_places=decimal_places)
        return
    else:
        if isinstance(value, float):
            svalue = '{}'.format(display_num(value, sig_figs=sig_figs, decimal_places=decimal_places))
        elif isinstance(value, uncertainties.UFloat):
            set_latex_value(key + 'Nominal', value.nominal_value, t=t, filename=filename, prefix=prefix, sig_figs=sig_figs, decimal_places=decimal_places)
            svalue = display_num(value, sig_figs=sig_figs, decimal_places=decimal_places)
        elif isinstance(value, int):
            svalue = display_num(value, sig_figs=sig_figs, decimal_places=decimal_places)
        elif isinstance(value, datetime.date):
            set_latex_value(key + 'Month', value.strftime('%B %Y'), t=t, filename=filename, prefix=prefix, sig_figs=sig_figs, decimal_places=decimal_places)
            svalue = str(value)
        else:
            svalue = str(value)
    # Set the contents
    kv_line = r'\newcommand{''\\' + prefix + key + r'}{' + svalue + r'}'
    k_part = r'\newcommand{''\\' + prefix + key + r'}'
    with open(filename + '.lock', 'w') as lf:
        fcntl.lockf(lf.fileno(), fcntl.LOCK_EX)
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
        fcntl.lockf(lf.fileno(), fcntl.LOCK_UN)


def find_sig_figs_significance(num, sig_figs):
    """
    Find the smallest value which is singificant to this number of significant figures
    i.e. if num is -1.1 and sig_figs is 3 then returns -0.01
    """
    if num == 0.0:
        sig_figs_position = (sig_figs - 1)
    else:
        sig_figs_position = (sig_figs - 1) - round(log10(abs(num)))
    if sig_figs_position < 0:
        sig_figs_significance = 1.0 * 10 ** (-sig_figs_position)
    else:
        sig_figs_significance = 1.0 * 10 ** (-sig_figs_position)
    return copysign(sig_figs_significance, num)


to_significance_after_point = re.compile(r'(-?)[0-9]\.([0-9]*)[1-9](e.*)?')
to_significance_before_point = re.compile(r'(-?)[1-9]*(0*)(\.0*)?(e.*)?')
def find_significance(num, sig_figs):
    match_after_point = to_significance_after_point.match(str(num))
    match_before_point = to_significance_before_point.match(str(num))
    if match_after_point:
        match = match_after_point
        significance = '{sign}{before_point}.{after_point}1'.format(sign=match.group(1), before_point='0', after_point='0'*len(match.group(2)))
        exponent = match.group(3)
        if exponent:
            significance += exponent
        significance = float(significance)
    elif match_before_point:
        match = match_before_point
        significance = '{sign}1{after_sig}'.format(sign=match.group(1), after_sig=match.group(2))
        exponent = match.group(4)
        if exponent:
            significance += exponent
        significance = float(significance)
    else:
        raise ValueError('No match on number, could not find significance: ' + num)
    return significance


def display_num(num, sig_figs=default_sig_figs, decimal_places=default_decimal_places):
    if isinstance(num, uncertainties.UFloat):
        rounded_nominal_num = round_num(num.nominal_value, sig_figs)
        if decimal_places != -1:
            rounded_nominal = reduce_to_decimal_places(decimal_places,rounded_nominal_num)
        else:
            rounded_nominal = '{:,}'.format(rounded_nominal_num).replace(',',r'\,')
        if abs(num.std_dev) < abs(find_sig_figs_significance(num.nominal_value, sig_figs)):
            rounded_std_dev = '{:,}'.format(round_num(0.0, sig_figs)).replace(',',r'\,')
        else:
            rounded_std_dev = '{:,}'.format(round_num(num.std_dev, sig_figs)).replace(',',r'\,')
        if '.' in rounded_nominal:
            ndp = len(rounded_nominal) - rounded_nominal.find('.') -1 # we want the index of the number after the '.'
            sdp = len(rounded_std_dev) - rounded_std_dev.find('.') -1
            if sdp > ndp:
                rounded_std_dev = '{:,}'.format(round(num.std_dev, ndp)).replace(',',r'\,')
        elif '.' in rounded_std_dev:
            rounded_std_dev = rounded_std_dev[:rounded_std_dev.find('.')]
        return '$' + rounded_nominal + r' \pm ' + rounded_std_dev + '$'

    rounded = round_num(num, sig_figs)
    if decimal_places != -1:
        return reduce_to_decimal_places(decimal_places, rounded)
    else:
        return '{:,}'.format(rounded).replace(',',r'\,')

def reduce_to_decimal_places(decimal_places, rounded_nominal_num):
    smallest_value = 1.0/(10.0**decimal_places)
    rounded_nominal = '{:,}'.format(rounded_nominal_num).replace(',',r'\,')
    if '.' in rounded_nominal and rounded_nominal_num != 0:
        if abs(rounded_nominal_num) < smallest_value:
            rounded_nominal = '<{}'.format(copysign(smallest_value, rounded_nominal_num))
            return rounded_nominal
        current_decimal_places = len(rounded_nominal.split('.')[1])
        if current_decimal_places > decimal_places:
            rounded_nominal = '{:,}'.format(round(rounded_nominal_num, decimal_places)).replace(',',r'\,')
    return rounded_nominal


def round_num(num, sig_figs):
    if isinstance(num, int):
        if len(str(abs(num))) < sig_figs:
            return num
        else:
            return floor(round(num, (sig_figs -1) - floor(log10(abs(num)))))
    if isinstance(num, float):
        if num == 0.0:
            return num
        logged = floor(log10(abs(num)))
        rounded = round(num, -int(logged) + (sig_figs -1))
        if logged >= sig_figs -1:#We don't want a spurious .0 if that is below the sig_figs
            rounded = floor(rounded)
        return rounded
    else:
        raise TypeError("unimplemented")


def num2word(number):
    # https://stackoverflow.com/questions/3154460/python-human-readable-large-numbers/3155023#3155023
    millnames = ['', ' thousand', ' million', ' billion', ' trillion', ' quadrillion', 'quintillion']
    n = round_num(float(number), default_sig_figs)
    millidx = max(0, min(len(millnames) - 1, int((floor(log10(abs(n))) // 3))))
    # If less than 10000 then just display it as normal
    if millidx == 0 or log10(abs(n)) < 4:
        return display_num(number)
    return '%s%s' % (display_num(n / 10 ** (3 * millidx)), millnames[millidx])


def try_shorten(string, length=20):
    if not isinstance(string, str):
        return string
    if len(string) > length:
        index = string.rfind(' ')
        if index > length//2:
            return try_shorten(string[:index])
        else:
            return string
    else:
        return string

