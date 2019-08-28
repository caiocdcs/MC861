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

RESET:
  sei
  cld
; Disable NMI and rendering
  lda #%00000000
  sta PPU_CTRL
  lda #%00000000
  sta PPU_MASK

; Wait for PPU
  lda PPU_STATUS
vBlankWait1:
  bit PPU_STATUS
  bpl vBlankWait1
  
; Clear RAM
  lda #$00
  ldx #$00
ClearLoop:
  sta $0000, X
  sta $0100, X
  sta $0200, X
  sta $0300, X
  sta $0400, X
  sta $0500, X
  sta $0600, X
  sta $0700, X
  inx
  cpx #$00
  bne ClearLoop

; Wait for PPU
vBlankWait2:
  bit PPU_STATUS
  bpl vBlankWait2

  ; Initialize Game
  jsr Initialize
  jsr LoadPalettes
  jsr LoadSprites
  jsr ConfigurePPU
  jsr WaitBlank
  jsr EnableSound
  jsr Loop

;----------------------------------------------------------------
; ENABLE SOUND
;----------------------------------------------------------------

EnableSound:
  lda #$FF ; typical
  sta $4000 ; write
  ; lda #$0F
  ; sta $4015 ;enable Square 1, Square 2, Triangle and Noise channels.  Disable DMC.

;----------------------------------------------------------------
; PPU CONFIGURATION
;----------------------------------------------------------------

ConfigurePPU:
  lda #%10000000   ; enable NMI, sprites from Pattern Table 0
  sta PPU_CTRL

  lda #%00010000   ; enable sprites
  sta PPU_MASK
  rts

; Makes safe update of screen
WaitBlank:
  lda PPU_STATUS
  bpl WaitBlank ; keet checking until bit is 7 (VBlank)

;----------------------------------------------------------------
; LOAD PALETTES
;----------------------------------------------------------------

LoadPalettes:
  lda PPU_STATUS    ; read PPU status to reset the high/low latch
  lda #$3F
  sta PPU_ADDR    ; write the high byte of $3F00 address
  lda #$00
  sta PPU_ADDR    ; write the low byte of $3F00 address
  ldx #$00
LoadPallete:
  lda palette, x
  sta PPU_DATA
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
  cpx #$00bc            ; Compare X to hex $00bc (each 4 is a sprite) -- change here if more sprites are needed
  bne LoadSprite        ; Branch to LoadSprite if compare was Not Equal to zero

  lda #%10000000   ; enable NMI, sprites from Pattern Table 1
  sta PPU_CTRL

  lda #%00010000   ; enable sprites
  sta PPU_MASK

;----------------------------------------------------------------
; FOREVER LOOP
;----------------------------------------------------------------

Forever:
  jmp Forever     ;jump back to Forever, infinite loop

;----------------------------------------------------------------
; GAME LOGIC
;----------------------------------------------------------------

; main loop
Loop:
  jsr CheckCurrentLetter
  jsr CheckWin
  jsr LatchController
  jmp Loop

; the size of the word in address $0500
; $0501 will be the current letter choosed, to check in the word
; $0502 will store how many parts of the body will be displayed ( how many errors )
; $0503 will store if a letter was correctly guessed during that round
; $0504 how many letters guessed
; initizalize the current word ( banana ) starting in address $0508 ( first letter ) 
; $0500 + the letter code choosed will be the place to store if the current letter was guessed right, beginning in $0520
Initialize:
  lda #$06 ; word size
  sta $0500
  lda #$22 ; B
  sta $0508
  lda #$20 ; A
  sta $0509
  lda #$3A ; N
  sta $050A
  lda #$20 ; A
  sta $050B
  lda #$3A ; N
  sta $050C
  lda #$20 ; A
  sta $050D

  lda #32
  sta $0501

  lda #$00
  sta $0505 ; position for count the tile position that will be drawn, each sprite has 4 bytes
  rts

CheckCurrentLetter:
  ldx #$00
  lda $0501
  cmp #$00
  beq CheckCurrentLetterEnd
CheckCurrentLetterLoop:
  lda $0508, x
  cmp $0501
  bne CheckCurrenterLetterIncX
  ; set letter as correct
  tay
  lda #$01
  sta $0500, y
  sta $0503 ; set that a letter was guessed
  inc $0504
CheckCurrenterLetterIncX:
  inx
  cpx $0500 ; iterate with the size of the word to guess
  bne CheckCurrentLetterLoop
  ; check if a letter was guessed
  lda $0503
  cmp #$01
  beq CheckCurrentLetterEnd ; if equals a letter was guessed and the value is equal to one, don't make a sound
  ;if an error happened
  inc $0502 ; inc how many erros ocurred
  ;jsr MakeSound
CheckCurrentLetterEnd:
  lda #$00
  sta $0503
  sta $0501
  rts

CheckWin:
  lda $0504
  cmp $0500
  beq Win
  lda $0502
  cmp #06
  beq GameOver
  rts
Win:
  jsr DrawWin
; TODO: Link B to command 'jsr RESET', if in state Win or GameOver (maybe use memory address to know)
  brk
GameOver:
  jsr DrawGameOver
; TODO: Link B to command 'jsr RESET', if in state Win or GameOver (maybe use memory address to know)
  brk

;----------------------------------------------------------------
; SOUND (More about sounds: https://patater.com/nes-asm-tutorials/day-14/)
;----------------------------------------------------------------

MoveSound:
  ; bit 7: enables/disables sweep (if sweep is 0, tone continues)
  ; bits 4-6: how fast from 0-7
  ; bit 3: 1 - increase, 0 - decrease frequency
  ; bits 0-2: shift to get frequency
  lda #%110101011
  sta $4001
  lda #$aa
  sta $4002
  lda #$a0
  sta $4003
  lda #%00000001
  sta $4015
  rts

WrongLetterSound:
  lda #%11001011
  sta $4001
  lda #$aa
  sta $4002
  lda #$aa
  sta $4003
  lda #%00000001
  sta $4015
  rts

; TODO: CorrectLetterSound
; TODO: WinSound
; TODO: Improve game over sound
GameOverSound:
  lda #%11001000
  sta $4001
  lda #$cc
  sta $4002
  lda #$a0
  sta $4003
  lda #%00000001
  sta $4015
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

;----------------------------------------------------------------
; NMI (Non-Maskable Interrupt)
;----------------------------------------------------------------

NMI:
  jsr DrawScreen
  jsr DrawErrors
  jsr DrawWord
  jmp EndNMI

;----------------------------------------------------------------
; MAIN SCREEN FUNCTION
;----------------------------------------------------------------

DrawScreen:
  lda #$00    ; load $00 to A
  sta OAM_ADDR   ; store first part in 2003
  sta OAM_ADDR   ; store second part in 2003
  jsr SetUpControllers

  rts

;----------------------------------------------------------------
; CONTROLLERS
;----------------------------------------------------------------

; $0300 saves the selector's offset horizontal position
; $0301 saves the selector's offset vertical position 
; $0302 alphabet position
 
SetUpControllers:
  lda #$02
  sta $4014   ; set the high byte (02) of the RAM address, start the transfer

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
; TODO: Link B to command 'jsr RESET', if in state Win or GameOver (maybe use memory address to know)
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
ReadStartDone:        ; handling this button is done

; Pressed Up
ReadUp: 
  LDA $4016           ; player 1 - Up
  AND #%00000001      ; only look at bit 0
  BEQ ReadUpDone      ; branch to ReadUpDone if button is NOT pressed (0)
CanMoveUp:
  LDA $0301           ; load selector y position
  SBC #1              ; move up y = y - 1
  BMI ReadUpDone      ; if negative, dont move selector
  STA $0301           ; else, move onde postion up
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
  ADC #1              ; move up y = y + 1
  CMP #$4             ; if y > 4
  BPL ReadDownDone    ; dont move the selector    
  STA $0301           ; else, move onde postion down
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
  SBC #1              ; move up x = x - 1
  BMI ReadLeftDone    ; if negative, dont move selector      
  STA $0300           ; else, move onde postion left
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
  ADC #1              ; move up x = x + 1
  CMP #$7             ; if x > 7
  BPL ReadRightDone   ; dont move the selector
  STA $0300           ; else, move onde postion right

MoveRight:           
  LDA $0203           ; load sprite X position
  CLC                 ; make sure carry flag is set
  ADC #$10            ; A = A + 16
  STA $0203           ; save sprite X position
  jsr MoveSound
ReadRightDone:        ; handling this button is done
  rts

;----------------------------------------------------------------
; DRAWING FUNCTIONS
;----------------------------------------------------------------

DrawWin:
  ; Disable selector
  lda #00
  sta $0200
  lda #88
  sta $0201
  lda #00
  sta $0203
  ; Y
  lda #112
  sta $0208
  lda #80
  sta $0209
  lda #02
  sta $020a
  lda #84
  sta $020b
  ; O
  lda #112
  sta $020c
  lda #60
  sta $020d
  lda #02
  sta $020e
  lda #96
  sta $020f
  ; U
  lda #112
  sta $0210
  lda #72
  sta $0211
  lda #02
  sta $0212
  lda #108
  sta $0213
  ; W
  lda #112
  sta $0214
  lda #76
  sta $0215
  lda #02
  sta $0216
  lda #132
  sta $0217
  ; I
  lda #112
  sta $0218
  lda #48
  sta $0219
  lda #02
  sta $021a
  lda #144
  sta $021b
  ; N
  lda #112
  sta $021c
  lda #58
  sta $021d
  lda #02
  sta $021e
  lda #156
  sta $021f
  jsr DrawPressB
  ; Clear remaining letters
  lda #88
  sta $0205
  sta $0221
  sta $0225
  sta $0229
  sta $022d
  sta $0231
  sta $024d
  sta $024d
  sta $0251
  sta $0255
  sta $0259
  sta $025d
  sta $0261
  sta $0265
  sta $0269

  rts

DrawGameOver:
  ; Disable selector
  lda #00
  sta $0200
  lda #88
  sta $0201
  lda #00
  sta $0203
  ; G
  lda #112
  sta $0204
  lda #45
  sta $0205
  lda #01
  sta $0206
  lda #72
  sta $0207
  ; A
  lda #112
  sta $0208
  lda #33
  sta $0209
  lda #01
  sta $020a
  lda #84
  sta $020b
  ; M
  lda #112
  sta $020c
  lda #57
  sta $020d
  lda #01
  sta $020e
  lda #96
  sta $020f
  ; E
  lda #112
  sta $0210
  lda #41
  sta $0211
  lda #01
  sta $0212
  lda #108
  sta $0213
  ; O
  lda #112
  sta $0214
  lda #61
  sta $0215
  lda #01
  sta $0216
  lda #132
  sta $0217
  ; V
  lda #112
  sta $0218
  lda #75
  sta $0219
  lda #01
  sta $021a
  lda #144
  sta $021b
  ; E
  lda #112
  sta $021c
  lda #41
  sta $021d
  lda #01
  sta $021e
  lda #156
  sta $021f
  ; R
  lda #112
  sta $0220
  lda #67
  sta $0221
  lda #01
  sta $0222
  lda #168
  sta $0223
  ; Dead Face (1/4)
  lda #96
  sta $0224
  lda #12
  sta $0225
  lda #01
  sta $0226
  lda #116
  sta $0227
  ; Dead Face (2/4)
  lda #96
  sta $0228
  lda #13
  sta $0229
  lda #01
  sta $022a
  lda #124
  sta $022b
  ; Dead Face (3/4)
  lda #104
  sta $022c
  lda #14
  sta $022d
  lda #01
  sta $022e
  lda #116
  sta $022f
  ; Dead Face (4/4)
  lda #104
  sta $0230
  lda #15
  sta $0231
  lda #01
  sta $0232
  lda #124
  sta $0233
  jsr DrawPressB
  ; Clear remaining letters
  lda #88
  sta $024d
  sta $0251
  sta $0255
  sta $0259
  sta $025d
  sta $0261
  sta $0265
  sta $0269

  rts

DrawPressB:
  ; P
  lda #132
  sta $0234
  lda #62
  sta $0235
  lda #90
  sta $0237
  ; R
  lda #132
  sta $0238
  lda #66
  sta $0239
  lda #100
  sta $023b
  ; E
  lda #132
  sta $023c
  lda #40
  sta $023d
  lda #110
  sta $023f
  ; S
  lda #132
  sta $0240
  lda #68
  sta $0241
  lda #120
  sta $0243
  ; S
  lda #132
  sta $0244
  lda #68
  sta $0245
  lda #130
  sta $0247
  ; B
  lda #132
  sta $0248
  lda #34
  sta $0249
  lda #150
  sta $024b

  rts

;----------------------------------------------------------------
; DRAW ALPHABET (DISABLED LETTERS)
;----------------------------------------------------------------
DisableA:
  lda #33
  sta $0205
  rts

DisableB:
  lda #35
  sta $0209
  rts

DisableC:
  lda #37
  sta $020d
  rts

DisableD:
  lda #39
  sta $0211
  rts

DisableE:
  lda #41
  sta $0215
  rts

DisableF:
  lda #43
  sta $0219
  rts

DisableG:
  lda #45
  sta $021d
  rts

DisableH:
  lda #47
  sta $0221
  rts

DisableI:
  lda #49
  sta $0225
  rts

DisableJ:
  lda #51
  sta $0229
  rts

DisableK:
  lda #53
  sta $022d
  rts

DisableL:
  lda #55
  sta $0231
  rts

DisableM:
  lda #57
  sta $0235
  rts

DisableN:
  lda #59
  sta $0239
  rts

DisableO:
  lda #61
  sta $023d
  rts

DisableP:
  lda #63
  sta $0241
  rts

DisableQ:
  lda #65
  sta $0245
  rts

DisableR:
  lda #67
  sta $0249
  rts

DisableS:
  lda #69
  sta $024d
  rts

DisableT:
  lda #71
  sta $0251
  rts

DisableU:
  lda #73
  sta $0255
  rts

DisableV:
  lda #75
  sta $0259
  rts

DisableW:
  lda #77
  sta $025d
  rts

DisableX:
  lda #79
  sta $0261
  rts

DisableY:
  lda #81
  sta $0265
  rts

DisableZ:
  lda #83
  sta $0269
  rts

;----------------------------------------------------------------
; DRAW HANGMAN
;----------------------------------------------------------------
DrawHead:
  lda #89
  sta $026d
  rts

DrawBody:
  lda #90
  sta $0271
  rts

DrawLeftArm:
  lda #92
  sta $0275
  rts

DrawRightArm:
  lda #93
  sta $0279
  rts

DrawLeftLeg:
  lda #94
  sta $027d
  rts

DrawRightLeg:
  lda #95
  sta $0281
  rts

;----------------------------------------------------------------
; DRAW WORD
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
; END NMI
;----------------------------------------------------------------

EndNMI:
  rti

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
  .db $0F,$31,$32,$33,$0F,$35,$36,$37,$0F,$39,$3A,$3B,$0F,$3D,$3E,$0F
  .db $0F,$29,$00,$20,$0F,$15,$26,$37,$0F,$1C,$15,$2B,$0F,$02,$38,$3C
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
  .db #32, #101, #00, #40   ; ($0284-$0287)
  .db #32, #99, #00, #32    ; ($0288-$028b)
  .db #32, #100, #00, #24   ; ($028c-$028f)
  .db #40, #98, #00, #24    ; ($0290-$0293)
  .db #48, #98, #00, #24    ; ($0294-$0297)
  .db #56, #98, #00, #24    ; ($0298-$029b)
  .db #64, #98, #00, #24    ; ($029c-$029f)
  .db #72, #96, #00, #24    ; ($02a0-$02a3)

  ; Word to be guessed
  .db #72, #88, #00, #60    ; ($02a4-$02a7)
  .db #72, #88, #00, #76    ; ($02a8-$02ab)
  .db #72, #88, #00, #92    ; ($02ac-$02af)
  .db #72, #88, #00, #108   ; ($02b0-$02b3)
  .db #72, #88, #00, #124   ; ($02b4-$02b7)
  .db #72, #88, #00, #140   ; ($02b8-$02bb)

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
