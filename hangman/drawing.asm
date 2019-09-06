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
