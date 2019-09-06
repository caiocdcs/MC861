#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

    // No parameter for rom file
    if (argc != 2) {
        printf("Provide a .nes file\n");
        return 1;
    }

    // Variables
    unsigned char buffer[64*1024];
    int i;
    FILE *fp;
    
    // Open file provided in parameter on read mode
    fp = fopen(argv[1], "r");

    // Read the file
    fread(buffer, sizeof(buffer), 1, fp);

    // Print file content
    for(i = 0; i < 64*1024; i++) {
        printf("%u ", buffer[i]);
    }

    printf("nes emulator\n");
    return 0;
}