#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include <sys/time.h>

typedef uint32_t uint;

uint MY_gettimeofday_milliseconds(void)
{
  uint iVar1;
  struct timeval local_10;
  
  iVar1 = gettimeofday(&local_10,(void *)0x0);
  if (iVar1 == 0) {
    iVar1 = local_10.tv_sec * 1000 + (uint)local_10.tv_usec / 1000;
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

int main() {
  int a = MY_gettimeofday_milliseconds();
  printf("millis %u\n", a);
  return 0;
}