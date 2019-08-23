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
  jsr LoadPalettes
  jsr ConfigurePPU
  jsr WaitBlank
  jsr EnableSound
  jsr Initialize
  jsr Loop

; Makes safe update of screen
WaitBlank:
  lda $2002
  bpl WaitBlank ; keet checking until bit is 7 (VBlank)

; main loop
Loop:
  jsr CheckCurrentLetter
  jsr CheckWin
  jmp Loop

; the size of the word in address $0200
; $0201 will be the current letter choosed, to check in the word
; $0202 will store how many parts of the body will be displayed ( how many errors )
; $0203 will store if a letter was correctly guessed during that round
; initizalize the current word ( banana ) starting in address $0204 ( first letter ) 
; $0200 + the letter choosed will be the place to store if the current letter was guessed right, beginning in $0241
Initialize:
  lda #$06 ; word size
  sta $0200
  lda #$42 ; B
  sta $0204
  lda #$41 ; A
  sta $0205
  lda #$4E ; N
  sta $0206
  lda #$41 ; A
  sta $0207
  lda #$4E ; N
  sta $0208
  lda #$41 ; A
  sta $0209
  rts

EnableSound:
  lda #%00000111  ;enable Sq1, Sq2 and Tri channels
  sta $4015

ConfigurePPU:
  lda #%10000000   ; enable NMI, sprites from Pattern Table 0
  sta $2000

  lda #%00010000   ; enable sprites
  sta $2001
  rts

LoadPalettes:
  lda $2002    ; read PPU status to reset the high/low latch
  lda #$3F
  sta $2006    ; write the high byte of $3F00 address
  lda #$00
  sta $2006    ; write the low byte of $3F00 address
  ldx #$00 
LoadPallete:
  lda palette, x
  sta $2007
  inx
  cpx #$20
  bne LoadPallete
  rts

CheckCurrentLetter:
  ldx #$00
CheckCurrentLetterLoop:
  lda $0204, x
  cmp $0201
  bne CheckCurrenterLetterIncX
  ; set letter as correct
  tay
  lda #$01
  sta $0200, y
  sta $0203 ; set that a letter was guessed
CheckCurrenterLetterIncX:
  inx
  cpx $0200 ; iterate with the size of the word to guess
  bne CheckCurrentLetterLoop
  ; check if a letter was guessed
  lda $0203
  cmp #$01
  beq CheckCurrentLetterEnd ; if equals a letter was guessed and the value is equal to one, don't make a sound
  ;if an error happened
  inc $0202 ; inc how many erros ocurred
  ; jsr MakeSound
CheckCurrentLetterEnd:
  lda #$00
  sta $0203
  rts


MakeSound:
  ;Square 1
  lda #%00011000  ;Duty 00, Volume 8 (half volume)
  sta $4000
  lda #$C9        ;$0C9 is a C# in NTSC mode
  sta $4002       ;low 8 bits of period
  lda #%11111000
  sta $4003       ;high 3 bits of period
 
  ;Square 2
  ;lda #%01110110  ;Duty 01, Volume 6
  ;sta $4004
  ;lda #$A9        ;$0A9 is an E in NTSC mode
  ;sta $4006
  ;lda #$00
  ;sta $4007
 
  ;Triangle
  ;lda #%10000001  ;Triangle channel on
  ;sta $4008
  ;lda #$42        ;$042 is a G# in NTSC mode
  ;sta $400A
  ;lda #$00
  ;sta $400B

; stop sound
  ;lda #%00000000
  ;sta $4015
  rts

CheckWin:

Win:

GameOver:
  brk

NMI:
  ;NOTE: NMI code goes here
  jsr DrawScreen
  jsr DrawWord
  jmp EndNMI

DrawScreen:
  lda #$00  ; load $00 to A
  sta $2003 ; store first part in 2003
  lda #$00  ; load $00 to A (not really necessary, just for learning purposes)
  sta $2003 ; store second part in 2003

  jsr DrawHanger
  jsr DrawAlphabet
  jsr DrawSelector
  ; jsr DrawHead
  ; jsr DrawBody
  ; jsr DrawLeftArm
  ; jsr DrawRightArm
  ; jsr DrawLeftLeg
  ; jsr DrawRightLeg
  ; jsr DrawDeadHead

  rts

DrawLeftLeg:

  lda #72
  sta $2004
  lda #0024
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #80
  sta $2004
  lda #0026
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  rts

DrawRightLeg:

  lda #80
  sta $2004
  lda #0027
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  lda #72
  sta $2004
  lda #0025
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  rts

DrawLeftArm:

  lda #48
  sta $2004
  lda #0018
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #56
  sta $2004
  lda #0021
  sta $2004
  lda #00
  sta $2004
  lda #40
  sta $2004

  lda #56
  sta $2004
  lda #0020
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  rts

DrawRightArm:

  lda #48
  sta $2004
  lda #0019
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  lda #56
  sta $2004
  lda #0022
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  lda #56
  sta $2004
  lda #0023
  sta $2004
  lda #00
  sta $2004
  lda #64
  sta $2004

  rts

DrawBody:

  lda #48
  sta $2004
  lda #0016
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #48
  sta $2004
  lda #0017
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  lda #56
  sta $2004
  lda #0016
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #56
  sta $2004
  lda #0017
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  lda #64
  sta $2004
  lda #0016
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #64
  sta $2004
  lda #0017
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  rts

DrawSelector:

  lda #130
  sta $2004
  lda #0086
  sta $2004
  lda #00
  sta $2004
  lda #80
  sta $2004

  rts

DrawAlphabet:

; TODO: Loop through 4 rows to optimize code
; LoopRow1:
;   ldx #07

;   lda #120
;   sta $2004
;   lda #0032
;   sta $2004
;   lda #00
;   sta $2004
;   lda (#80, X)
;   sta $2004

;   dex
;   bne LoopRow1

  ; letter A (base)
  lda #128  ; decimal value of y
  sta $2004 ; Y value
  lda #0032 ; number of the tile of the sprite
  sta $2004 ; store tile number
  lda #00   ; store junk
  sta $2004 ; store number again (no special junk)
  lda #80   ; decimal value of x
  sta $2004 ; X value

  lda #128
  sta $2004
  lda #0034
  sta $2004
  lda #00
  sta $2004
  lda #96
  sta $2004

  lda #128
  sta $2004
  lda #0036
  sta $2004
  lda #00
  sta $2004
  lda #112
  sta $2004

  lda #128
  sta $2004
  lda #0038
  sta $2004
  lda #00
  sta $2004
  lda #128
  sta $2004

  lda #128
  sta $2004
  lda #0040
  sta $2004
  lda #00
  sta $2004
  lda #144
  sta $2004

  lda #128
  sta $2004
  lda #0042
  sta $2004
  lda #00
  sta $2004
  lda #160
  sta $2004

  lda #128
  sta $2004
  lda #0044
  sta $2004
  lda #00
  sta $2004
  lda #176
  sta $2004

  ; make loop 2nd row
  lda #144
  sta $2004
  lda #0046
  sta $2004
  lda #00
  sta $2004
  lda #80
  sta $2004

  lda #144
  sta $2004
  lda #0048
  sta $2004
  lda #00
  sta $2004
  lda #96
  sta $2004

  lda #144
  sta $2004
  lda #0050
  sta $2004
  lda #00
  sta $2004
  lda #112
  sta $2004

  lda #144
  sta $2004
  lda #0052
  sta $2004
  lda #00
  sta $2004
  lda #128
  sta $2004

  lda #144
  sta $2004
  lda #0054
  sta $2004
  lda #00
  sta $2004
  lda #144
  sta $2004

  lda #144
  sta $2004
  lda #0056
  sta $2004
  lda #00
  sta $2004
  lda #160
  sta $2004

  lda #144
  sta $2004
  lda #0058
  sta $2004
  lda #00
  sta $2004
  lda #176
  sta $2004

  ; make loop 3rd row
  lda #160
  sta $2004
  lda #0060
  sta $2004
  lda #00
  sta $2004
  lda #80
  sta $2004

  lda #160
  sta $2004
  lda #0062
  sta $2004
  lda #00
  sta $2004
  lda #96
  sta $2004

  lda #160
  sta $2004
  lda #0064
  sta $2004
  lda #00
  sta $2004
  lda #112
  sta $2004

  lda #160
  sta $2004
  lda #0066
  sta $2004
  lda #00
  sta $2004
  lda #128
  sta $2004

  lda #160
  sta $2004
  lda #0068
  sta $2004
  lda #00
  sta $2004
  lda #144
  sta $2004

  lda #160
  sta $2004
  lda #0070
  sta $2004
  lda #00
  sta $2004
  lda #160
  sta $2004

  lda #160
  sta $2004
  lda #0072
  sta $2004
  lda #00
  sta $2004
  lda #176
  sta $2004

  ; make loop 4th row
  lda #176
  sta $2004
  lda #0074
  sta $2004
  lda #00
  sta $2004
  lda #80
  sta $2004

  lda #176
  sta $2004
  lda #0076
  sta $2004
  lda #00
  sta $2004
  lda #96
  sta $2004

  lda #176
  sta $2004
  lda #0078
  sta $2004
  lda #00
  sta $2004
  lda #112
  sta $2004

  lda #176
  sta $2004
  lda #0080
  sta $2004
  lda #00
  sta $2004
  lda #128
  sta $2004

  lda #176
  sta $2004
  lda #0082
  sta $2004
  lda #00
  sta $2004
  lda #144
  sta $2004

  rts

DrawHead:
  lda #32   ; decimal value of y
  sta $2004 ; Y value
  lda #0008 ; number of the tile of the sprite
  sta $2004 ; store tile number
  lda #00   ; store junk
  sta $2004 ; store number again (no special junk)
  lda #48   ; decimal value of x
  sta $2004 ; X value

  lda #32
  sta $2004
  lda #0009
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  lda #40
  sta $2004
  lda #0010
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #40
  sta $2004
  lda #0011
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  rts

DrawDeadHead:
  lda #32
  sta $2004
  lda #0012
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #32
  sta $2004
  lda #0013
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  lda #40
  sta $2004
  lda #0014
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #40
  sta $2004
  lda #0015
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  rts

DrawHanger:

  ; Hanger corner (will be the base value)
  lda #24
  sta $2004
  lda #00
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #24
  sta $2004
  lda #0001
  sta $2004
  lda #00
  sta $2004
  lda #32
  sta $2004

  lda #24
  sta $2004
  lda #0001
  sta $2004
  lda #00
  sta $2004
  lda #40
  sta $2004

  lda #24
  sta $2004
  lda #0003
  sta $2004
  lda #00
  sta $2004
  lda #48
  sta $2004

  lda #24
  sta $2004
  lda #0006
  sta $2004
  lda #00
  sta $2004
  lda #56
  sta $2004

  ; Vertical bar (make loop?)
  lda #32
  sta $2004
  lda #0002
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #40
  sta $2004
  lda #0002
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #48
  sta $2004
  lda #0002
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #56
  sta $2004
  lda #0002
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #64
  sta $2004
  lda #0002
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #72
  sta $2004
  lda #0002
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #80
  sta $2004
  lda #0002
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #88
  sta $2004
  lda #0002
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  lda #96
  sta $2004
  lda #0004
  sta $2004
  lda #00
  sta $2004
  lda #24
  sta $2004

  rts

DrawWord:
  ldx #$00
DrawWordLoop:
  lda $0241, x
  cmp #$01
  bne DrawLetterNotFound
DrawLetterSuccess:
  ; draw a guessed letter
  lda #$00   ; these lines tell $2003
  sta $2003  ; to tell
  lda #$00   ; $2004 to start
  sta $2003  ; at $0000.

  ; calculate Y position
  lda #50  ; load Y value
  sta $2004 ; store Y value

  ; tile number will change with the letter ascii code
  lda #$0204, x ; pick tile for that letter ( maybe we will need to calculate that)
  sta $2004 ; store tile number

  ; pass this info always as 0
  lda #$00 ; no special junk
  sta $2004 ; store special junk

  ; calculate X position
  lda #20  ; load X value
  sta $2004 ; store X value
  jmp DrawWordLoopIncX
DrawLetterNotFound:


DrawWordLoopIncX:
  inx
  cpx #$19 ; 25 for 26 letter from alphabet
  bne DrawWordLoop
  rts

EndNMI:
  RTI        ; return from interrupt

IRQ:
   ;NOTE: IRQ code goes here
  rti

  .org $E000
palette:
  .db $0F,$31,$32,$33,$0F,$35,$36,$37,$0F,$39,$3A,$3B,$0F,$3D,$3E,$0F
  .db $0F,$29,$10,$20,$0F,$02,$38,$3C,$0F,$1C,$15,$14,$0F,$02,$38,$3C
  ;   Whi,LGr,MGr,DGr <-- Sprites color mapping
  ;   BG
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
  .base $0000
  .incbin "sprites.chr"
