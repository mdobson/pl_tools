#include <stdio.h>
#include <stdlib.h>

void print_int_collection(int** collection, int size) {
    for (int i = 0; i < size; i++) {
        // Check if the pointer is valid before dereferencing
        if (collection[i] != NULL) {
            printf("Value at position %d: %d\n", i, *collection[i]);
        }
    }
}

int main() {
    // Example creating and using a collection of int pointers
    const int size = 5;
    int** numbers = malloc(size * sizeof(int*));
    
    // Allocate and assign values
    for (int i = 0; i < size; i++) {
        numbers[i] = malloc(sizeof(int));
        *numbers[i] = i * 10;  // Sample values: 0, 10, 20, 30, 40
    }

    // Print the collection
    print_int_collection(numbers, size);

    // Clean up memory
    for (int i = 0; i < size; i++) {
        free(numbers[i]);
    }
    free(numbers);

    return 0;
}
