#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int getInstruction(int pc, unsigned char *buffer) {
    return buffer[pc];
}

int main(int argc, char *argv[]) {

    // No parameter for rom file
    if (argc != 2) {
        printf("Provide a .nes file\n");
        return 1;
    }

    // Variables
    unsigned char buffer[64*1024];
    int pc = 0;
    int instruction;
    FILE *fp;
    
    // Open file provided in parameter on read mode
    fp = fopen(argv[1], "r");

    // Read the file
    fread(buffer, sizeof(buffer), 1, fp);

    while (1) {
        instruction = getInstruction(pc, buffer);

        switch(instruction) {
            // LDA immediate
            case 0xA9:
                printf("instruction: %d\n", instruction);
                // some code
                break;
            default:
                printf("invalid instruction\n");
        }
        pc++;

        // printf("pc: %d, instruction: %d\n", pc, instruction);
    }

    return 0;
}