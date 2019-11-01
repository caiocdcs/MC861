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

NMI:

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
ReadStartDone:        ; handling this button is done



; Pressed Up
ReadUp: 
  LDA $4016           ; player 1 - Up
  AND #%00000001      ; only look at bit 0
  BEQ ReadUpDone      ; branch to ReadUpDone if button is NOT pressed (0)
  LDX #$01
ReadUpDone:           ; handling this button is done

; Pressed Down
ReadDown: 
  LDA $4016           ; player 1 - Down
  AND #%00000001      ; only look at bit 0
  BEQ ReadDownDone    ; branch to ReadDownDone if button is NOT pressed (0)
  LDX #$01
ReadDownDone:         ; handling this button is done

; Pressed Left
ReadLeft: 
  LDA $4016           ; player 1 - Left
  AND #%00000001      ; only look at bit 0
  BEQ ReadLeftDone    ; branch to ReadLeftDone if button is NOT pressed (0)
  LDX #$01
ReadLeftDone:         ; handling this button is done

; Pressed Right
ReadRight: 
  LDA $4016           ; player 1 - Right
  AND #%00000001      ; only look at bit 0
  BEQ ReadRightDone   ; branch to ReadRightDone if button is NOT pressed (0)
  LDX #$01
ReadRightDone:        ; handling this button is done

  jmp LatchController


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
  .db #01, #04
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
