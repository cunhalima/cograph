CPP=g++
OBJS=alex.o
EXE=alex

.PHONY: all clean run

all: $(EXE)

clean:
	@rm -f $(EXE) $(OBJS)

run: $(EXE)
	@./$(EXE)

$(EXE): $(OBJS)
	@$(CPP) $(CPPFLAGS) $^ -o $@

.cpp.o:
	@$(CPP) $(CPPFLAGS) -c $^ -o $@
