#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint32_t uint;
typedef uint8_t byte;

int MY_String2Blob_helper(int param_1)
{
  char cVar1;
  int iVar2;
  
  cVar1 = (char)param_1;
  if (param_1 < 0x1a) {
    cVar1 = cVar1 + 'a';
  }
  else {
    if (param_1 < 0x34) {
      cVar1 = cVar1 + '\'';
    }
    else {
      if (0x3d < param_1) {
        if (param_1 == 0x3e) {
          iVar2 = 0x5f;
        }
        else {
          iVar2 = 0x2d;
        }
        return iVar2;
      }
      cVar1 = cVar1 + -4;
    }
  }
  return (int)cVar1;
}


char * MY_String2Blob(char *param_1)

{
  char cVar1;
  char *pcVar2;
  uint uVar3;
  size_t sVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int local_24;
  
  sVar4 = strlen(param_1);
  local_24 = (int)(sVar4 << 3) / 6;
  if (local_24 == 0) {
    local_24 = 1;
  }
  else {
    local_24 = local_24 + 2;
  }
  pcVar2 = (char *) malloc(local_24 + 1);
  memset(pcVar2,0,local_24 + 1);
  if (pcVar2 != (char *)0x0) {
    iVar6 = 0;
    uVar5 = 8;
    iVar7 = iVar6;
    while (iVar6 < (int)sVar4) {
      uVar3 = (int)(uint)(byte)param_1[iVar6] >> (8 - uVar5 & 0xff);
      if ((int)uVar5 < 6) {
        iVar6 = iVar6 + 1;
        if (iVar6 < (int)sVar4) {
          uVar3 = uVar3 | (uint)(byte)param_1[iVar6] << (uVar5 & 0xff);
          uVar5 = uVar5 + 2;
        }
      }
      else {
        uVar5 = uVar5 - 6;
        if (uVar5 == 0) {
          iVar6 = iVar6 + 1;
          uVar5 = 8;
        }
      }
      cVar1 = MY_String2Blob_helper(uVar3 & 0x3f);
      pcVar2[iVar7] = cVar1;
      iVar7 = iVar7 + 1;
    }
    if (local_24 != 1 && uVar5 == 8) {
      cVar1 = MY_String2Blob_helper(0);
      pcVar2[iVar7] = cVar1;
    }
  }
  return pcVar2;
}

int main() {
  if (strcmp(MY_String2Blob("f|1|i|25470|v|1.0.1j|"), "MXxm8LgFYudn3adF2XxmUaJlXOgFa") != 0) {
    printf("FAILED 1\n");
  } else {
    printf("PASSED 1\n");
  }
  if (strcmp(MY_String2Blob("f|204|i|25470|y|1|nid|0|l|en|u|ae87b081fddccaf8fc32180b52b639b10a662e26|"), "MXNmWqdFPXNm1qZnWWxE8fdFULgz8bdFSXxzUXxD8fwz4CJyWGtmMrgzJnwyMHJzJnJmXGdmIvJmIzZm5iwmWeMn2itzYydFa") != 0) {
    printf("FAILED 2\n");
  } else {
    printf("PASSED 2\n");
  }
  return 0;
}
