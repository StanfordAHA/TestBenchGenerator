from itertools import chain
import json
import magma as m

_CGRA_SIGNAL_PORTS = [
        ('config_addr_in', m.Array(32, m.BitIn)),
        ('config_data_in', m.Array(32, m.BitIn)),
        ('clk_in',         m.BitIn),
        ('reset_in',       m.BitIn),
        ('tdi',            m.BitIn),
        ('tms',            m.BitIn),
        ('tck',            m.BitIn),
        ('trst_n',         m.BitIn),
        ('tdo',            m.BitOut),
        ]

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

    ios = _flatten(chain(
        _CGRA_SIGNAL_PORTS,
        ((mod, m.Array(int(c['width']), _s2b(c['mode']))) for mod, c in io_d.items())
    ))

    class Tester(m.Circuit):
        name = "CGRA_tester"
        IO = ios

        @classmethod
        def definition(io):
            cgra = cgra_def()

            for port in io.interface:
                if port in io_d:
                    #port is a pin
                    direct = io_d[port]['mode']
                    for bit, pad in io_d[port]['bits'].items():
                        try:
                            #pad + '_' + direct is the 'de-tristated' name
                            m.wire(cgra.interface[pad + '_' + direct], io.interface[port][int(bit)])
                        except KeyError as e:
                            Print('Looks like their is some sort of inconsistency between the cgra_info (or at least the collateral) and top.v')
                            raise e
                else:
                    #port is a control signal
                    try:
                        m.wire(cgra.interface[port], io.interface[port])
                    except KeyError as e:
                        Print('Looks like _CGRA_SIGNAL_PORTS is no longer correct')
                        raise e




    return Tester

if __name__ == '__main__':
    cgra = DefineTester('top.v', 'collateral.json')
    m.compile('tester', cgra)

