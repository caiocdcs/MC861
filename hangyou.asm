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

;----------------------------------------------------------------
; program bank(s)
;----------------------------------------------------------------

   .base $10000-(PRG_COUNT*$4000)

Reset:

LoadSprites:
  LDX #$00              ; start at 0
LoadSpritesLoop:
   LDA sprites, x        ; load data from address (sprites + x)
   STA $0200, x          ; store into RAM address ($0200 + x)
   INX                   ; X = X + 1
   CPX #$10              ; Compare X to hex $10, decimal 16
   BNE LoadSpritesLoop   ; Branch to LoadSpritesLoop if compare was Not Equal to zero
                         ; if compare was equal to 16, continue down
   Forever:
      JMP Forever     ;infinite loop


NMI:

   ;NOTE: NMI code goes here

IRQ:

   ;NOTE: IRQ code goes here

;----------------------------------------------------------------
; interrupt vectors
;----------------------------------------------------------------

sprites:

   ;vert tile attr horiz
   .db $80, $32, $00, $80   ;sprite 0
   .db $80, $33, $00, $88   ;sprite 1
   .db $88, $34, $00, $80   ;sprite 2
   .db $88, $35, $00, $88   ;sprite 3

   .org $fffa

   .dw NMI
   .dw Reset
   .dw IRQ

;----------------------------------------------------------------
; CHR-ROM bank
;----------------------------------------------------------------

   .incbin "mario.chr"