#!/usr/bin/env python3

#%%

import xml.etree.ElementTree as ElementTree
import re
from functools import lru_cache


signal_regex = re.compile('(\$.+)\.(.+)\[(\d+)\]')

#%%

@lru_cache(maxsize=200)
def find(root: ElementTree.Element, blockname: str):

    for e in root.iterfind(f'.//block[@name=\'{blockname}\']'):
        subels = e.iter()
        # find block with attributes
        next(subels)
        subel = next(subels)
        if subel.tag != 'attributes':
            continue

        return e

def print_element(e: ElementTree.Element, port_name: str, src_loc: bool):
    # print(e.items())
    if src_loc:
        for attr in e.iter('attribute'):
            if attr.attrib['name'] == 'src':
                yield f'src: {attr.text}'
        # print(attr.tag, attr.attrib, attr.text)

    for se in e.iter('port'):
        if se.attrib['name'] == port_name:
            text = se.text
            yield f'{port_name}: {text}'

            # replace portname with output
            if '->' in text:
                new_port = 'Q'
                if port_name[0] == 'S':
                    new_port = 'O'
                port_name = new_port + port_name[1:]


#%%
def process_file(f, root: ElementTree.Element, src_loc: bool):
    # for _ in range(1000):
        # line = f.readline()
    for line in f:
        auto_signal = signal_regex.search(line)
        print(line, end='')

        if auto_signal is None:
            continue

        block, port, index = auto_signal.groups()
        # print(groups)

        entry = find(root, block)
        if entry is None:
            continue

        for res in print_element(entry, port, src_loc):
            print('\t' + res)


#%%

if __name__ == '__main__':
    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser()
    parser.add_argument('report_file', type=Path)
    parser.add_argument('packed_netlist', type=Path)
    parser.add_argument('-s', '--src_loc', action='store_true')

    args = parser.parse_args()

    tree = ElementTree.parse(args.packed_netlist)
    root = tree.getroot()

    with open(args.report_file) as rpt:
        process_file(rpt, root, args.src_loc)

    cache_info = find.cache_info()
    hit_ratio = cache_info.hits/(cache_info.hits + cache_info.misses)
    print(f'#Cache stats: {cache_info}, hit ratio={hit_ratio*100:.2f}%')
