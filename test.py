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

con = sqlite3.connect("cograph.db")
baseQuery = "SELECT COUNT(*) " \
            "FROM op INNER JOIN gr AS r ON op.g = r.id " \
            "INNER JOIN gr AS a ON op.a  = a.id " \
            "INNER JOIN gr AS b ON op.b  = b.id " \
            "INNER JOIN gr AS core ON r.core = core.id " \
            "INNER JOIN gr AS acore ON a.core = acore.id " \
            "INNER JOIN gr AS bcore ON b.core = bcore.id " \
            "WHERE op.op = 1 " \

def BasicTest(name, prop):
    print("==============================")
    print(" ", name, "test:")
    print("==============================")
    cur = con.cursor()
    query = baseQuery + prop
    cur.execute(query)
    total = cur.fetchall()[0][0]
    if total == 0:
        print("Unable to test", name, "due to lack of valid instances\n")
        return
    cur.execute(query + "AND r.class = 1")
    class1 = cur.fetchall()[0][0]
    cur.execute(query + "AND r.class = 2")
    class2 = cur.fetchall()[0][0]
    print("Class 1: %7d cases out of %d" % (class1, total))
    print("Class 2: %7d cases out of %d" % (class2, total))
    if total == class1:
        print(name, "passed the test\n")
    else:
        print(name, "DID NOT pass the test\n")

# Test Conjecture A
def Test_1():
    BasicTest("Conjecture A", "AND a.maxdeg = b.maxdeg AND acore.cycle = 0 ")

# Test Theorem 5.2
def Test_2():
    BasicTest("Theorem 5.2", "AND a.maxdeg = b.maxdeg AND acore.m = 0 ")

# Test Theorem 4.7
def Test_3():
    BasicTest("Theorem 4.7[Simone & Mello]", "AND a.maxdeg = b.maxdeg " \
              "AND a.class = 1 AND b.class = 1 ")

# Test Theorem 4.12
def Test_4():
    BasicTest("Theorem 4.12[Machado & Figueiredo]",
              "AND b.maxdeg < (b.n - a.n) ")

def smallQuery(title, query):
    cur = con.cursor()
    cur.execute(query)
    res = cur.fetchall()
    print(title, res[0][0])

# Show basic SO cographs
def Test_5():
    print("==============================")
    print(" Smallest SO cographs:")
    print("==============================")
    queryHead = "SELECT cotree " \
                "FROM gr WHERE "
    queries = [ "ov=1 AND no=1 ",
                "ov=1 AND no=0 ",
                "ov=0 AND no=1 ",
                "so=1 AND ov=0 AND no=0 " ]
    titles = [ "SO, O, NO",
               "SO, O",
               "SO, NO",
               "SO" ]
    for i in range(len(queries)):
        smallQuery("A cograph %-9s: cotree =" % titles[i],
                   queryHead + queries[i] + "LIMIT 1")

Test_1()
Test_2()
Test_3()
Test_4()
Test_5()
