from rational_multi_monitors import RationalMultiMonitors
import argparse
import importlib
import sys

def main(args):
    """
    Main function to parse arguments and run the Rational Multi-Monitors.
    """
    parser = argparse.ArgumentParser(description='Rational Monitor for LTL formulas.')
    parser.add_argument('ltl', type=str, help='LTL formulas to monitor (separated by comma)')
    parser.add_argument('ap', type=str, help='Atomic propositions in the formula')
    parser.add_argument('visibility', type=str, help='Monitors\' visibility')
    parser.add_argument('resource_bound', type=float, help='Resource bound for knapsack problem')
    parser.add_argument('time_window', type=int, help='Time window for monitoring')
    parser.add_argument('filename', type=str, help='File with events to monitor')
    
    args = parser.parse_args(args[1:])

    ltls = args.ltl.split(',')
    ap = set(args.ap.replace('[','').replace(']','').replace(' ', '').split(','))
    ap.add('inv1')
    ap.add('inv2')
    aux = args.visibility
    visibilities = []
    i = aux.find('[')
    j = aux.find(']')
    while i != -1 and j != -1:
        visibilities.append(aux[i+1:j].replace(' ', '').split(','))
        i = aux.find('[', i+1)
        j = aux.find(']', j+1)
    sims = []
    for visibility in visibilities:
        aux = []
        for atom in ap:
            if atom not in ['inv1', 'inv2'] and atom not in visibility:
                aux.append([atom, 'inv1', 'inv2'])
        sims.append(aux)
    ltls_and_sim = []
    for i in range(len(ltls)):
        ltl = ltls[i]
        sim = sims[i]
        ltls_and_sim.append((ltl, sim))
    resource_bound = args.resource_bound
    time_window = args.time_window
    filename = args.filename
    
    monitor = RationalMultiMonitors(ltls_and_sim, ap, resource_bound, time_window)
    verdicts = None
    with open(filename, 'r') as file:
        while True:
            event = file.readline()
            if not event:
                break
            verdicts = monitor.next(set(event.replace('\n', '').replace(' ', '').split(',')))
    for i in range(len(verdicts)):
        print(f'Monitor {i}\'s Verdict: ' + str(verdicts[i]))
    return verdicts

if __name__ == '__main__':
    main(sys.argv)