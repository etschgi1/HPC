# Compiler
MPICC = mpicc

# Flags for compiler
CFLAGS = -Wall -O2

# Source files (list all .c files here)
SRCS = helloworld.c

# Output executable
TARGET = my_mpi_program

# Object files (derived from source files)
OBJS = $(SRCS:.c=.o)

# Default target: compile and link the program
all: $(TARGET)

# Rule to compile and link
$(TARGET): $(OBJS)
	$(MPICC) $(CFLAGS) -o $(TARGET) $(OBJS)

# Rule to compile .c files into .o files
%.o: %.c
	$(MPICC) $(CFLAGS) -c $< -o $@

# Clean the build files
clean:
	rm -f $(OBJS) $(TARGET)

# Phony targets
.PHONY: all clean
