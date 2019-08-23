;----------------------------------------------------------------
; constants
;----------------------------------------------------------------

PRG_COUNT = 1 ;1 = 16KB, 2 = 32KB
MIRRORING = %0001 ;%0000 = horizontal, %0001 = vertical, %1000 = four-screen

;----------------------------------------------------------------
; variables
;----------------------------------------------------------------

   .enum $0000

   ;NOTE: declare variables using the DSB and DSW directives, like this:

   ;MyVariable0 .dsb 1
   ;MyVariable1 .dsb 3

   .ende

   ;NOTE: you can also split the variable declarations into individual pages, like this:

   ;.enum $0100
   ;.ende

   ;.enum $0200
   ;.ende

;----------------------------------------------------------------
; iNES header
;----------------------------------------------------------------

   .db "NES", $1a ;identification of the iNES header
   .db PRG_COUNT ;number of 16KB PRG-ROM pages
   .db $01 ;number of 8KB CHR-ROM pages
   .db $00|MIRRORING ;mapper 0 and mirroring
   .dsb 9, $00 ;clear the remaining bytes
   .inesprg 1   ; 1x 16KB PRG code
   .ineschr 1   ; 1x  8KB CHR data
   .inesmap 0   ; mapper 0 = NROM, no bank swapping
   .inesmir 2   ; background mirroring - 2 is single screen

;----------------------------------------------------------------
; program bank(s)
;----------------------------------------------------------------

   .base $10000-(PRG_COUNT*$4000)
   ; additional code of tutorial, is it necessary?

Reset:
   
   SEI          ; disable IRQs
	CLD          ; disable decimal mode
	LDX #$40	
	STX $4017    ; disable APU frame IRQ
	LDX #$FF	
	TXS          ; Set up stack
	INX          ; now X = 0
	STX $2000    ; disable NMI
	STX $2001    ; disable rendering
	STX $4010    ; disable DMC IRQs

   vblankwait1:       ; First wait for vblank to make sure PPU is ready
      BIT $2002
      BPL vblankwait1

   clrmem:
      LDA #$00
      STA $0000, x
      STA $0100, x
      STA $0200, x
      STA $0400, x
      STA $0500, x
      STA $0600, x
      STA $0700, x
      LDA #$FE
      STA $0300, x
      INX
      BNE clrmem
      
   vblankwait2:      ; Second wait for vblank, PPU is ready after this
      BIT $2002
      BPL vblankwait2

   LoadPalettes:
      LDA $2002             ; read PPU status to reset the high/low latch
      LDA #$3F
      STA $2006             ; write the high byte of $3F00 address
      LDA #$00
      STA $2006             ; write the low byte of $3F00 address
      LDX #$00              ; start out at 0
      
   LoadPalettesLoop:
      LDA background_palette, x        ; load data from address (palette + the value in x)
                              ; 1st time through loop it will load palette+0
                              ; 2nd time through loop it will load palette+1
                              ; 3rd time through loop it will load palette+2
                              ; etc
      STA $2007             ; write to PPU
      INX                   ; X = X + 1
      CPX #$10              ; Compare X to hex $10, decimal 16 - copying 16 bytes = 4 sprites
      BNE LoadPalettesLoop  ; Branch to LoadPalettesLoop if compare was Not Equal to zero

   Foreverloop:
	   JMP Foreverloop     ;jump back to Forever, infinite loop

NMI:

   RTI

   background_palette:
      .db $22,$29,$1A,$0F	;background palette 1
      .db $22,$36,$17,$0F	;background palette 2
      .db $22,$30,$21,$0F	;background palette 3
      .db $22,$27,$17,$0F	;background palette 4
   
   sprite_palette:
      .db $22,$16,$27,$18	;sprite palette 1
      .db $22,$1A,$30,$27	;sprite palette 2
      .db $22,$16,$30,$27	;sprite palette 3
      .db $22,$0F,$36,$17  ;sprite palette 4

IRQ:

   ;NOTE: IRQ code goes here

;----------------------------------------------------------------
; interrupt vectors
;----------------------------------------------------------------

   .org $fffa

   .dw NMI
   .dw Reset
   .dw IRQ

;----------------------------------------------------------------
; CHR-ROM bank
;----------------------------------------------------------------

   .incbin "sprites.chr"
