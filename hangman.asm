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
  jsr EnableSound
  jsr Initialize
  jsr Loop

; main loop
Loop:
  jsr CheckCurrentLetter
  jsr CheckWin
  jmp Loop

; initizalize the current word ( banana ) starting in address $0203 ( first letter ) and the size of the word in address $0200
; $0201 will be the current letter choosed, to check in the word
; $0202 will store how many parts of the body will be displayed ( how many errors )
; $0200 + the letter choosed will be the place to store if the current letter was guessed right, beginning in $0241
Initialize:
  lda #$05 ; word size - 1
  sta $0200
  lda #$42 ; B
  sta $0203
  lda #$41 ; A
  sta $0204
  lda #$42 ; N
  sta $0205
  lda #$41 ; A
  sta $0206
  lda #$42 ; N
  sta $0207
  lda #$41 ; A
  sta $0208
  ; test
  lda #$01
  ldx $0204
  sta $0200, x
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
  lda $0203, x
  cmp $0201
  beq CheckCurrenterLetterIncSuccess
CheckCurrenterLetterIncSuccess:
  ; set letter as correct
  tay
  lda #$01
  sta $0200, y
  jmp CheckCurrenterLetterIncX
CheckCurrenterLetterIncError:
  jsr MakeSound
  inc $0202
CheckCurrenterLetterIncX:
  inx
  cpx $0200
  bne CheckCurrentLetterLoop
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
  lda #$0203, x ; pick tile for that letter ( maybe we will need to calculate that)
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
  .db $0F,$1C,$15,$14,$0F,$02,$38,$3C,$0F,$1C,$15,$14,$0F,$02,$38,$3C
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
  .incbin "mario.chr"