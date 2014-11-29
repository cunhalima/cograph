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

def Test_1():
    # We name a connected cograph without cycles with at least 2 vertices a star
    print("Cographs with a star in the core:")
    cur = con.cursor()    
    cur.execute( "SELECT r.id,r.cotree,core.cotree "
                 "FROM gr AS r "
                 "INNER JOIN gr AS core ON r.core = core.id "
                 "WHERE core.star = 1 "
                 "ORDER BY r.id")
    rows = cur.fetchall()
    for row in rows: print(row)

Test_1()
