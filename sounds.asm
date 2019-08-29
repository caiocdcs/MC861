
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
; TODO: GameOverSound
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
