# Emulador

Qualquer linguagem, exemplos em C

## Pseudocódigo

Le_cartucho(char *arquivo) -> coloca em um vetor de 64kB
while (1) {
  instrucao = Decodifica(PC);
  ...
  switch(opcode_instrucao) {
    case 0: erro
      ... (soma, memoria, ... funcao por instrucao...)
      break;
    case 1: erro
      ...
      break;
    ...
    default: ERRO
  }
  Log(____);
  Temporizacao();
}

## Other info

Memória do processador: 64kB (malloc 64kB, ou algo do tipo)

## Functions
- Le_cartucho
- Decodifica
- Log (imprime formato da instrucao, depuracao)
- Temporizacao: casar o tempo com um ciclo do processador
- Varios programas para testes, testes pelos grupos (100 problemas de 5/poucas instrucoes)
- Makefile para rodar programa automaticamente

