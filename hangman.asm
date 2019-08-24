;----------------------------------------------------------------
; CONSTANTS
;----------------------------------------------------------------

PRG_COUNT = 1 ;1 = 16KB, 2 = 32KB
MIRRORING = %0001 ;%0000 = horizontal, %0001 = vertical, %1000 = four-screen

;----------------------------------------------------------------
; VARIABLES
;----------------------------------------------------------------

  .enum $0000
  .ende

;----------------------------------------------------------------
; HEADER
;----------------------------------------------------------------

  .db "NES", $1a ;identification of the iNES header
  .db PRG_COUNT ;number of 16KB PRG-ROM pages
  .db $01 ;number of 8KB CHR-ROM pages
  .db $00|MIRRORING ;mapper 0 and mirroring
  .dsb 9, $00 ;clear the remaining bytes

;----------------------------------------------------------------
; PROGRAM BANK (BASE)
;----------------------------------------------------------------

  .base $10000-(PRG_COUNT*$4000)

;----------------------------------------------------------------
; RESET
;----------------------------------------------------------------

Reset:

  jsr LoadPalettes
  jsr LoadSprites
  jsr ConfigurePPU
  jsr WaitBlank
  jsr EnableSound
  ; jsr Initialize
  jsr Loop

;----------------------------------------------------------------
; ENABLE SOUND
;----------------------------------------------------------------

EnableSound:
  lda #%00000111  ;enable Sq1, Sq2 and Tri channels
  sta $4015

;----------------------------------------------------------------
; PPU CONFIGURATION
;----------------------------------------------------------------

ConfigurePPU:
  lda #%10000000   ; enable NMI, sprites from Pattern Table 0
  sta $2000

  lda #%00010000   ; enable sprites
  sta $2001
  rts

; Makes safe update of screen
WaitBlank:
  lda $2002
  bpl WaitBlank ; keet checking until bit is 7 (VBlank)

;----------------------------------------------------------------
; LOAD PALETTES
;----------------------------------------------------------------

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

;----------------------------------------------------------------
; LOAD SPRITES
;----------------------------------------------------------------

LoadSprites:
  ldx #$00              ; start at 0
LoadSprite:
  lda sprites, x        ; load data from address (sprites +  x)
  sta $0200, x          ; store into RAM address ($0200 + x)
  inx                   ; X = X + 1
  cpx #$01b0            ; Compare X to hex $08, decimal 8 (each 4 is a sprite)
  bne LoadSprite        ; Branch to LoadSprite if compare was Not Equal to zero

  lda #%10000000   ; enable NMI, sprites from Pattern Table 1
  sta $2000

  lda #%00010000   ; enable sprites
  sta $2001

;----------------------------------------------------------------
; TODO: HOW TO DISPLAY SPRITES (WEIRD FOREVER BELOW)
;----------------------------------------------------------------

Forever:
  jmp Forever     ;jump back to Forever, infinite loop

  ; rts ; TODO currently does nothing

;----------------------------------------------------------------
; GAME LOGIC
;----------------------------------------------------------------

; main loop
Loop:
  jsr CheckCurrentLetter
  jsr CheckWin
  jsr LatchController
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

CheckWin:

Win:

GameOver:
  brk

;----------------------------------------------------------------
; SOUND
;----------------------------------------------------------------

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

;----------------------------------------------------------------
; NMI (Non-Maskable Interrupt)
;----------------------------------------------------------------

NMI:
  jsr DrawScreen
  jsr DrawWord
  jmp EndNMI

;----------------------------------------------------------------
; MAIN SCREEN FUNCTION
;----------------------------------------------------------------

DrawScreen:
  lda #$00  ; load $00 to A
  sta $2003 ; store first part in 2003

  LDA #$02
  STA $4014       ; set the high byte (02) of the RAM address, start the transfer
  jsr SetUpControllers

  rts

;----------------------------------------------------------------
; CONTROLLERS
;----------------------------------------------------------------

SetUpControllers:

LatchController:
  LDA #$01
  STA $4016
  LDA #$00
  STA $4016

; Pressed A
ReadA: 
  LDA $4016           ; player 1 - A
  AND #%00000001      ; only look at bit 0
  BEQ ReadADone       ; branch to ReadADone if button is NOT pressed (0)
                      ; add instructions here to do something when button IS pressed (1)
ReadADone:            ; handling this button is done
  
; Pressed B
ReadB: 
  LDA $4016           ; player 1 - B
  AND #%00000001      ; only look at bit 0
  BEQ ReadBDone       ; branch to ReadBDone if button is NOT pressed (0)
                      ; add instructions here to do something when button IS pressed (1)
ReadBDone:            ; handling this button is done

; Pressed Select
ReadSelect: 
  LDA $4016           ; player 1 - Select
  AND #%00000001      ; only look at bit 0
  BEQ ReadSelectDone  ; branch to ReadBDone if button is NOT pressed (0)
                      ; add instructions here to do something when button IS pressed (1)
ReadSelectDone:       ; handling this button is done

; Pressed Start
ReadStart: 
  LDA $4016           ; player 1 - Select
  AND #%00000001      ; only look at bit 0
  BEQ ReadStartDone   ; branch to ReadBDone if button is NOT pressed (0)
                      ; add instructions here to do something when button IS pressed (1)
  LDA $0203           ; load sprite X position
  SEC                 ; make sure carry flag is set
  SBC #$01            ; A = A - 1
  STA $0203           ; save sprite X position
ReadStartDone:        ; handling this button is done

; Pressed Up
ReadUp: 
  LDA $4016           ; player 1 - Up
  AND #%00000001      ; only look at bit 0
  BEQ ReadUpDone      ; branch to ReadUpDone if button is NOT pressed (0)
MoveUp:
  LDA $0200           ; load sprite Y position
  SEC                 ; make sure carry flag is set
  SBC #$01            ; A = A - 1
  STA $0200           ; save sprite Y position
ReadUpDone:           ; handling this button is done

; Pressed Down
ReadDown: 
  LDA $4016           ; player 1 - Down
  AND #%00000001      ; only look at bit 0
  BEQ ReadDownDone    ; branch to ReadDownDone if button is NOT pressed (0)
MoveDown:
  LDA $0200           ; load sprite Y position
  CLC                 ; make sure carry flag is set
  ADC #$01            ; A = A + 1
  STA $0200           ; save sprite Y position
ReadDownDone:         ; handling this button is done

; Pressed Left
ReadLeft: 
  LDA $4016           ; player 1 - Left
  AND #%00000001      ; only look at bit 0
  BEQ ReadLeftDone    ; branch to ReadLeftDone if button is NOT pressed (0)
MoveLeft:
  LDA $0203           ; load sprite X position
  SEC                 ; make sure carry flag is set
  SBC #$01            ; A = A - 1
  STA $0203           ; save sprite X position
ReadLeftDone:         ; handling this button is done

; Pressed Right
ReadRight: 
  LDA $4016           ; player 1 - Right
  AND #%00000001      ; only look at bit 0
  BEQ ReadRightDone   ; branch to ReadRightDone if button is NOT pressed (0)
MoveRight:           
  LDA $0203           ; load sprite X position
  CLC                 ; make sure carry flag is set
  ADC #$01            ; A = A + 1
  STA $0203           ; save sprite X position
ReadRightDone:        ; handling this button is done
  rts

;----------------------------------------------------------------
; DRAWING FUNCTIONS
;----------------------------------------------------------------

; TODO: Base memory is $0204 - letter A, iterates each 4 then
; disableLetter:           
;   lda $0205           ; load sprite tile
;   clc                 ; make sure carry flag is set
;   adc #$01            ; A = A + 1 (which is the disable tile for the letter)
;   sta $0205           ; save sprite tile

disableA: 
  lda $0205           ; load sprite tile
  clc                 ; make sure carry flag is set
  adc #$01            ; A = A + 1 (which is the disable tile for the letter)
  sta $0205           ; save sprite tile

;----------------------------------------------------------------
; DRAW WORD
;----------------------------------------------------------------

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

;----------------------------------------------------------------
; END NMI
;----------------------------------------------------------------

EndNMI:
  rti        ; return from interrupt

;----------------------------------------------------------------
; IRG
;----------------------------------------------------------------

IRQ:
   ;NOTE: IRQ code goes here

;----------------------------------------------------------------
; COLOR PALETTE
;----------------------------------------------------------------

  .org $E000
palette:
  .db $0F,$31,$32,$33,$0F,$35,$36,$37,$0F,$39,$3A,$3B,$0F,$3D,$3E,$0F
  .db $0F,$29,$00,$20,$0F,$02,$38,$3C,$0F,$1C,$15,$14,$0F,$02,$38,$3C
  ;   Whi,LGr,MGr,DGr <-- Sprites color mapping
  ;   BG

;----------------------------------------------------------------
; SPRITES
;
; Using adresses ($0200 - $0307)
;----------------------------------------------------------------

sprites:
  ;vert tile attr horiz
  .db #130, #86, #00, #80 ; Y, tile, junk, X (Selector: $0200-$0203)

  ; Alphabet
  .db #128, #32, #00, #80   ; A ($0204-$0207)
  .db #128, #34, #00, #96   ; B ($0208-$0211)
  .db #128, #36, #00, #112  ; C ($0212-$0215)
  .db #128, #38, #00, #128  ; D ($0216-$0219)
  .db #128, #40, #00, #144  ; E ($0220-$0223)
  .db #128, #42, #00, #160  ; F ($0224-$0227)
  .db #128, #44, #00, #176  ; G ($0228-$0231)
  .db #144, #46, #00, #80   ; H ($0232-$0235)
  .db #144, #48, #00, #96   ; I ($0236-$0239)
  .db #144, #50, #00, #112  ; J ($0240-$0243)
  .db #144, #52, #00, #128  ; K ($0244-$0247)
  .db #144, #54, #00, #144  ; L ($0248-$0251)
  .db #144, #56, #00, #160  ; M ($0252-$0255)
  .db #144, #58, #00, #176  ; N ($0256-$0259)
  .db #160, #60, #00, #80   ; O ($0260-$0263)
  .db #160, #62, #00, #96   ; P ($0264-$0267)
  .db #160, #64, #00, #112  ; Q ($0268-$0271)
  .db #160, #66, #00, #128  ; R ($0272-$0275)
  .db #160, #68, #00, #144  ; S ($0276-$0279)
  .db #160, #70, #00, #160  ; T ($0280-$0283)
  .db #160, #72, #00, #176  ; U ($0284-$0287)
  .db #176, #74, #00, #80   ; V ($0288-$0291)
  .db #176, #76, #00, #96   ; W ($0292-$0295)
  .db #176, #78, #00, #112  ; X ($0296-$0299)
  .db #176, #80, #00, #128  ; Y ($0300-$0303)
  .db #176, #82, #00, #144  ; Z ($0304-$0307)

;----------------------------------------------------------------
; INTERRUPT VECTORS
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
