#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

const char *byte2binary(int x) {
    static char b[9];
    int j;

    b[0] = '\0';

    for (j = 128; j > 0; j >>= 1) {
        strcat(b, ((x & j) == j) ? "1" : "0");
    }
    return b;
}

void print(uint8_t a, uint8_t x, uint8_t y, uint16_t sp, uint16_t pc, uint8_t p) {
    printf("| pc = 0x%x ", pc);
    printf("| a = 0x%x ", a);
    printf("| x = 0x%x ", x);
    printf("| y = 0x%x ", y);
    printf("| sp = 0x%x ", sp);
    printf("| p[NV-BDIZC] = ");
    printf("%s |\n", byte2binary(p));
}

void printls(uint8_t a, uint8_t x, uint8_t y, uint16_t sp, uint16_t pc, uint8_t p, uint16_t addr, uint8_t data) {
    printf("| pc = 0x%x ", pc);
    printf("| a = 0x%x ", a);
    printf("| x = 0x%x ", x);
    printf("| y = 0x%x ", y);
    printf("| sp = 0x%x ", sp);
    printf("| p[NV-BDIZC] = ");
    printf("%s ", byte2binary(p));
    printf("| MEM[0x%x] = 0x%x |\n", addr, data);
}
  
int getInstruction(uint16_t pc, unsigned char *buffer) {
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
    FILE *fp;

    uint8_t instruction;

    uint16_t pc = 0, sp = 0, p = 0;
    uint8_t a = 0, x = 0, y = 0;
    uint16_t addr = 0;
    uint8_t data = 0;
    
    // Open file provided in parameter on read mode
    fp = fopen(argv[1], "r");

    // Read the file
    fread(buffer, sizeof(buffer), 1, fp);

    while (1) {
        instruction = getInstruction(pc, buffer);

        switch(instruction) {
            // LDA immediate
            case 0xA9:
                // some code
                printf("instruction: %d\n", instruction);
                break;
            default:
                // printf("invalid instruction\n");
                break;
        }
        pc++;

        print(a, x, y, sp, pc, p);
        printls(a, x, y, sp, pc, p, addr, data);
    }

    return 0;
}