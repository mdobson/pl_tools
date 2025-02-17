# Compiler settings
CC = gcc                    # Define the C compiler to use
CFLAGS = -Wall -Wextra -g  # Compiler flags:
                           # -Wall: Enable all common warnings
                           # -Wextra: Enable extra warnings
                           # -g: Include debug information

# Project files
SOURCES = main.c node.c parser.c printer.c interpreter.c  # List all source files
OBJECTS = $(SOURCES:.c=.o)                  # Generate object file names from sources
                                           # (e.g., main.c -> main.o)
TARGET = lisp_parser                        # Name of the final executable

# Mark these targets as "not real files" to ensure they always run
.PHONY: all clean run

# Default target: build everything
all: $(TARGET)

# Link object files to create the executable
$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET)

# Generic rule for building object files
# $< refers to the first prerequisite (the .c file)
# $@ refers to the target (the .o file)
%.o: %.c lisp_parser.h
	$(CC) $(CFLAGS) -c $< -o $@

# Remove all built files
clean:
	rm -f $(OBJECTS) $(TARGET)

# Run the program after building
run: $(TARGET)
	./$(TARGET) 