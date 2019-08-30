;----------------------------------------------------------------
; CONSTANTS
;----------------------------------------------------------------

PRG_COUNT = 1     ;1 = 16KB, 2 = 32KB
MIRRORING = %0001 ;%0000 = horizontal, %0001 = vertical, %1000 = four-screen

L_byte         = $0000
H_byte         = $0001

; PPU

PPU_CTRL    =   $2000
PPU_MASK    =   $2001
PPU_STATUS  =   $2002
OAM_ADDR    =   $2003
OAM_DATA    =   $2004
PPU_SCROLL  =   $2005
PPU_ADDR    =   $2006
PPU_DATA    =   $2007

;----------------------------------------------------------------
; VARIABLES
;----------------------------------------------------------------

  .enum $0000
  .ende

;----------------------------------------------------------------
; HEADER
;----------------------------------------------------------------

  .db "NES", $1a    ;identification of the iNES header
  .db PRG_COUNT     ;number of 16KB PRG-ROM pages
  .db $01           ;number of 8KB CHR-ROM pages
  .db $00|MIRRORING ;mapper 0 and mirroring
  .dsb 9, $00       ;clear the remaining bytes

;----------------------------------------------------------------
; PROGRAM BANK (BASE)
;----------------------------------------------------------------

  .base $10000-(PRG_COUNT*$4000)

;----------------------------------------------------------------
; RESET
;----------------------------------------------------------------

.org $C000

RESET:
  sei
  cld
; Disable APU frame IRQ
  ldx #$40
  stx $4017
  ldx #$FF
  txs
  ldx #$00
; Disable NMI and rendering
  stx PPU_CTRL
  stx PPU_MASK
  stx $4010

;----------------------------------------------------------------
; ENABLE SOUNDS
;----------------------------------------------------------------

ClearAPU:
  lda #$00
  ldy #$00
ClearAPULoop:
  sta $4000, y
  iny
  cpy $18
  bne ClearAPULoop

;----------------------------------------------------------------
; WAIT PPU AND CLEAR MEMORY
;----------------------------------------------------------------

; Wait for PPU
vBlankWait1:
  bit PPU_STATUS
  bpl vBlankWait1
  
; Clear Memory
ClearLoop:
  lda #$00
  sta $0000, X
  sta $0100, X
  sta $0200, X
  sta $0300, X
  sta $0400, X
  sta $0500, X
  sta $0600, X
  sta $0700, X
  lda #$FE
  sta $0200, x
  inx
  bne ClearLoop

; Wait for PPU
vBlankWait2:
  bit PPU_STATUS
  bpl vBlankWait2

;----------------------------------------------------------------
; LOAD PALETTES
;----------------------------------------------------------------

LoadPalettes:
  lda PPU_STATUS    ; read PPU status to reset the high/low latch
  lda #$3F
  sta PPU_ADDR      ; write the high byte of $3F00 address
  lda #$00
  sta PPU_ADDR      ; write the low byte of $3F00 address
  ldx #$00
LoadPalette:
  lda palette, x
  sta PPU_DATA
  inx
  cpx #$20
  bne LoadPalette

;----------------------------------------------------------------
; LOAD SPRITES
;----------------------------------------------------------------

LoadSprites:
  ldx #$00              ; start at 0
LoadSprite:
  lda sprites, x        ; load data from address (sprites +  x)
  sta $0200, x          ; store into RAM address ($0200 + x)
  inx                   ; X = X + 1
  cpx #$c0              ; Compare X to hex $c0 (each 4 is a sprite) -- change here if more sprites are needed
  bne LoadSprite        ; Branch to LoadSprite if compare was Not Equal to zero

;----------------------------------------------------------------
; LOAD BACKGROUND 
;----------------------------------------------------------------

LoadBackground:
  lda PPU_STATUS
  lda #$20
  sta PPU_ADDR          ; set high byte
  lda #$00
  sta PPU_ADDR          ; set low byte
  ldx #$00
LoadBackgroundTile1:
  lda bg1, x
  sta PPU_DATA
  inx
  cpx #$00
  bne LoadBackgroundTile1
LoadBackgroundTile2:
  lda bg2, x
  sta PPU_DATA
  inx
  cpx #$00
  bne LoadBackgroundTile2
LoadBackgroundTile3:
  lda bg3, x
  sta PPU_DATA
  inx
  cpx #$00
  bne LoadBackgroundTile3
LoadBackgroundTile4:
  lda bg4, x
  sta PPU_DATA
  inx
  cpx #$c0
  bne LoadBackgroundTile4

;----------------------------------------------------------------
; LOAD ATTRIBUTES
;----------------------------------------------------------------

LoadAttributes:
  lda $2002
  lda #$23
  sta $2006
  lda #$c0
  sta $2006
  lda #$00
  ldy #$00
LoadAttribute:
  sta $2007
  iny
  cpy #$40
  bne LoadAttribute

;----------------------------------------------------------------
; PPU CONFIGURATION
;----------------------------------------------------------------

ConfigurePPU:
  lda #%10010000   ; enable NMI, sprites from Pattern Table 0
  sta PPU_CTRL
  lda #%00011110   ; enable sprites and background
  sta PPU_MASK
  lda #$00         ; disable scroll
  sta PPU_SCROLL
  sta PPU_SCROLL

;----------------------------------------------------------------
; INITIALIZE
;----------------------------------------------------------------

; the size of the word in address $0500
; $0501 will be the current letter choosed, to check in the word
; $0502 will store how many parts of the body will be displayed ( how many errors )
; $0503 will store if a letter was correctly guessed during that round
; $0504 how many letters guessed
; initizalize the current word ( banana ) starting in address $0508 ( first letter ) 
; $0500 + the letter code choosed will be the place to store if the current letter was guessed right, beginning in $0520
Initialize:

; code to generate a ramdom number and pick a word
RandomNumber:
	ldx #2     ; iteration count (generates 2 bits)
	lda seed+0

	asl        ; shift the register
	rol seed+1
	bcc :+
	eor #$2D   ; apply XOR feedback whenever a 1 bit is shifted out

	dex
	bne :--
	sta seed+0
	cmp #0     ; reload flags

GetWord:
  lda words
  sta $0500
  ldx seed
  ldy #00
GetWordLoop:
  lda words, x
  sta $0508, y
  inx
  iny
  cpy $0500
  bne GetWordLoop ; load last letter

  lda #$00
  sta $0505 ; position for count the tile position that will be drawn, each sprite has 4 bytes

  ; Controller counter c initialization (as 0)
  lda #$00
  sta $0302

;----------------------------------------------------------------
; INFINITE LOOP
;----------------------------------------------------------------

Forever:
  jmp Forever

;----------------------------------------------------------------
; SOUNDS
;----------------------------------------------------------------

.include "sounds.asm"

;----------------------------------------------------------------
; NMI (Non-Maskable Interrupt)
;----------------------------------------------------------------

NMI:
SetUpOAMAddr:
  lda #$00        ; load $00 to A
  sta OAM_ADDR    ; store first part in 2003
  sta OAM_ADDR    ; store second part in 2003
SetUpControllers:
  lda #$02
  sta $4014   ; set the high byte (02) of the RAM address, start the transfer

  jsr DrawErrors
  jsr DrawWord
  jmp EndNMI

;----------------------------------------------------------------
; DRAW ERRORS & WORD
;----------------------------------------------------------------

DrawWord:
  ldy #00
DrawWordLoop: 
  ldx $0508, y
  lda $0500, x
  cmp #$01
  bne DrawWordNotGuessed

  txa
  ldx $0505
  sta $02A5, x
  jmp DrawWordEndLoop

DrawWordNotGuessed:
  lda #$1D
  ldx $0505
  sta $02A5, x

DrawWordEndLoop:
  txa
  clc
  adc #$04
  sta $0505

  iny
  cpy $0500
  bne DrawWordLoop

  lda #00
  sta $0505
  rts

DrawErrors:
  lda $0502
  cmp #$01
  beq DrawErrorHead
  cmp #$02
  beq DrawErrorBody
  cmp #$03
  beq DrawErrorLeftArm
  cmp #$04
  beq DrawErrorRightArm
  cmp #$05
  beq DrawErrorLeftLeg
  cmp #$06
  beq DrawErrorRightLeg
  jmp DrawErrorEnd
DrawErrorRightLeg:
  jsr DrawRightLeg
DrawErrorLeftLeg:
  jsr DrawLeftLeg
DrawErrorRightArm:
  jsr DrawRightArm
DrawErrorLeftArm:
  jsr DrawLeftArm
DrawErrorBody:
  jsr DrawBody
DrawErrorHead:
  jsr DrawHead
DrawErrorEnd:
  rts

;----------------------------------------------------------------
; DRAWING FUNCTIONS
;----------------------------------------------------------------

.include "drawing.asm"

;----------------------------------------------------------------
; END NMI
;----------------------------------------------------------------

EndNMI:

;----------------------------------------------------------------
; CONTROLLERS
;----------------------------------------------------------------

; $0300 saves the selector's offset horizontal position
; $0301 saves the selector's offset vertical position 
; $0302 alphabet counter

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
SelectLetter:
  LDA $0302           ; counter c = c * 2
  STA $0303
  ASL $0303           
  LDA $0303
  ADC #$20            ; x = c + 32
  STA $0501           ; selecionar letra
ReadADone:            ; handling this button is done
  
; Pressed B
ReadB: 
  LDA $4016           ; player 1 - B
  AND #%00000001      ; only look at bit 0
  BEQ ReadBDone       ; branch to ReadBDone if button is NOT pressed (0)
                      ; add instructions here to do something when button IS pressed (1)
; TODO: Link B to command 'jsr RESET', if in state Win or GameOver (maybe use memory address to know)
  jmp RESET
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
; TODO REMOVEEE!
  LDA $0302           ; counter c = c * 2
  STA $0303
  ASL $0303           
  LDA $0303
  ADC #$20            ; x = c + 32
  STA $0501           ; selecionar letra
ReadStartDone:        ; handling this button is done

; Pressed Up
ReadUp: 
  LDA $4016           ; player 1 - Up
  AND #%00000001      ; only look at bit 0
  BEQ ReadUpDone      ; branch to ReadUpDone if button is NOT pressed (0)
CanMoveUp:
  LDA $0301           ; load selector y position
  SEC
  SBC #1              ; move up y = y - 1
  BMI ReadUpDone      ; if negative, dont move selector
  STA $0301           ; else, move onde postion up
IterateAlphabetUp:
  LDA $0302           ; load alphabet counter c
  SEC
  SBC #7              ; c = c - 7
  BMI ReadUpDone      ; if negative, dont move selector
  STA $0302           ; else, move onde postion up
MoveUp:
  LDA $0200           ; load sprite Y position
  SEC                 ; make sure carry flag is set
  SBC #$10            ; A = A - 16
  STA $0200           ; save sprite Y position
  jsr MoveSound
ReadUpDone:           ; handling this button is done

; Pressed Down
ReadDown: 
  LDA $4016           ; player 1 - Down
  AND #%00000001      ; only look at bit 0
  BEQ ReadDownDone    ; branch to ReadDownDone if button is NOT pressed (0)
CanMoveDown:
  LDA $0301           ; load selector y position
  CLC
  ADC #1              ; move down y = y - 1
  CMP #$4             ; if y > 4
  BPL ReadDownDone    ; dont move the selector
; Cannot move outside of boundaries
  tax
  lda $0300
  cmp #$5             ; if x < 5
  bmi ContinueMoveDown
  lda $0301
  cmp #$2             ; if y < 2
  bmi ContinueMoveDown
  jmp ReadDownDone
ContinueMoveDown:
  stx $0301
IterateAlphabetDown:
  LDA $0302           ; load alphabet counter c
  CLC
  ADC #7              ; c = c + 7
  CMP #$26            ; if c > 26
  BPL ReadDownDone    ; dont move the selector
  STA $0302           ; else, move onde postion down
MoveDown:
  LDA $0200           ; load sprite Y position
  CLC                 ; make sure carry flag is set
  ADC #$10            ; A = A + 16
  STA $0200           ; save sprite Y position
  jsr MoveSound
ReadDownDone:         ; handling this button is done

; Pressed Left
ReadLeft: 
  LDA $4016           ; player 1 - Left
  AND #%00000001      ; only look at bit 0
  BEQ ReadLeftDone    ; branch to ReadLeftDone if button is NOT pressed (0)
CanMoveLeft:
  LDA $0300           ; load selector x position
  SEC
  SBC #1              ; move left x = x - 1
  BMI ReadLeftDone    ; if negative, dont move selector      
  STA $0300           ; else, move onde postion left
IterateAlphabetLeft:
  LDA $0302           ; load alphabet counter c
  SEC
  SBC #1              ; c = c - 1
  BMI ReadLeftDone    ; if negative, dont move selector
  STA $0302           ; else, move onde postion left
MoveLeft:
  LDA $0203           ; load sprite X position
  SEC                 ; make sure carry flag is set
  SBC #$10            ; A = A - 16
  STA $0203           ; save sprite X position
  jsr MoveSound
ReadLeftDone:         ; handling this button is done

; Pressed Right
ReadRight: 
  LDA $4016           ; player 1 - Right
  AND #%00000001      ; only look at bit 0
  BEQ ReadRightDone   ; branch to ReadRightDone if button is NOT pressed (0)
CanMoveRight:
  LDA $0300           ; load selector x position
  CLC
  ADC #1              ; move right x = x + 1
  CMP #$7             ; if x > 7
  BPL ReadRightDone   ; dont move the selector
; Cannot move outside of boundaries
  tax
  lda $0301
  cmp #$3             ; if y < 3
  bmi ContinueMoveRight
  lda $0300
  cmp #$4             ; if x < 4
  bmi ContinueMoveRight
  jmp ReadRightDone
ContinueMoveRight:
  stx $0300
IterateAlphabetRight:
  LDA $0302           ; load alphabet counter c
  CLC
  ADC #1              ; c = c + 1
  CMP #$26            ; if c > 26
  BPL ReadRightDone   ; dont move the selector
  STA $0302           ; else, move onde postion right
MoveRight:           
  LDA $0203           ; load sprite X position
  CLC                 ; make sure carry flag is set
  ADC #$10            ; A = A + 16
  STA $0203           ; save sprite X position
  jsr MoveSound
ReadRightDone:        ; handling this button is done

ControllersDone:

;----------------------------------------------------------------
; GAME LOGIC
;----------------------------------------------------------------

CheckCurrentLetter:
  ldx #$00
  lda $0501
  cmp #$00
  beq CheckCurrentLetterEnd
CheckCurrentLetterLoop:
  lda $0508, x
  cmp $0501
  bne CheckCurrenterLetterIncX
  ; check if is the first time the letter is guessed
SetCorrectLetter:
  tay
  lda #$01
  sta $0503                 ; set that a letter was guessed
  lda $0500, y
  cmp #$01
  beq CheckCurrenterLetterIncX
  inc $0504
CheckCurrenterLetterIncX:
  inx
  cpx $0500                 ; iterate with the size of the word to guess
  bne CheckCurrentLetterLoop
  ; check if a letter was guessed
  lda $0503
  cmp #$01
  beq CheckCurrentLetterGuessed ; if equals a letter was guessed and the value is equal to one, don't make a sound
  ldy $0501
  lda $0500, y
  cmp #$02
  beq CheckCurrentLetterEnd
  lda #$02
  sta $0500, y
  inc $0502                 ; inc error count to game over
  jmp CheckCurrentLetterEnd
  ;jsr MakeSound
CheckCurrentLetterGuessed:
  lda #$01
  sta $0500, y
CheckCurrentLetterEnd:
  lda #$00
  sta $0503
  sta $0501

CheckWin:
  lda $0504
  cmp $0500
  beq Win
  lda $0502
  cmp #06
  beq GameOver
  
  jmp Forever

Win:
  jsr DrawWin
; TODO: Link B to command 'jsr RESET', if in state Win or GameOver (maybe use memory address to know)
  brk

GameOver:
  jsr DrawGameOver
; TODO: Link B to command 'jsr RESET', if in state Win or GameOver (maybe use memory address to know)
  brk


;----------------------------------------------------------------
; IRQ
;----------------------------------------------------------------

IRQ:
  rti

;----------------------------------------------------------------
; COLOR PALETTE
;----------------------------------------------------------------

  .org $E000
palette:
  .db $0F,$32,$08,$18,$0F,$35,$36,$37,$0F,$39,$3A,$3B,$0F,$3D,$3E,$0F
  .db $0F,$29,$00,$20,$0F,$15,$26,$37,$0F,$1C,$15,$2B,$0F,$26,$27,$28
  ;   Whi,LGr,MGr,DGr <-- Sprites color mapping

;----------------------------------------------------------------
; SPRITES
;
; Using adresses ($0200 - $02a3)
;----------------------------------------------------------------

sprites:
  ; Selector
  .db #130, #86, #00, #80 ; Y, tile, junk, X (Selector: $0200-$0203)

  ; Alphabet
  .db #128, #32, #00, #80   ; A ($0204-$0207)
  .db #128, #34, #00, #96   ; B ($0208-$020b)
  .db #128, #36, #00, #112  ; C ($020c-$020f)
  .db #128, #38, #00, #128  ; D ($0210-$0213)
  .db #128, #40, #00, #144  ; E ($0214-$0217)
  .db #128, #42, #00, #160  ; F ($0218-$021b)
  .db #128, #44, #00, #176  ; G ($021c-$021f)
  .db #144, #46, #00, #80   ; H ($0220-$0223)
  .db #144, #48, #00, #96   ; I ($0224-$0227)
  .db #144, #50, #00, #112  ; J ($0228-$022b)
  .db #144, #52, #00, #128  ; K ($022c-$022f)
  .db #144, #54, #00, #144  ; L ($0230-$0233)
  .db #144, #56, #00, #160  ; M ($0234-$0237)
  .db #144, #58, #00, #176  ; N ($0238-$023b)
  .db #160, #60, #00, #80   ; O ($023c-$023f)
  .db #160, #62, #00, #96   ; P ($0240-$0244)
  .db #160, #64, #00, #112  ; Q ($0244-$0247)
  .db #160, #66, #00, #128  ; R ($0248-$024b)
  .db #160, #68, #00, #144  ; S ($024c-$024f)
  .db #160, #70, #00, #160  ; T ($0250-$0253)
  .db #160, #72, #00, #176  ; U ($0254-$0257)
  .db #176, #74, #00, #80   ; V ($0258-$025b)
  .db #176, #76, #00, #96   ; W ($025c-$025f)
  .db #176, #78, #00, #112  ; X ($0260-$0263)
  .db #176, #80, #00, #128  ; Y ($0264-$0267)
  .db #176, #82, #00, #144  ; Z ($0268-$026b)

  ; Stickman
  ; #88 is an empty sprite tile
  .db #40, #88, #00, #40  ; Head    ($026c-$026f)
  .db #48, #88, #00, #40  ; Body    ($0270-$0273)
  .db #48, #88, #00, #36  ; LArm    ($0274-$0277)
  .db #48, #88, #00, #44  ; RArm    ($0278-$027b)
  .db #56, #88, #00, #36  ; LLeg    ($027c-$027f)
  .db #56, #88, #00, #44  ; RLeg    ($0280-$0283)

  ; Hanger
  .db #32, #101, #03, #40   ; ($0284-$0287)
  .db #32, #99, #03, #32    ; ($0288-$028b)
  .db #32, #100, #03, #24   ; ($028c-$028f)
  .db #40, #98, #03, #24    ; ($0290-$0293)
  .db #48, #98, #03, #24    ; ($0294-$0297)
  .db #56, #98, #03, #24    ; ($0298-$029b)
  .db #64, #98, #03, #24    ; ($029c-$029f)
  .db #72, #96, #03, #24    ; ($02a0-$02a3)

  ; Word to be guessed
  .db #72, #88, #00, #60    ; ($02a4-$02a7)
  .db #72, #88, #00, #76    ; ($02a8-$02ab)
  .db #72, #88, #00, #92    ; ($02ac-$02af)
  .db #72, #88, #00, #108   ; ($02b0-$02b3)
  .db #72, #88, #00, #124   ; ($02b4-$02b7)
  .db #72, #88, #00, #140   ; ($02b8-$02bb)
  .db #72, #88, #00, #156   ; ($02bc-$02bf)

;----------------------------------------------------------------
; WORDS
;----------------------------------------------------------------
words:               ; each word has his length and eight letters at most
  .db #07, #54, #32, #68, #32, #58, #46, #32, #00    ;  LASANHA
  .db #07, #42, #72, #70, #40, #34, #60, #54, #00    ;  FUTEBOL
  .db #03, #62, #32, #60, #00, #00, #00, #00, #00    ;  PAO
  .db #04, #54, #32, #70, #32, #00, #00, #00, #00    ;  LATA

seed:
  .db #01
;----------------------------------------------------------------
; BACKGROUND
;----------------------------------------------------------------

background:
  .include "bg.asm"

;----------------------------------------------------------------
; INTERRUPT VECTORS
;----------------------------------------------------------------

  .org $fffa

  .dw NMI
  .dw RESET
  .dw IRQ

;----------------------------------------------------------------
; CHR-ROM bank
;----------------------------------------------------------------

  .base $0000
  .incbin "sprites.chr"
