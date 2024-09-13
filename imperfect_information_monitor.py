import spot
from enum import Enum
import buddy

class Verdict(Enum):
    ff = 0
    tt = 1
    nf = 2
    nt= 3
    unknown = 4
    undefined = 5
    def __str__(self):
        if self.value == 0:
            return 'False'
        elif self.value == 1:
            return 'True'
        elif self.value == 2:
            return 'Unknown (but it won\'t ever be False)'
        elif self.value == 3:
            return 'Unknown (but it won\'t ever be True)'
        elif self.value == 4:
            return 'Unknown'
        else:
            return 'Undefined'

class ImperfectInformationMonitor:
    def __init__(self, ltl, ap, sim):
        self.__ap = ap
        self.__sim = sim
        self.__ltl = self.split(spot.formula(ltl))
    def get_sim(self):
        return self.__sim
    def set_sim(self, sim):
        self.__sim = sim
    def __str__(self):
        return str(self.__ltl)
    def next(self, ev):
        return self.__ltl.next(ev, self.__sim)
    def split(self, ltl):
        if ltl._is(spot.op_And): # conjunction
            sub_ltls = []
            for sub_ltl in ltl:
                sub_ltls.append(self.split(sub_ltl))
            return AndCompositionalMonitor(sub_ltls)
        elif ltl._is(spot.op_Or): # conjunction
            sub_ltls = []
            for sub_ltl in ltl:
                sub_ltls.append(self.split(sub_ltl))
            return OrCompositionalMonitor(sub_ltls)
        elif ltl._is(spot.op_Not): # negation
            for sub_ltl in ltl:
                return NotCompositionalMonitor(self.split(sub_ltl))
        else:
            return TemporalMonitor(str(ltl), self.__ap) 
            
class AndCompositionalMonitor():
    def __init__(self, sub_ltls):
        self.__sub_ltls = sub_ltls
    def __str__(self):
        l = []
        for sub_ltl in self.__sub_ltls:
            l.append(str(sub_ltl))
        return '&&'.join(l)
    def next(self, ev, sim):
        verdicts = []
        new_sub_ltls = []
        for sub_ltl in self.__sub_ltls:
            if sub_ltl not in [Verdict.tt, Verdict.ff, Verdict.undefined]:
                verdict = sub_ltl.next(ev, sim)
            else:
                verdict = sub_ltl
            verdicts.append(verdict)
            if verdict in [Verdict.tt, Verdict.ff, Verdict.undefined]:
                new_sub_ltls.append(verdict)
            else:
                new_sub_ltls.append(sub_ltl)
        self.__sub_ltls = new_sub_ltls
        if Verdict.ff in verdicts:
            return Verdict.ff
        elif Verdict.undefined in verdicts:
            return Verdict.undefined
        elif Verdict.nf in verdicts and Verdict.nt not in verdicts and Verdict.unknown not in verdicts:
            return Verdict.nf
        elif Verdict.nt in verdicts and Verdict.nf not in verdicts:
            return Verdict.nt
        elif Verdict.nf in verdicts and Verdict.nt in verdicts:
            return Verdict.nt
        elif Verdict.unknown in verdicts:
            return Verdict.unknown
        else:
            return Verdict.tt
class OrCompositionalMonitor():
    def __init__(self, sub_ltls):
        self.__sub_ltls = sub_ltls
    def __str__(self):
        l = []
        for sub_ltl in self.__sub_ltls:
            l.append(str(sub_ltl))
        return '||'.join(l)
    def next(self, ev, sim):
        verdicts = []
        new_sub_ltls = []
        for sub_ltl in self.__sub_ltls:
            if sub_ltl not in [Verdict.tt, Verdict.ff, Verdict.undefined]:
                verdict = sub_ltl.next(ev, sim)
            else:
                verdict = sub_ltl
            verdicts.append(verdict)
            if verdict in [Verdict.tt, Verdict.ff, Verdict.undefined]:
                new_sub_ltls.append(verdict)
            else:
                new_sub_ltls.append(sub_ltl)
        self.__sub_ltls = new_sub_ltls
        if Verdict.tt in verdicts:
            return Verdict.tt
        elif Verdict.nf in verdicts and Verdict.nt not in verdicts:
            return Verdict.nf
        elif Verdict.nt in verdicts and Verdict.nf not in verdicts and Verdict.unknown not in verdicts:
            return Verdict.nt
        elif Verdict.nf in verdicts and Verdict.nt in verdicts and Verdict.unknown not in verdicts:
            return Verdict.nf
        elif Verdict.unknown in verdicts:
            return Verdict.unknown
        elif Verdict.undefined in verdicts:
            return Verdict.undefined
        else:
            return Verdict.ff
        
class NotCompositionalMonitor():
    def __init__(self, sub_ltl):
        self.__sub_ltl = sub_ltl
    def __str__(self):
        return f'!({str(self.__sub_ltl)})'
    def next(self, ev, sim):
        if self.__sub_ltl not in [Verdict.tt, Verdict.ff, Verdict.undefined]:
            verdict = self.__sub_ltl.next(ev, sim)
        else:
            verdict = self.__sub_ltl
        if verdict in [Verdict.tt, Verdict.ff, Verdict.undefined]:
            self.__sub_ltl = verdict
        if Verdict.tt == verdict:
            return Verdict.ff
        elif Verdict.ff == verdict:
            return Verdict.tt
        elif Verdict.nt == verdict:
            return Verdict.nf
        elif Verdict.nf == verdict:
            return Verdict.nt
        elif Verdict.unknown == verdict:
            return Verdict.unknown
        else:
            return Verdict.undefined
        
class TemporalMonitor:
    def __init__(self, ltl, ap):
        eLTL = explicit_ltl(spot.formula(ltl).negative_normal_form().to_str(), ap)
        # print('Explicit LTL: ', eLTL)
        enLTL = explicit_ltl(spot.formula('!(' + ltl + ')').negative_normal_form().to_str(), ap)
        # print('Explicit negation of LTL: ', enLTL)
        self.__pAut = spot.translate(eLTL)
        self.__nAut = spot.translate(enLTL)
        self.__uAut = spot.translate('!('+eLTL+')&'+'!('+enLTL+')')
        # print(self.__uAut.to_str('hoa'))
        self.__pInit, self.__pFin = self.setup(self.__pAut)
        self.__nInit, self.__nFin = self.setup(self.__nAut)
        self.__uInit, self.__uFin = self.setup(self.__uAut)
        self.__ap = ap
        self.__ltl = ltl
    def __str__(self):
        return self.__ltl
    def setup(self, aut):
        fin = set()
        states = set()
        statesAux = set()
        init = aut.get_init_state_number()
        states.add(aut.get_init_state_number())
        statesAux.add(aut.get_init_state_number())
        while statesAux:
            s0 = statesAux.pop()
            for t in aut.out(s0):
                if t.dst not in states:
                    states.add(t.dst)
                    statesAux.add(t.dst)
        for s in states:
            aut.set_init_state(s)
            if not aut.is_empty():
                fin.add(s)
        aut.set_init_state(init)
        initSet = set()
        initSet.add(init)
        return initSet, fin
    def next(self, ev, sim):
        # print(ev)
        event = buddy.bddtrue
        for ap in self.__ap:
            if ap.startswith('!'): continue
            ind = []
            for s in sim:
                if ap in s:
                    ind = s
                    break
            # print(ind)
            if not ind and ap in ev:
                a = self.__pAut.register_ap(ap+'tt')
                b = self.__pAut.register_ap(ap+'ff')
                bdda = buddy.bdd_ithvar(a)
                bddb = buddy.bdd_nithvar(b)
                event = event & bdda & bddb
            elif not ind and ap not in ev:
                a = self.__pAut.register_ap(ap+'ff')
                b= self.__pAut.register_ap(ap+'tt')
                bdda = buddy.bdd_ithvar(a)
                bddb = buddy.bdd_nithvar(b)
                event = event & bdda & bddb
            elif ind and all(elem in ev for elem in ind):
                a = self.__pAut.register_ap(ap+'tt')
                b = self.__pAut.register_ap(ap+'ff')
                bdda = buddy.bdd_ithvar(a)
                bddb = buddy.bdd_nithvar(b)
                event = event & bdda & bddb
            elif ind and all(elem not in ev for elem in ind):
                a = self.__pAut.register_ap(ap+'ff')
                b = self.__pAut.register_ap(ap+'tt')
                bdda = buddy.bdd_ithvar(a)
                bddb = buddy.bdd_nithvar(b)
                event = event & bdda & bddb
            else:
                a = self.__pAut.register_ap(ap+'tt')
                b = self.__pAut.register_ap(ap+'ff')
                bdda = buddy.bdd_nithvar(a)
                bddb = buddy.bdd_nithvar(b)
                event = event & bdda & bddb
        pInitAux = set()
        while self.__pInit:
            init = self.__pInit.pop()
            for t in self.__pAut.out(init):
                if (t.cond & event) != buddy.bddfalse and t.dst in self.__pFin:
                    pInitAux.add(t.dst)
        self.__pInit = pInitAux
        nInitAux = set()
        while self.__nInit:
            init = self.__nInit.pop()
            for t in self.__nAut.out(init):
                if (t.cond & event) != buddy.bddfalse and t.dst in self.__nFin:
                    nInitAux.add(t.dst)
        self.__nInit = nInitAux
        uInitAux = set()
        while self.__uInit:
            init = self.__uInit.pop()
            for t in self.__uAut.out(init):
                if (t.cond & event) != buddy.bddfalse and t.dst in self.__uFin:
                    uInitAux.add(t.dst)
        self.__uInit = uInitAux
        foundP = len(self.__pInit) > 0
        foundN = len(self.__nInit) > 0
        foundU = len(self.__uInit) > 0
        if not foundN and not foundU:
            return Verdict.tt
        elif not foundP and not foundU:
            return Verdict.ff
        elif not foundP and not foundN:
            return Verdict.undefined
        elif not foundN:
            return Verdict.nf
        elif not foundP:
            return Verdict.nt
        else:
            return Verdict.unknown

def explicit_ltl(ltlstr, ap):
    # print(ltlstr)
    for atom in ap:
        ltlstr = ltlstr.replace('!' + atom, atom + 'ff')
    for atom in ap:
        # print(atom)
        j = 0
        while True:
            i = ltlstr.find(atom, j)
            if i == -1:
                break
            if (i+len(atom)) >= len(ltlstr) or ltlstr[i+len(atom)] != 'f':
                ltlstr = ltlstr[:i] + atom + 'tt' + ltlstr[i+len(atom):]
            j = i+1
    return ltlstr
