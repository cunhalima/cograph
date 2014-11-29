#!/usr/bin/env python3
#
# Copyright (C) 2014 Alex Reimann Cunha Lima
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
#
import sqlite3

# some globals
MAX_ORDER   =   5
VF_DELTA    =   1
INF_GIRTH   =   5
OP_VERT  = '.'
OP_UNION = '0'
OP_JOIN  = '1'
OPERATIONS = (OP_VERT, OP_UNION, OP_JOIN)
enableColouringPrint = False
cgset = {}
cglst = []
nullGraph = None

## GRAPH ENCODING -------------------------------------------------------------------
enc_set = {}
enc_lst = []
enc_nod = []

class ENode:
    def __init__(self, op, a, b):
        self.op = op
        self.a = a
        self.b = b
        self.string = self.op

    def __str__(self):
        return self.string

    def sort(self):
        if self.a != None and self.b != None:
            #dbg = False
            #if self.a.string == '..0' and self.b.string == '..1' and self.op == OP_JOIN:
            #    dbg = True
            #if self.a.string == '.' and self.b.string == '...01' and self.op == OP_JOIN:
            #    dbg = True
            # Cotrees a and b already sorted
            # if same op, they should all be on node.b
            if self.a.op == self.op or self.a.op != self.op:
            #if True:
                #if dbg:
                #    print("EITA")
                # create list of codes
                lst = []
                n = self.a
                while n.op == self.op:
                    lst.append(n.a)
                    n = n.b
                lst.append(n)
                n = self.b
                while n.op == self.op:
                    lst.append(n.a)
                    n = n.b
                lst.append(n)
                #if dbg:
                #    for i in lst:
                #        print(">>", i.string)
                lst = sorted(lst, key = lambda x: x.string)
                #if dbg:
                #    for i in lst:
                #        print(">>", i.string)
                bstr = ""
                for i in range(1, len(lst)):
                    bstr += lst[i].string
                for i in range(len(lst) - 2):
                    bstr += self.op
                self.a = lst[0]
                self.b = enc_nod[enc_set[bstr]]
                #if dbg:
                #    print(self.a.string)
                #    print(self.b.string)
                #    print(len(lst))
            #elif self.a.op == self.op:
            #    self.a, self.b = self.b, self.a
            elif self.b.op != self.op:
                if self.a.string > self.b.string:
                    self.a, self.b = self.b, self.a
            self.string = self.a.string + self.b.string + self.op
        if self.string in enc_set:
            return enc_nod[enc_set[self.string]]
        addEncoding(self.string, self)
        return self

def MakeENode(op, a, b):
    if op == '' or op == OP_VERT:
        s = op
    else:
        s = a.string + b.string + op
        if s in enc_set:
            return enc_nod[enc_set[s]]
        s = b.string + a.string + op
    if s in enc_set:
        return enc_nod[enc_set[s]]
    node = ENode(op, a, b)
    return node.sort()
                
def validateCotree(s):
    vnode = enc_nod[enc_set[OP_VERT]]
    stack = []
    for op in s:
        if op == OP_VERT:
            stack.append(vnode)
        else:
            if len(stack) < 2:
                return None
            b = stack.pop()
            a = stack.pop()
            stack.append(MakeENode(op, a, b))
    if len(stack) != 1:
        return None
    n = stack.pop()
    if n == None:
        return None
    return n.string

def addEncoding(s, node):
    n = len(enc_lst)
    enc_set[s] = n
    enc_lst.append(s)
    enc_nod.append(node)
    return n

#def printAll():
#    for i in range(len(enc_lst)):
#        print(i, ':', enc_lst[i])

#def runStrings():
#    MAXCTSIZE = 4
#    def makeStrings(s, c):
#        if (c == 0):
#            #if len(enc_lst) == 16:
#            #    print('UU', s)
#            go(s)
#            return
#        for x in OPERATIONS:
#            makeStrings(s + x, c - 1)
#    for x in range(MAXCTSIZE):
#        makeStrings('', 2 * x + 1)
#
#addEncoding('', None)
#addEncoding(OP_VERT, ENode(OP_VERT, None, None))

def genGraphs(cur = None):
    for i in range(MAX_ORDER + 1):
        makeOrder(i, cur)

def initEncoding():
    global orderBase
    global currentOrder
    #MakeENode('', None, None)
    #LoadGraph('')
    #MakeENode(OP_VERT, None, None)

    orderBase = []
    #orderBase.append(0)
    #orderBase.append(len(enc_lst) - 1)

    currentOrder = 0
    currentOrder = -1
    #currentOrder = 1

    #genGraphs()

def makeOrder(order, cur):
    global currentOrder
    global orderBase

    if (order == currentOrder + 1):
        currentOrder += 1
        orderBase.append(len(enc_lst))
    elif order > currentOrder + 1:
        return
    orderMax = (order // 2) + 1
    if order == 0:
        n = MakeENode('', None, None)
        writeCGData(n, None, None, cur)
        return
    elif order == 1:
        n = MakeENode(OP_VERT, None, None)
        writeCGData(n, None, None, cur)
        return
    for i in range(1, orderMax):
        orderA = i
        orderB = order - orderA

        startA = orderBase[orderA]
        endA = orderBase[orderA + 1]
        startB = orderBase[orderB]
        endB = orderBase[orderB + 1]
        for j in range(startA, endA):
            for k in range(startB, endB):
                nodeA = enc_nod[j]
                nodeB = enc_nod[k]
                n = MakeENode(OP_UNION, nodeA, nodeB)
                writeCGData(n, nodeA, nodeB, cur)
                n = MakeENode(OP_JOIN, nodeA, nodeB)
                writeCGData(n, nodeA, nodeB, cur)

## GRAPH BUILDING -------------------------------------------------------------------

def encodeEmpty(n):
    s = ""
    for i in range(n):
        s += OP_VERT
    for i in range(n - 1):
        s += OP_UNION
    return s

def encodeOperation(op, a, b):
    assert op in OPERATIONS
    an = enc_nod[enc_set[a]]
    bn = enc_nod[enc_set[b]]
    n = MakeENode(op, an, bn)
    return n.string

# Given an encoded cotree "enc",
# delete its kth (countint from 0) vertex and returns
# a valid encoded cotree
def delCotreeVertex(enc, k):
    stack = []
    out = ""
    for i in range(len(enc)):
        c = enc[i]
        if c == '.':
            if k == 0:
                stack.append(0)
            else:
                stack.append(1)
                out += c
            k -= 1
        else:
            if len(stack) < 2:
                return None
            b = stack.pop()
            a = stack.pop()
            stack.append(a | b)
            if (a & b) == 1:
                out += c
    if len(stack) != 1:
        return None
    return validateCotree(out)
    #return out

def induceCotree(enc, indset):
    if enc == "":
        return ""
    stack = []
    out = ""
    p = 0
    #print("D) " + enc)
    #print("E) " + str(indset))
    for i in range(len(enc)):
        c = enc[i]
        if c == '.':
            if not indset[p]:
                stack.append(0)
            else:
                stack.append(1)
                out += c
            p += 1
        else:
            if len(stack) < 2:
                return None
            b = stack.pop()
            a = stack.pop()
            stack.append(a | b)
            if (a & b) == 1:
                out += c

    # ..1..0
    # FITA: 00
    # PILHA: 1 0 0 
    #
    #print("AAAAAAAAAAAAAAAAAAAAAAAAAAA" + out)
    if len(stack) != 1:
        return None
    return validateCotree(out)

def LoadGraph(encodedCotree, cl=0):
    if encodedCotree == "":
        return MakeCoNode(None, None, None)
    stack = []
    forceClass = 0
    for i in range(len(encodedCotree)):
        c = encodedCotree[i]
        assert c in OPERATIONS
        if i == len(encodedCotree) - 1:
            forceClass = cl
        if c == '.':
            a = None
            b = None
        else:
            if len(stack) < 2:
                return None
            a = stack.pop()
            b = stack.pop()
        stack.append(MakeCoNode(c, a, b, forceClass))
    if len(stack) != 1:
        return None
    return stack.pop()

# PRONTO
def MakeCoNode(op, a, b, cl=0):
    if op != None:
        assert op in OPERATIONS
        if op == OP_VERT:
            assert a == None and b == None
        else:
            assert a != None and b != None
        if a == None or b == None:
            cmd = op
        else:
            apos = len(a.cmd)
            bpos = len(b.cmd)
            while a.cmd[apos - 1:apos] == op: apos -= 1
            while b.cmd[bpos - 1:bpos] == op: bpos -= 1
            acmd = a.cmd[:apos]
            bcmd = b.cmd[:bpos]
            if acmd > bcmd:
                acmd, bcmd = bcmd, acmd
            cmd = acmd + bcmd + a.cmd[apos:] + b.cmd[bpos:] + op
    else:
        a = None
        b = None
        cmd = ""
    if cmd in cgset:
        o = cgset[cmd]
    else:
        o = CoNode(op, a, b, cmd, len(cglst), cl)
        cgset[cmd] = o                              # Should be before o.build() because build() sometimes
                                                    # attempts to access the graphs, own cgset[cmd]
        o.build()
        cglst.append(o)
    return o
        
class CoNode:
    def __init__(self, op, a, b, cmd, index, cl=0):
        self.id = index
        # cotree data
        self.op = op
        self.a = a
        self.b = b
        self.cmd = cmd
        self.height = 0                             # cotree height
        self.numchildren = 0                        # number root's children
        # cograph data
        self.V = []
        self.VF = []                                # vertces flags
        self.VDN = []                               # number of delta neighbourts
        self.numV = 0
        self.numE = 0
        # cograph characteristics
        self.cpClass = 1                            # null graphs are class one
        self.maxDegree = 0                          # 
        self.maxEDegree = 0                         # 
        self.minDegree = 0                          # 
        self.connected = True                       # null graphs are connected
        self.overfull = False                       # null graphs are not overfull ??
        self.SO = False
        self.deltaSubgraphs = {}
        self.complete = True                        # null graphs are complete
        self.cycle = False                          # null graphs have no cycles
        self.clique = 0                             # clique number
        self.combinations = 0                       # number of different combinations of graphs that can build me
        self.complement = self
        self.fullHeight = True
        self.girth = INF_GIRTH
        self.colors = ''
        self.ovsub = None                           # the overfull subgraph
        self.threshold = True
        self.solved = False
        self.chromNum = 0
        self.chromInd = 0
        self.strangers = False                      # nao tem nenhum par de vertices que nao sao vizinhos
        self.c4 = False
        self.hasstar = False

    def addEdge(self, x1, x2):
        self.V[x1].append(x2)
        self.V[x2].append(x1)
        self.numE += 1

    # Find interesting Delta Subgraphs
    def calcDeltaSubgraphs(self):
        # No interesting delta subgraphs
        if self.numV <= 1:
            return
        # the graph itself is an interesting delta Subgraph
        if self.overfull:
            return
        if self.op == OP_UNION:
            return
        for i in range(self.numV):
            enc = delCotreeVertex(self.cmd, i)
            #enc = validateCotree(enc2)
            if not enc in cgset:
                print(self.id, self.cmd)
                #print(enc2)
                print(enc)
            g = cgset[enc]
            if g.maxDegree == self.maxDegree:
                self.deltaSubgraphs[g.id] = g

    def calcSO(self):
        self.SO = False
        self.ovsub = None
        if self.overfull:
            self.SO = True
            self.ovsub = self
            return
        if self.op == OP_UNION:
            self.SO = self.a.SO or self.b.SO
            return
        elif self.op == OP_JOIN:
            for gid, g in self.deltaSubgraphs.items():
                if g.SO:
                    self.SO = True
                    self.ovsub = g.ovsub
                    break
        #for g in (self.a, self.b):
        #    if g != None:
        #        if g.maxDegree == self.maxDegree and g.SO:
        #            self.SO = True

    #def isProperMajorVertex(self, x):
    #    dgsum = 0
    #    for y in self.V[x]:                         # for each vertex in Neighbourhood of x
    #        dgsum += len(self.V[y])                 #   get its degree and sum it up
    #    if dgsum >= self.maxDegree * (self.maxDegree - 1) + 2:
    #        return True
    #    return False
    #
    #def getPMNList(self):
    #    p = []
    #    for u in range(self.numV):
    #        if self.isProperMajorVertex(u):
    #            p.append(1)
    #        else:
    #            p.append(0)
    #    return p
    #
    # Count the number of proper major vertices in Neighbourhood
    #def countPMN(self):
    #    pc = []
    #    p = self.getPMNList()
    #    for x in range(self.numV):
    #        count = 0
    #        for y in self.V[x]:
    #            count += p[y]
    #        pc.append(count)
    #    return pc
    #
    #def calcSubgraphOverfull(self):
    #    if self.overfull:
    #        self.sgOverfull = True
    #        return
    #    if not self.connected:
    #        self.sgOverfull = self.recursiveFindSO(self)
    #        return
    #    pc = self.countPMN()
    #    S = []
    #    for u in range(self.numV):
    #        if pc[u] <= 1:
    #            S.append(u)
    def fastColor(self):
        Edict = {}
        Elist = []
        V = []
        numV = self.numE
        numE = 0
        #print('x', self.numV)
        #print('x', self.numE)
        for i in range(self.numE):
            V.append([])
        for i in range(self.numV):      # for each vertex
            for j in self.V[i]:             # for each other vertex
                if i >= j: continue
                Edict[(i,j)] = len(Elist)
                Elist.append((i,j))
                #print((i, j))

        for e in range(self.numE):
            pair = Elist[e]
            for k in range(2):
                i = pair[k]
                other = pair[k^1]
                for j in self.V[i]:
                    if j == other: continue
                    if i < j:
                        x, y = i, j
                    else:
                        x, y = j, i
                    n = Edict[(x, y)]
                    V[e].append(n)
                    if e < n:
                        numE += 1

        # now we have a line graph
        #color it using that algorithm
        #print(numV)
        #print(numE)
        exists = []
        AM = []
        for i in range(numV):
            exists.append(True)
            AM.append([])
            for j in range(numV):
                AM[i].append(0)
        #print(V)
        for i in range(numV):
            for j in V[i]:
                AM[i][j] = 1
                AM[j][i] = 1
        #print(AM)
        colorsUsed = numV
        while True:
            largestC = -1
            largestPair = None
            for i in range(numV):
                if not exists[i]: continue
                for j in range(numV):
                    if not exists[j]: continue
                    if i >= j: continue
                    if AM[i][j] != 0: continue
                    c = 0
                    for k in range(numV):
                        c += AM[i][k] & AM[j][k]
                    if c > largestC:
                        largestC = c
                        largestPair = (i, j)
                    
            if largestPair == None:
                break
            # Achei o par que vou mesclar
            i = largestPair[0]
            j = largestPair[1]
            for k in range(numV):
                AM[i][k] |= AM[j][k]
                AM[j][k] = 0
                AM[k][i] |= AM[k][j]
                AM[k][j] = 0
            exists[j] = False
            colorsUsed -= 1
        if colorsUsed != self.maxDegree:
            print(self.id)
            print(self.cmd)
            print("COLOR ERROR")

    def colorViolation(self, Ec, Ee, i):
        for j in Ee[i]:
            if Ec[i] == Ec[j]:
                return True
        return False

    def recursiveColor(self, Ec, Ee, i, numcolors):
        if i == self.numE:
            return True
        for k in range(self.maxDegree):
            Ec[i] = k + 1
            if self.colorViolation(Ec, Ee, i):
                continue
            if self.recursiveColor(Ec, Ee, i + 1, self.maxDegree):
                return True
        Ec[i] = 0
        return False

    def colorEdges(self):
        #if self.id == 841:
        #    return
        #if self.id == 905:
        #    return
        #if self.id == 1129:
        #    return
        print('coloring', self.id)
        Ex = []
        Ey = []
        Ec = []
        Ee = []
        for x in range(self.numV):
            for y in self.V[x]:
                if x > y: continue
                Ex.append(x)
                Ey.append(y)
                Ec.append(0)
                Ee.append([])
        for i in range(self.numE):
            for j in range(self.numE):
                if i == j: continue
                if Ex[i] == Ex[j] or Ex[i] == Ey[j] or Ey[i] == Ex[j] or Ey[i] == Ey[j]:
                    Ee[i].append(j)
        res = self.recursiveColor(Ec, Ee, 0, 1)
        if enableColouringPrint:
            self.printColoring(Ec, Ex, Ey)
        for i in Ec:
            self.colors += ':' + str(i)
        if not res:
            print(self.colors)
            raw_input('aaa')
        return res

    def printColoring(self, Ec, Ex, Ey):
        print("Coloring:")
        for x1 in range(len(self.V)):
            el = self.V[x1]
            print(str(x1) + ": ", end='')
            for x2 in el:
                print(str(x2)+"(", end='')
                for k in range(self.numE):
                    if (Ex[k] == x1 and Ey[k] == x2) or (Ex[k] == x2 and Ey[k] == x1):
                        print(Ec[k], end='')
                        break
                print("), ", end='')
            print("")

    def calcOverfull(self):
        if self.numE > self.maxDegree * (self.numV // 2):
            self.overfull = True
        else:
            self.overfull = False

    def calcClass(self):
        if self.SO:
            self.cpClass = 2
        else:
            self.cpClass = 1
        self.chromInd = self.maxDegree + self.cpClass - 1

        #if self.overfull:
        #    self.cpClass = 2
        #    return
        #if not self.connected:
        #    # Acho que isso eh desnecessario ja que agora calculo o SO mais ou menos 
        #    self.cpClass = 1
        #    for component in (self.a, self.b):
        #        if component.cpClass == 2 and component.maxDegree == self.maxDegree:
        #            self.cpClass = 2
        #    return
        #if self.colorEdges():
        #    self.cpClass = 1
        #    return
        #self.cpClass = 2
        #=== DEPOIS POR DE VOLTA
        #if self.cpClass == 1:
        #    self.colorEdges()
        #if self.cpClass == 1:
        #    self.fastColor()

    def calcCore(self):
        if self.complete:
            self.core = self
        elif self.op == OP_VERT:
            self.core = self
        elif self.op == OP_UNION:
            if self.a.maxDegree > self.b.maxDegree:
                self.core = self.a.core
            elif self.b.maxDegree > self.a.maxDegree:
                self.core = self.b.core
            else:
                self.core = cgset[encodeOperation(OP_UNION, self.a.core.cmd, self.b.core.cmd)]
        elif self.op == OP_JOIN:
            adegree = self.a.maxDegree + self.b.numV
            bdegree = self.b.maxDegree + self.a.numV
            if adegree > bdegree:
                self.core = self.a.core
            elif bdegree > adegree:
                self.core = self.b.core
            else:
                #corecmd = encodeOperation(OP_JOIN, self.a.core.cmd, self.b.core.cmd)
                self.core = cgset[encodeOperation(OP_JOIN, self.a.core.cmd, self.b.core.cmd)]
                #if corecmd == self.cmd:
                #    self.core = self
                #else:
                #    self.core = cgset[corecmd]
        else:
            print("ERORR WHAT DOING HERE?")

    def calcFlags(self):
        while len(self.VF) < self.numV:
            self.VF.append(0)
            self.VDN.append(0)

        for u in range(self.numV):
            if len(self.V[u]) == self.maxDegree:
                self.VF[u] |= VF_DELTA

        for u in range(self.numV):
            if self.VF[u] & VF_DELTA:
                self.VDN[u] += 1
            for w in self.V[u]:
                if self.VF[w] & VF_DELTA:
                    self.VDN[u] += 1

    def induce(self, inset):
        #print("A) OOOOOOOO " + self.cmd)
        enc = induceCotree(self.cmd, inset)
        #print("B) OOOOOOOO " + enc)
        return cgset[enc]

    def calcSemiCore(self):
        if self.complete:
            self.semiCore = self
            return
        induceSet = []
        for u in range(self.numV):
            if self.VDN[u] > 0:
                induceSet.append(True)
            else:
                induceSet.append(False)
        self.semiCore = self.induce(induceSet)

    def calcChildren(self):
        self.numchildren = 2
        if self.a.op == self.op:
            self.numchildren += self.a.numchildren - 1
        if self.b.op == self.op:
            self.numchildren += self.b.numchildren - 1

    def calcHeight(self):
        ha = self.a.height
        hb = self.b.height
        if self.a.op != self.op:
            ha += 1
        if self.b.op != self.op:
            hb += 1
        self.height = max(ha, hb)
        if (ha == hb) and (self.a.fullHeight and self.b.fullHeight):
            self.fullHeight = True
        else:
            self.fullHeight = False
        #if self.b.cmd == '.' and self.a.cmd == '..1' and self.op == OP_UNION:
        #    print('aaaaaaaa')
        #    print(self.cmd)
        #    print(self.fullHeight)
        #    print(ha)
        #    print(hb)
        #    if (ha == hb) and (self.a.fullHeight and self.b.fullHeight):
        #        print('ooo')

    def union(self):
        self.numV = self.a.numV + self.b.numV
        self.numE = self.a.numE + self.b.numE
        while len(self.V) < self.numV:
            self.V.append([])
        for x1 in range(self.a.numV):
            edges = self.a.V[x1]
            for x2 in edges:
                self.V[x1].append(x2)
        splitpos = self.a.numV
        for x1 in range(self.b.numV):
            edges = self.b.V[x1]
            for x2 in edges:
                self.V[splitpos + x1].append(splitpos + x2)
        self.maxDegree = max(self.a.maxDegree, self.b.maxDegree)
        self.minDegree = min(self.a.minDegree, self.b.minDegree)
        self.maxEDegree = max(self.a.maxEDegree, self.b.maxEDegree)
        self.connected = False
        self.cycle = self.a.cycle or self.b.cycle
        self.girth = min(self.a.girth, self.b.girth)
        self.chromNum = max(self.a.chromNum, self.b.chromNum)
        self.strangers = True
        self.c4 = self.a.c4 or self.b.c4
        self.hasstar = self.a.hasstar or self.b.hasstar

    def join(self):
        self.union()
        for x1 in range(self.a.numV):
            for y in range(self.b.numV):
                x2 = y + self.a.numV
                self.addEdge(x1, x2)
        self.maxDegree = max(self.a.maxDegree + self.b.numV, self.b.maxDegree + self.a.numV)
        self.minDegree = min(self.a.minDegree + self.b.numV, self.b.minDegree + self.a.numV)
        self.connected = True
        if self.a.numE > 0 or self.b.numE > 0:
            self.cycle = True
            self.girth = 3
        elif self.a.numV > 1 and self.b.numV > 1:
            self.cycle = True
            self.girth = min(self.girth, 4)
        Mmax = self.a.maxDegree + self.b.maxDegree
        Amax = self.a.maxEDegree
        Bmax = self.b.maxEDegree
        if self.a.numE > 0:
            Amax += self.b.numV + self.b.numV
        if self.b.numE > 0:
            Bmax += self.a.numV + self.a.numV
        self.maxEDegree = max(Mmax, Amax, Bmax)
        self.chromNum = self.a.chromNum + self.b.chromNum
        self.strangers = self.a.strangers or self.b.strangers
        self.c4 = self.a.c4 or self.b.c4
        if self.a.strangers and self.b.strangers:
            self.c4 = True
        if self.numV >= 3 and not self.cycle:
            self.hasstar = True
        else:
            self.hasstar = False

    def singleton(self):
        self.numV = 1
        self.numE = 0
        self.V.append([])
        self.maxDegree = 0
        self.minDegree = 0
        self.connected = True
        self.overfull = False
        self.SO = False
        self.cpClass = 1
        self.cycle = False
        self.a = nullGraph
        self.b = nullGraph
        self.height = 0
        self.numchildren = 0
        self.clique = 1
        self.chromNum = 1
        self.chromInd = 0

    def calcComplete(self):
        if self.numE == (self.numV * (self.numV - 1)) // 2:
            self.complete = True
        else:
            self.complete = False

    def calcClique(self):
        if self.op == OP_UNION:
            self.clique = max(self.a.clique, self.b.clique)
        elif self.op == OP_JOIN:
            self.clique = self.a.clique + self.b.clique

    def plantholt(self):
        if self.op != OP_JOIN: return
        if (self.numV & 1) == 1: return
        if self.numV < 2: return
        
        
        pass

    def build(self):
        global enableColouringPrint
        if self.op == None:             # null graph
            self.a = self
            self.b = self
        elif self.op == OP_VERT:
            self.singleton()
        else:
            if self.op == OP_UNION:
                self.union()
            elif self.op == OP_JOIN:
                self.join()
            else:
                print("ERROR: unknown operation")
            # calculate if it is a threshold graph
            if not((self.a.threshold and self.b.op == OP_VERT) or (self.b.threshold and self.a.op == OP_VERT)):
                self.threshold = False
            self.calcChildren()
            self.calcHeight()
            self.calcOverfull()
            self.calcDeltaSubgraphs()
            self.calcSO()
            self.calcClass()
            #if self.cpClass == 1 and self.SO == True:
            #    print("ERROR CL1 SO")
            #    print(self.cmd)
            #    enableColouringPrint = True
            #    if self.colorEdges():
            #        print("Found coloring")
            #    else:
            #        print("Didn't find coloring")
            #    enableColouringPrint = False
            #
            #    for gid, g in self.deltaSubgraphs.items():
            #        if g.SO:
            #            print("aqui")
            #            print(g.cmd)
            #            break
            #
            #    for component in (self.a, self.b):
            #        if component.cpClass == 2 and component.maxDegree == self.maxDegree:
            #            print("vai 2")
            #
            #    exit(0)
            #if self.cpClass == 2 and self.SO == False:
            #    print("ERROR CL2 NSO")
            #    exit(0)
        self.calcComplete()
        self.calcCore()
        self.calcFlags()
        self.calcSemiCore()
        self.calcClique()
        self.plantholt()

    def edgesDescription(self):
        s = ""
        for x1 in range(len(self.V)):
            el = self.V[x1]
            s += str(x1) + ": "
            for x2 in el:
                s += str(x2) + " "
            s += "\n"
        return s

    def fullDescription(self):
        s = "CG(" + str(self.id) + ") {\n"
        s += "vertices   = " + str(self.numV) + "\n"
        s += "edges      = " + str(self.numE) + "\n"
        s += "cotree     = \"" + str(self.cmd) + "\"\n"
        s += "max degree = " + str(self.maxDegree) + "\n"
        s += "connected  = " + str(self.connected) + "\n"
        s += "overfull   = " + str(self.overfull) + "\n"
        s += "class      = " + str(self.cpClass) + "\n"
        s += self.edgesDescription()
        s += "}"
        return s

    def __str__(self):
        s = "CG(" + str(self.id) + ") {\n"
        s += self.edgesDescription()
        s += "}"
        return s


#np = MakeCoNode('.', None, None)
#na = MakeCoNode('1', np, np)
#nb = MakeCoNode('0', np, na)
#nc = MakeCoNode('0', np, np)
#nd = MakeCoNode('1', nc, nb)
#print("np = " + np.cmd)
#print("na = " + na.cmd)
#print("nb = " + nb.cmd)
#print("nc = " + nc.cmd)
#print("nd = " + nd.cmd)
#print(len(cgset))
#print(na)
#print(na.fullDescription())
#print(nb.fullDescription())
#print(nc.fullDescription())
#print(nd.fullDescription())

#zz = LoadGraph('...10..01')
#zz = LoadGraph('..1')
#zz = LoadGraph('.')
#zz = LoadGraph('...11')
#zz = LoadGraph('....111')
#zz = LoadGraph('.....1111')
#zz = LoadGraph('.........11010111')
#print(zz.fullDescription())
#zz.colorEdges()

import sys

def updateGraphs(cur):
    tr = str.maketrans('01', '10')
    for g in cglst:
        ccmd = validateCotree(g.cmd.translate(tr))
        cid = -1
        if ccmd != None:
            cg = cgset[ccmd]
            g.complement = cg
            cid = g.complement.id
        if g.solved:
            solved = 1
        else:
            solved = 0
        cur.execute("UPDATE gr SET combinations=%d,complement=%d,solved=%d WHERE id=%d" % (g.combinations, cid, solved, g.id))

def writeGraphData():
    con = sqlite3.connect('old.db')
    with con:
        cur = con.cursor()    
        cur.execute("DROP TABLE IF EXISTS gr")
        cur.execute("DROP TABLE IF EXISTS op")
        cur.execute("CREATE TABLE gr("
                    "id INT PRIMARY KEY, "
                    "cotree TEXT, "
                    "colors TEXT, "
                    "n INT, "
                    "m INT, "
                    "hasstar INT, "
                    "c4 INT, "
                    "solved INT, "
                    "threshold INT, "
                    "complete INT, "
                    "clique INT, "
                    "combinations INT, "
                    "complement INT, "
                    "connected INT, "
                    "cycle INT, "
                    "girth INT, "
                    "maxdeg INT, "
                    "mindeg INT, "
                    "maxedeg INT, "
                    "ov INT, "
                    "so INT, "
                    "ovsub INT, "
                    "class INT, "
                    "core INT, "
                    "semicore INT, "
                    "height INT, "
                    "fullheight INT, "
                    "numchildren INT, "
                    "chromnum INT, "
                    "chromind INT) WITHOUT ROWID")
        #cur.execute("INSERT INTO Graph VALUES(1, '..0')")
        cur.execute("CREATE TABLE op(op INT, g INT, a INT, b INT)")
        #cur.execute("INSERT INTO Operation VALUES(1, 1, 1)")
        genGraphs(cur)
        updateGraphs(cur)


    #f.close()
    #for x in cglst:
    #    if x.overfull:
    #        ov = 1
    #    else:
    #        ov = 0
    #    if x.SO:
    #        so = 1
    #    else:
    #        so = 0
    #    if x.core.cycle:
    #        cc = 1
    #    else:
    #        cc = 0
    #    a = x.a
    #    b = x.b
    #    if x.b.numV > x.a.numV:
    #        a, b = b, a
    #    f.write('%5d' % x.id)
    #    f.write(' %3d %3d' % (x.numV, x.numE))
    #    f.write(' %2d' % cc)
    #    f.write(' %2d' % x.maxDegree)
    #    f.write('  %d' % ov)
    #    f.write('  %d' % so)
    #    f.write(' %dX%d=%d' % (a.cpClass, b.cpClass, x.cpClass))
    #    f.write(' %5d' % a.id)
    #    f.write(' %5d' % b.id)
    #    f.write(' %5d' % x.core.id)
    #    f.write(' %5d' % x.semiCore.id)
    #    f.write(' %2d' % x.height)
    #    f.write(' %2d' % x.numchildren)
    #    f.write(' %30s' % (x.cmd + '#'))
    #    f.write('\n')
    #f.close()

def writeCGData(n, a, b, cur):
    if cur == None:
        return
    creating = False
    if n.string in cgset:
        n = cgset[n.string]
    else:
        n = LoadGraph(n.string)
        creating = True
    if a != None and b != None:
        a = cgset[a.string]
        b = cgset[b.string]
        if b.numV > a.numV:
            a, b = b, a
    if n.op == None:
        op = 3
    elif n.op == OP_VERT:
        op = 2
    elif n.op == OP_UNION:
        op = 0
    elif n.op == OP_JOIN:
        op = 1
    if n.op != OP_JOIN:
        n.solved = True
    elif a.maxDegree < b.maxDegree:
        n.solved = True
    elif a.maxDegree == b.maxDegree:
        if a.cpClass == 1 and b.cpClass == 1:
            n.solved = True
    elif a.maxDegree > b.maxDegree:
        if a.numV == b.numV:
            n.solved = True
    if a != None and b != None:
        cur.execute("INSERT INTO op VALUES(%d, %d, %d, %d)" % (op, n.id, a.id, b.id))
    n.combinations += 1
    if not creating: return


    if n.c4:
        c4 = 1
    else:
        c4 = 0
    if n.overfull:
        ov = 1
    else:
        ov = 0
    if n.SO:
        so = 1
    else:
        so = 0
    ovsub = 0
    if n.ovsub != None:
        ovsub = n.ovsub.id
    if n.cycle:
        cc = 1
    else:
        cc = 0
    if n.connected:
        connected = 1
    else:
        connected = 0
    if n.fullHeight:
        fullHeight = 1
    else:
        fullHeight = 0
    if n.threshold:
        threshold = 1
    else:
        threshold = 0
    if n.hasstar:
        hasstar = 1
    else:
        hasstar = 0
    cur.execute("INSERT INTO gr VALUES(%d, '%s', '%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)" %
            (n.id, n.cmd, n.colors, n.numV, n.numE, hasstar, c4, 0, threshold, n.complete, n.clique,
            n.combinations, n.complement.id, connected, cc, n.girth, n.maxDegree, n.minDegree, n.maxEDegree,
            ov, so, ovsub, n.cpClass, n.core.id, n.semiCore.id,
            n.height, fullHeight, n.numchildren, n.chromNum, n.chromInd))

def makeFirstGraphs():
    global nullGraph
    nullGraph = LoadGraph("")               # First build the null graph

def loadGraphData():
    count = 1000
    print("LOADING:: ", end='', flush=True)
    f = open('ALLCOGRAPHS', 'r')
    for line in f:
        count -= 1
        if count == 0:
            break
        #n, m, Delta, overfull, so, cpClass, cmd = line.strip().split()
        cmd = line.strip()
        cmd = validateCotree(cmd)
        #cpClass, cmd = line.strip().split()
        #LoadGraph(cmd, int(cpClass))
        #LoadGraph(cmd)
        #print(cpClass)
        #print(cmd)
        LoadGraph(cmd)
        #print(cmd + ' -> ' + str(validateCotree(cmd)))
    f.close()
    print(" done!", flush=True)

def buildGraphData():
    print("BUILDING: ", end='', flush=True)
    f = open('ALLCOGRAPHS', 'r')
    for line in f:
        enc = line.strip()
        enc = validateCotree(enc)
        if enc != None:
            if enc not in cgset:
                zz = LoadGraph(enc)
            else:
                zz = cgset[enc]
    f.close()
    print(" done!", flush=True)
 

def run():
    makeFirstGraphs()
    loadGraphData()
    #buildGraphData()
    #writeGraphData()

#def runStrings():
#    MAXCTSIZE = 8
#    cgset = {}
#    def makeStrings(s, c):
#        if (c == 0):
#            s = validateCotree(s)
#            if s != None:
#                if s not in cgset:
#                    cgset[s] = True
#                    print(s)
#            return
#        for x in OPERATIONS:
#            makeStrings(s + x, c - 1)
#    for x in range(MAXCTSIZE):
#        makeStrings('', 2 * x + 1)
#
#
#run()
#print(validateCotree('...00...011'))
#print(validateCotree('...0...0011'))
#print(validateCotree('....00..011'))
#if '..0' > '...00':
#    print('a')
#def runStringsTwo():
#    MAXCTSIZE = 8
#    cgset = {}
#    def makeStrings(enc, gone, left, stack):
#        if (c == 0):
#            s = validateCotree(s)
#            if s != None:
#                if s not in cgset:
#                    cgset[s] = True
#                    print(s)
#            return
#        for x in OPERATIONS:
#            makeStrings(s + x, c - 1)
#    for x in range(MAXCTSIZE):
#        makeStrings('', 2 * x + 1)
#
#print(validateCotree("...00"))
#runStrings()
#print(delCotreeVertex("..0...11..111..00", 7))
#print(cglst[40].fullDescription())
#print(cglst[0].fullDescription())
#print(cglst[0].fullDescription())
#print(MakeCoNode(OP_JOIN, cglst[5], cglst[3]))


##_------------------------------- DATABASE STUFF

initEncoding()
#makeFirstGraphs()   # so faz o NULL
#genGraphs()
#for e in enc_lst:
#    LoadGraph(e)
#writeGraphData()
#print("AGORA")
#print(validateCotree('..0..11'))
writeGraphData()    # genGraphs com gravacao
