LatchController:
  LDA #$01
  STA $4016
  LDA #$00
  STA $4016       ; tell both the controllers to latch buttons


ReadA: 
  LDA $4016       ; player 1 - A
  AND #%00000001  ; only look at bit 0
  BEQ ReadADone   ; branch to ReadADone if button is NOT pressed (0)
                  ; add instructions here to do something when button IS pressed (1)
ReadADone:        ; handling this button is done
  

ReadB: 
  LDA $4016       ; player 1 - B
  AND #%00000001  ; only look at bit 0
  BEQ ReadBDone   ; branch to ReadBDone if button is NOT pressed (0)
                  ; add instructions here to do something when button IS pressed (1)
ReadBDone:        ; handling this button is done

ReadSelect: 
  LDA $4016       ; player 1 - Select
  AND #%00000001  ; only look at bit 0
  BEQ ReadSelectDone   ; branch to ReadBDone if button is NOT pressed (0)
                  ; add instructions here to do something when button IS pressed (1)
ReadSelectDone:        ; handling this button is done

ReadStart: 
  LDA $4016       ; player 1 - Select
  AND #%00000001  ; only look at bit 0
  BEQ ReadStartDone   ; branch to ReadBDone if button is NOT pressed (0)
                  ; add instructions here to do something when button IS pressed (1)
ReadStartDone:        ; handling this button is done

ReadUp: 
  LDA $4016       ; player 1 - Up
  AND #%00000001  ; only look at bit 0
  BEQ ReadUpDone   ; branch to ReadUpDone if button is NOT pressed (0)
                  ; add instructions here to do something when button IS pressed (1)
AlphabetUp:
  LDA $100
  SEC             ; make sure carry flag is set
  SBC #$09        ; X = X - 9 
                  ; check if X < 0
  STA $0100       ; save position of vector
  jsr MoveUp

ReadUpDone:        ; handling this button is done

ReadDown: 
  LDA $4016       ; player 1 - Down
  AND #%00000001  ; only look at bit 0
  BEQ ReadDownDone   ; branch to ReadDownDone if button is NOT pressed (0)
                  ; add instructions here to do something when button IS pressed (1)
AlphabetDown: 
  LDA $100
  CLC             ; make sure carry flag is set
  ADC #$09        ; X = X + 9 
                  ; check if X > 26
  STA $0100       ; save position of vector
  jsr MoveDown

ReadDownDone:        ; handling this button is done

ReadLeft: 
  LDA $4016       ; player 1 - Left
  AND #%00000001  ; only look at bit 0
  BEQ ReadLeftDone   ; branch to ReadLeftDone if button is NOT pressed (0)
                  ; add instructions here to do something when button IS pressed (1)

AlphabetLeft:
  LDA #100
  SEC             ; make sure carry flag is set
  SBC #$01        ; X = X - 1
                  ; check if X < 0
  STA #100       ; save position of vector
  jsr MoveLeft

ReadLeftDone:        ; handling this button is done

ReadRight: 
  LDA $4016       ; player 1 - Right
  AND #%00000001  ; only look at bit 0
  BEQ ReadRightDone   ; branch to ReadRightDone if button is NOT pressed (0)
                  ; add instructions here to do something when button IS pressed (1)

AlphabetRight:
  LDA $100
  CLC             ; make sure carry flag is set
  ADC #$01        ; X = X + 1
                  ; check if X > 26 
  STA $0100       ; save position of vector
  jsr MoveRight

ReadRightDone:        ; handling this button is done

  rts