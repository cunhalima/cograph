#
#    cograph - Cograph Generation and Chromatic Analysis
#    Copyright (C) 2014 Alex Reimann Cunha Lima
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import sqlite3

# Constants
DB_FILE     = "cograph.db"
MAX_ORDER   = 8
VF_DELTA    = 1
INF_GIRTH   = 5
OP_VERT     = "."
OP_UNION    = "0"
OP_JOIN     = "1"
OPERATIONS = (OP_UNION, OP_JOIN, OP_VERT)

# Globals
g_nullGraph = None
g_cgset = {}
g_cglst = []
g_enc_set = {}
g_enc_lst = []
g_enc_nod = []

# Cotree encoding
# ------------------------------------------------------------------------------
class CotreeNode:
    def __init__(self, op, a, b):
        self.op = op
        self.a = a
        self.b = b
        self.string = self.op

    def __str__(self):
        return self.string

    def sort(self):
        if self.a != None and self.b != None:
            if self.a.op == self.op or self.a.op != self.op:
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
                lst = sorted(lst, key = lambda x: x.string)
                bstr = ""
                for i in range(1, len(lst)):
                    bstr += lst[i].string
                for i in range(len(lst) - 2):
                    bstr += self.op
                self.a = lst[0]
                self.b = g_enc_nod[g_enc_set[bstr]]
            elif self.b.op != self.op:
                if self.a.string > self.b.string:
                    self.a, self.b = self.b, self.a
            self.string = self.a.string + self.b.string + self.op
        if self.string in g_enc_set:
            return g_enc_nod[g_enc_set[self.string]]
        addEncoding(self.string, self)
        return self

def makeCotreeNode(op, a, b):
    if op == "" or op == OP_VERT:
        s = op
    else:
        s = a.string + b.string + op
        if s in g_enc_set:
            return g_enc_nod[g_enc_set[s]]
        s = b.string + a.string + op
    if s in g_enc_set:
        return g_enc_nod[g_enc_set[s]]
    node = CotreeNode(op, a, b)
    return node.sort()
                
def validateCotree(s):
    vnode = g_enc_nod[g_enc_set[OP_VERT]]
    stack = []
    for op in s:
        if op == OP_VERT:
            stack.append(vnode)
        else:
            if len(stack) < 2:
                return None
            b = stack.pop()
            a = stack.pop()
            stack.append(makeCotreeNode(op, a, b))
    if len(stack) != 1:
        return None
    n = stack.pop()
    if n == None:
        return None
    return n.string

def addEncoding(s, node):
    n = len(g_enc_lst)
    g_enc_set[s] = n
    g_enc_lst.append(s)
    g_enc_nod.append(node)
    return n

def genGraphs(cur = None):
    for i in range(MAX_ORDER + 1):
        makeOrder(i, cur)

def initEncoding():
    global orderBase
    global currentOrder
    orderBase = []
    currentOrder = -1

def makeOrder(order, cur):
    global currentOrder
    global orderBase
    if (order == currentOrder + 1):
        currentOrder += 1
        orderBase.append(len(g_enc_lst))
    elif order > currentOrder + 1:
        return
    orderMax = (order // 2) + 1
    if order == 0:
        n = makeCotreeNode("", None, None)
        writeCGData(n, None, None, cur)
        return
    elif order == 1:
        n = makeCotreeNode(OP_VERT, None, None)
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
                nodeA = g_enc_nod[j]
                nodeB = g_enc_nod[k]
                n = makeCotreeNode(OP_UNION, nodeA, nodeB)
                writeCGData(n, nodeA, nodeB, cur)
                n = makeCotreeNode(OP_JOIN, nodeA, nodeB)
                writeCGData(n, nodeA, nodeB, cur)

def encodeOperation(op, a, b):
    assert op in OPERATIONS
    an = g_enc_nod[g_enc_set[a]]
    bn = g_enc_nod[g_enc_set[b]]
    n = makeCotreeNode(op, an, bn)
    return n.string

def delCotreeVertex(enc, k):
    stack = []
    out = ""
    for i in range(len(enc)):
        c = enc[i]
        if c == OP_VERT:
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

def induceCotree(enc, indset):
    if enc == "":
        return ""
    stack = []
    out = ""
    p = 0
    for i in range(len(enc)):
        c = enc[i]
        if c == OP_VERT:
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

    if len(stack) != 1:
        return None
    return validateCotree(out)

# Cograph building
# ------------------------------------------------------------------------------
def loadGraph(encodedCotree, cl=0):
    if encodedCotree == "":
        return makeCoNode(None, None, None)
    stack = []
    forceClass = 0
    for i in range(len(encodedCotree)):
        c = encodedCotree[i]
        assert c in OPERATIONS
        if i == len(encodedCotree) - 1:
            forceClass = cl
        if c == OP_VERT:
            a = None
            b = None
        else:
            if len(stack) < 2:
                return None
            a = stack.pop()
            b = stack.pop()
        stack.append(makeCoNode(c, a, b, forceClass))
    if len(stack) != 1:
        return None
    return stack.pop()

def makeCoNode(op, a, b, cl=0):
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
    if cmd in g_cgset:
        o = g_cgset[cmd]
    else:
        o = CoNode(op, a, b, cmd, len(g_cglst), cl)
        g_cgset[cmd] = o
        o.build()
        g_cglst.append(o)
    return o
        
class CoNode:
    def __init__(self, op, a, b, cmd, index, cl=0):
        self.id = index
        # cotree data
        self.op = op
        self.a = a
        self.b = b
        self.cmd = cmd
        self.height = 0             # cotree height
        self.numchildren = 0        # number root's children
        # cograph data
        self.V = []
        self.VF = []                # vertices flags
        self.VDN = []               # number of delta neighbours
        self.numV = 0
        self.numE = 0
        # cograph properties
        self.cpClass = 1            # null graphs are class one
        self.maxDegree = 0
        self.maxEDegree = 0
        self.minDegree = 0
        self.connected = True       # null graphs are connected
        self.overfull = False       # null graphs are not overfull
        self.SO = False
        self.deltaSubgraphs = {}
        self.complete = True        # null graphs are complete
        self.cycle = False          # null graphs have no cycles
        self.clique = 0             # clique number
        self.combinations = 0       # num of diff combos for building this graph
        self.complement = self
        self.fullHeight = True
        self.girth = INF_GIRTH
        self.ovsub = None           # the overfull subgraph (if exists)
        self.chromNum = 0
        self.chromInd = 0
        self.strangers = False      # every pair of vertices are neighbours
        self.c4 = False
        self.star = False

    def addEdge(self, x1, x2):
        self.V[x1].append(x2)
        self.V[x2].append(x1)
        self.numE += 1

    def calcDeltaSubgraphs(self):
        if self.numV <= 1:
            return
        if self.overfull:
            return
        if self.op == OP_UNION:
            return
        for i in range(self.numV):
            enc = delCotreeVertex(self.cmd, i)
            assert(enc in g_cgset)
            g = g_cgset[enc]
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
                en = encodeOperation(OP_UNION, self.a.core.cmd, self.b.core.cmd)
                self.core = g_cgset[en]
        elif self.op == OP_JOIN:
            adegree = self.a.maxDegree + self.b.numV
            bdegree = self.b.maxDegree + self.a.numV
            if adegree > bdegree:
                self.core = self.a.core
            elif bdegree > adegree:
                self.core = self.b.core
            else:
                en = encodeOperation(OP_JOIN, self.a.core.cmd, self.b.core.cmd)
                self.core = g_cgset[en]

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
        enc = induceCotree(self.cmd, inset)
        return g_cgset[enc]

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

    def unionRaw(self):
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
        self.cycle = self.a.cycle or self.b.cycle
        self.girth = min(self.a.girth, self.b.girth)
        self.c4 = self.a.c4 or self.b.c4

    def union(self):
        self.unionRaw()
        self.connected = False
        self.maxDegree = max(self.a.maxDegree, self.b.maxDegree)
        self.minDegree = min(self.a.minDegree, self.b.minDegree)
        self.maxEDegree = max(self.a.maxEDegree, self.b.maxEDegree)
        self.chromNum = max(self.a.chromNum, self.b.chromNum)
        self.strangers = True
        self.star = self.a.star or self.b.star

    def join(self):
        self.unionRaw()
        for x1 in range(self.a.numV):
            for y in range(self.b.numV):
                x2 = y + self.a.numV
                self.addEdge(x1, x2)
        self.connected = True
        adeg = self.a.maxDegree + self.b.numV
        bdeg = self.b.maxDegree + self.a.numV
        self.maxDegree = max(adeg, bdeg)
        adeg = self.a.minDegree + self.b.numV
        bdeg = self.b.minDegree + self.a.numV
        self.minDegree = min(adeg, bdeg)
        # cycle, girth, c4 already pre-calculated by unionRaw
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
        if self.a.strangers and self.b.strangers:
            self.c4 = True
        if self.numV >= 3 and not self.cycle:
            self.star = True
        else:
            self.star = False

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
        self.a = g_nullGraph
        self.b = g_nullGraph
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

    def build(self):
        if self.op == None:             # null graph
            self.a = self
            self.b = self
        else:
            assert self.op in OPERATIONS
            if self.op == OP_VERT:
                self.singleton()
            else:
                if self.op == OP_UNION:
                    self.union()
                elif self.op == OP_JOIN:
                    self.join()
                self.calcChildren()
                self.calcHeight()
                self.calcOverfull()
                self.calcDeltaSubgraphs()
                self.calcSO()
                self.calcClass()
        self.calcComplete()
        self.calcCore()
        self.calcFlags()
        self.calcSemiCore()
        self.calcClique()

def updateGraphs(cur):
    tr = str.maketrans("01", "10")
    for g in g_cglst:
        ccmd = validateCotree(g.cmd.translate(tr))
        cid = -1
        if ccmd != None:
            cg = g_cgset[ccmd]
            g.complement = cg
            cid = g.complement.id
        cur.execute("UPDATE gr SET combinations=%d,complement=%d WHERE id=%d" %
            (g.combinations, cid, g.id))

def writeGraphData():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()    
        cur.execute("DROP TABLE IF EXISTS gr")
        cur.execute("DROP TABLE IF EXISTS op")
        cur.execute("CREATE TABLE gr("
                    "id INT PRIMARY KEY, "
                    "cotree TEXT, "
                    "n INT, "
                    "m INT, "
                    "star INT, "
                    "c4 INT, "
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
        cur.execute("CREATE TABLE op(op INT, g INT, a INT, b INT)")
        genGraphs(cur)
        updateGraphs(cur)

def b2i(b):
    if b: return 1
    return 0

def writeCGData(n, a, b, cur):
    if cur == None:
        return
    creating = False
    if n.string in g_cgset:
        n = g_cgset[n.string]
    else:
        n = loadGraph(n.string)
        creating = True
    if a != None and b != None:
        a = g_cgset[a.string]
        b = g_cgset[b.string]
        if b.numV > a.numV:
            a, b = b, a
    if n.op != None:
        op = OPERATIONS.index(n.op)
    else:
        op = len(OPERATIONS)
    if a != None and b != None:
        cur.execute("INSERT INTO op VALUES(%d, %d, %d, %d)" %
            (op, n.id, a.id, b.id))
    n.combinations += 1
    if not creating: return
    ovsub = 0
    if n.ovsub != None:
        ovsub = n.ovsub.id
    cur.execute("INSERT INTO gr VALUES(" \
        "%d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, "
        "%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)" %
        (n.id, n.cmd, n.numV, n.numE, n.star, n.c4, n.complete,
        n.clique, n.combinations, n.complement.id, n.connected, n.cycle,
        n.girth, n.maxDegree, n.minDegree, n.maxEDegree, n.overfull, n.SO,
        ovsub, n.cpClass, n.core.id, n.semiCore.id, n.height, n.fullHeight,
        n.numchildren, n.chromNum, n.chromInd))

initEncoding()
writeGraphData()
