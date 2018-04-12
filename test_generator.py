from itertools import chain
import json

import magma as m

def _flatten(l):
    return list(chain(*l))

def _s2b(s):
    if s == 'out':
        return m.BitOut
    elif s == 'in':
        return m.BitIn
    elif s == 'inout':
        return m.BitInOut
    else:
        raise ValueError(f'Unknown direction {s}')

def DefineTester(cgra_file, collateral_file):

    cgra_def = m.DeclareFromVerilogFile(cgra_file)[0]


    with open(collateral_file, 'r') as f:
        io_d = json.load(f)

    ios = _flatten(
            (mod, m.Array(int(c['width']), _s2b(c['mode']))) for mod, c in io_d.items()
            )

    class Tester(m.Circuit):
        name = "CGRA_tester"
        IO = ios

        @classmethod
        def definition(io):
            cgra = cgra_def()

            for port in io.interface:
                direct = io_d[port]['mode']

                for bit, pad in io_d[port]['bits'].items():
                    if direct == "out":
                        m.wire(cgra.interface[pad + '_' + direct], io.interface[port][int(bit)])
                    else:
                        m.wire(io.interface[port][int(bit)], cgra.interface[pad + '_' + direct])

    return Tester

if __name__ == '__main__':
    cgra = DefineTester('top.v', 'collateral.json')
    m.compile('tester', cgra)

