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
PYTHON=/usr/bin/env python3
SQLITE=sqlite3
PROGRAM=cograph.py
TEST=test.py
DBASE=cograph.db

.PHONY: all clean run build test

all: build

clean:
	@rm -f $(DBASE)

build: $(DBASE)

run: $(DBASE)
	@$(SQLITE) $^

$(DBASE): $(PROGRAM)
	@$(PYTHON) $^

test: $(DBASE)
	@$(PYTHON) $(TEST)