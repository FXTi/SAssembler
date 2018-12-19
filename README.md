# SAssembler

Don't support related addressing from PC register!

Sample:
```
IN R0,00H
IN R1,00H
ADD R0,R1 
OUT 40H,R0
HLT
```

Result:
```
00 20 ; IN R0,00H
01 00
02 21 ; IN R1,00H
03 00
04 04 ; ADD R0,R1 
05 30 ; OUT 40H,R0
06 40
07 50 ; HLT
```

Destination register first, then the Source register!
