; Author: tokumaru
; http://forums.nesdev.com/viewtopic.php?%20p=58138#58138
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

    LDX #0
    Reset:
    ; Pressed Up
    ReadUp: 
    LDA $4016           ; player 1 - Up
    AND #%00000001      ; only look at bit 0
    BEQ ReadUpDone      ; branch to ReadUpDone if button is NOT pressed (0)

    UpButtonPressed:
    INX
    ReadUpDone:           ; handling this button is done

    ; Pressed Down
    ReadDown: 
    LDA $4016           ; player 1 - Down
    AND #%00000001      ; only look at bit 0
    BEQ ReadDownDone    ; branch to ReadDownDone if button is NOT pressed (0)

    DownButtonPressed:
    INX
    ReadDownDone:         ; handling this button is done

    ; Pressed Left
    ReadLeft: 
    LDA $4016           ; player 1 - Left
    AND #%00000001      ; only look at bit 0
    BEQ ReadLeftDone    ; branch to ReadLeftDone if button is NOT pressed (0)
    LeftButtonPressed:
    INX
    ReadLeftDone:         ; handling this button is done

    ; Pressed Right
    ReadRight: 
    LDA $4016           ; player 1 - Right
    AND #%00000001      ; only look at bit 0
    BEQ ReadRightDone   ; branch to ReadRightDone if button is NOT pressed (0)
    RightButtonDone:
    INX
    ReadRightDone:        ; handling this button is done

    ControllersDone:

NMI:

   ;NOTE: NMI code goes here

IRQ:

   ;NOTE: IRQ code goes here

;----------------------------------------------------------------
; interrupt vectors
;----------------------------------------------------------------

   .org $fffa

   .dw NMI
   .dw Reset
   .dw IRQ



