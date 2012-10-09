import sys
import re
import string
class Transition(object):
    def __init__(self, trans, alphabet):
        statelist = trans.split(",")
        self.string = trans
        self.fromstate, self.tostate = statelist[0], statelist[1]
        self.Is = []
        self.Os = []
        self.dirs = []
        for i in xrange(2,len(statelist)):
            inout = statelist[i].split("/")
            if inout[0][0] == "\"":
                inout[0] = (chr(int(inout[0][3:len(inout[0])-1],16)))
            self.Is.append(inout[0])
            if inout[1][0] == "\"":
                inout[1] = (chr(int(inout[1][3:len(inout[1])-1],16)))
            zero = re.compile(inout[0]+"$")
            zerofail = False
            onefail = False
            for i in alphabet:
                if zero.match(i):
                    zerofail = True
            if not zerofail:
                raise RuntimeError('Tape symbol: ' + inout[0] + " not in alphabet")
            if not inout[1] in alphabet:
                raise RuntimeError('Tape symbol: \"' + inout[1] + "\" not in alphabet")
            self.Os.append(inout[1])
            self.dirs.append(inout[2])

class State(object):
    def __init__(self, name):
        self.transdic = {}
        self.keys = []
        self.name = name
        self.transitions = []
    def addTransition(self,transition):
        self.transitions.append(transition)
    def finalizeTransitions(self):
        for i in xrange(len(self.transitions)):
            self.keys.append(tuple(self.transitions[i].Is))
    

                 
class TuringMachine(object):
    def __init__(self, TMFileName):
        TMFile = open(TMFileName, "r")
        self.tapepointers = []
        self.tapes = int(TMFile.readline().split()[0])
        for i in xrange(self.tapes):
            self.tapepointers.append(0)
        alphabet = list(set(["Blank","Unconditional","self"] + TMFile.readline().split()))
        self.alphabet = []
        for i in alphabet:
            if i[0] == "\"":
                self.alphabet.append(chr(int(i[3:len(i)-1],16)))
            elif i == "ascii":
                for j in xrange(0x100):
                    self.alphabet.append(chr(j))
            else:
                self.alphabet.append(i)
        self.alphabet = list(set(self.alphabet))
        states = list(set(TMFile.readline().split()))
        startstate = list(set(TMFile.readline().split()))[0]
        self.states = {}
        for i in states:
            self.states[i] = State(i)
        line = " "
        transitions = []
        while line != "":
            line = TMFile.readline()
            linesplit = list(set(line.split()))
            if linesplit:
                transitions += linesplit
        for i in transitions:
            tmptrans = Transition(i, self.alphabet)
            try:
                self.states[tmptrans.fromstate].addTransition(tmptrans)
            except KeyError:
                TMFile.close()
                raise RuntimeError('No such state: ' + tmptrans.fromstate)
        for i in self.states:
            self.states[i].finalizeTransitions()
        self.State = self.states[startstate]
        TMFile.close()

    def execute(self):
        self.TMtapes = []
        if len(filter (lambda a: a not in ["-dbs","-nl","-db","-o"], sys.argv)) <= 2:
            for i in xrange(self.tapes):
                tmpgo = raw_input("Use input directly (1) or file (anything else) for tape " + str(i+1) + " input? ")
                if tmpgo == "1":
                    tp = list(raw_input("Enter tape input: "))
                    if tp:
                        self.TMtapes.append(tp)
                    else:
                        self.TMtapes.append(["Blank"])
                else:
                    filename = raw_input("Name of tape file: ")
                    tpfile = open(filename, "rb")
                    tp = tpfile.read()
                    tpfile.close()
                    if tp:
                        self.TMtapes.append(list(tp))
                    else:
                        self.TMtapes.append(["Blank"])
        else:
            for i in xrange(self.tapes):
                filename = filter (lambda a: a not in ["-dbs","-nl","-db","-o"], sys.argv)[i+2]
                tpfile = open(filename, "rb")
                tp = tpfile.read()
                tpfile.close()
                if "-nl" in sys.argv:
                    tp = tp[:len(tp)-1]
                if tp:
                    self.TMtapes.append(list(tp))
                else:
                    self.TMtapes.append(["Blank"])
                
        for i in xrange(len(self.TMtapes)):
            tmptape = []
            matches = 0
            for j in xrange(len(self.TMtapes[i])):
                if matches == 0:
                    if self.TMtapes[i][j] == "B":
                        matches += 1
                    else:
                        tmptape.append(self.TMtapes[i][j])
                elif matches == 1:
                    if self.TMtapes[i][j] == "l":
                        matches += 1
                    else:
                        matches = 0
                        tmptape += ["B",self.TMtapes[i][j]]
                elif matches == 2:
                    if self.TMtapes[i][j] == "a":
                        matches += 1
                    else:
                        matches = 0
                        tmptape += ["B","l",self.TMtapes[i][j]]

                elif matches == 3:
                    if self.TMtapes[i][j] == "n":
                        matches += 1
                    else:
                        matches = 0
                        tmptape += ["B","l","a",self.TMtapes[i][j]]

                elif matches == 4:
                    if self.TMtapes[i][j] == "k":
                        matches = 0
                        tmptape.append("Blank")
                    else:
                        matches = 0
                        tmptape += ["B","l","a,","n",self.TMtapes[i][j]]
            self.TMtapes[i] = tmptape
        while True:
            tapestate = []
            for i in xrange(len(self.TMtapes)):
                tapestate.append(self.TMtapes[i][self.tapepointers[i]])
            tapestate = tuple(tapestate)
            try:
                trans = None
                for i in xrange(len(self.State.keys)):
                    tempfound = True
                    for j in xrange(len(self.State.keys[i])):
                        tempre = re.compile(self.State.keys[i][j])
                        if not tempre.match(tapestate[j]):
                            tempfound = False
                            break
                    if tempfound:  
                        trans = self.State.transitions[i]
                        break
                if not trans:
                    raise KeyError
                self.State = self.states[trans.tostate]
                for i in xrange(len(trans.Is)):
                    if not trans.Os[i] == "self":  
                        self.TMtapes[i][self.tapepointers[i]] = trans.Os[i]
                    if trans.dirs[i] == "L":
                        self.tapepointers[i] -= 1
                        if self.tapepointers[i] < 0:
                            raise RuntimeError("Tape #" + str(i) + " underflowed")                            
                    elif trans.dirs[i] == "R":
                        self.tapepointers[i] += 1
                        if self.tapepointers[i] > len(self.TMtapes[i])-1:
                            self.TMtapes[i].append("Blank")
                displayable = list(string.letters) + ['Blank',
                                                      '1','2','3','4','5','6','7','8','9','0',
                                                      " ","\n",",",".","[","]",";",":","'",'"',
                                                      "<",'>','?','/','\\','{','}','-','_','=',
                                                      '+','!','@','#','$','%','^','&','*','(',
                                                      ')','`','~','\t']
                if "-db" in sys.argv:
                    print trans.dirs
                    print self.State.name
                    for i in xrange(len(self.TMtapes)):
                        tmpstring = ""
                        for j in xrange(len(self.TMtapes[i])):
                            if j == self.tapepointers[i]:
                                if self.TMtapes[i][j] in displayable:
                                    tmpstring += "[%s] " % self.TMtapes[i][j]
                                else:
                                    tmpstring += "[\\x%x] " % ord(self.TMtapes[i][j])
                            else:
                                if self.TMtapes[i][j] in displayable:
                                    tmpstring += "%s " % self.TMtapes[i][j]
                                else:
                                    tmpstring += "\\x%x " % ord(self.TMtapes[i][j])
                        print tmpstring
                        print self.tapepointers[i]  
                    print "\n"
                elif "-dbs" in sys.argv:
                    print trans.dirs
                    print self.State.name
                    for i in xrange(len(self.TMtapes)):
                        tmpstring = ""
                        for j in xrange(len(self.TMtapes[i])):
                            if j == self.tapepointers[i]:
                                if self.TMtapes[i][j] in displayable:
                                    tmpstring += "[%s] " % self.TMtapes[i][j]
                                else:
                                    tmpstring += "[\\x%x] " % ord(self.TMtapes[i][j])
                            else:
                                if self.TMtapes[i][j] in displayable:
                                    tmpstring += "%s " % self.TMtapes[i][j]
                                else:
                                    tmpstring += "\\x%x " % ord(self.TMtapes[i][j])
                        print tmpstring
                        print self.tapepointers[i]  
                    print "\n"
                    raw_input("Press enter to continue")
            except KeyError:
                print "Halted due to not finding a transition for: " + str(tapestate) + " for state: " + self.State.name
                return
        if "-o" in sys.argv:
            for i in xrange(len(self.TMtapes)):
                outfile = open("Tape" + str(i),'w')
                for j in self.TMtapes[i]:
                    outfile.write(j)
                outfile.close()
        else:
            for i in xrange(len(self.TMtapes)):
                print "Tape %d" % (i+1)
                tmpstring = ""
                for j in xrange(len(self.TMtapes[i])):
                    if j == self.tapepointers[i]:
                        if self.TMtapes[i][j] in displayable:
                            tmpstring += "[%s] " % self.TMtapes[i][j]
                        else:
                            tmpstring += "[\\x%x] " % ord(self.TMtapes[i][j])
                    else:
                        if self.TMtapes[i][j] in displayable:
                            tmpstring += "%s " % self.TMtapes[i][j]
                        else:
                            tmpstring += "\\x%x " % ord(self.TMtapes[i][j])
                print tmpstring
            
if len(filter (lambda a: a not in ["-dbs","-nl","-db","-o"], sys.argv)) == 1:
    filename = raw_input("name of TM file: ")
else:
    filename = sys.argv[1]
TM = TuringMachine(filename)
TM.execute()
