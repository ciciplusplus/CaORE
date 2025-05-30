#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint32_t uint;
typedef uint8_t  byte;

/* ----------  forward (already supplied) ---------- */
static int MY_String2Blob_helper(int n)
{
    if (n < 0x1a)          return n + 'a';        /* a–z  */
    else if (n < 0x34)     return n + '\'';       /* A–Z  */
    else if (n > 0x3d)     return (n == 0x3e) ? '_' : '-';  /* 62, 63 */
    else                   return n - 4;          /* 0–9  */
}

char *MY_String2Blob(char *s)
{
    size_t in_len = strlen(s);
    int out_len   = (int)((in_len << 3) / 6);
    out_len = (out_len == 0) ? 1 : out_len + 2;

    char *out = malloc(out_len + 1);
    if (!out) return NULL;
    memset(out, 0, out_len + 1);

    int i = 0, out_i = 0;
    unsigned u_bits_left = 8;

    while (i < (int)in_len) {
        uint32_t v = ((byte)s[i]) >> (8 - u_bits_left);

        if (u_bits_left < 6) {                         /* need next byte */
            i++;
            if (i < (int)in_len) {
                v |= ((byte)s[i]) << u_bits_left;
                u_bits_left += 2;
            }
        } else {
            u_bits_left -= 6;
            if (u_bits_left == 0) {
                i++;
                u_bits_left = 8;
            }
        }
        out[out_i++] = (char)MY_String2Blob_helper(v & 0x3f);
    }
    if (out_len != 1 && u_bits_left == 8)              /* trailing pad */
        out[out_i] = (char)MY_String2Blob_helper(0);

    return out;
}

/* ----------  reverse direction that we add now ---------- */

/* Map encoded character back to its 6‑bit value */
static int MY_Blob2String_helper(char c)
{
    if      (c >= 'a' && c <= 'z') return c - 'a';          /* 0–25 */
    else if (c >= 'A' && c <= 'Z') return c - 'A' + 26;     /* 26–51 */
    else if (c >= '0' && c <= '9') return c - '0' + 52;     /* 52–61 */
    else if (c == '_')              return 62;              /* 62    */
    else                            return 63;              /* '-'   */
}

/* Decode the blob back to the original byte string */
char *MY_Blob2String(char *blob)
{
    size_t  in_len  = strlen(blob);
    size_t  max_out = (in_len * 6) / 8 + 2;                 /* safe upper bound */
    char   *out     = malloc(max_out);
    if (!out) return NULL;

    int     out_i       = 0;
    uint8_t curr_byte   = 0;
    int     bit_offset  = 0;                                /* bits already filled (LSB‑first) */

    for (size_t i = 0; i < in_len; ++i) {
        int v = MY_Blob2String_helper(blob[i]) & 0x3f;
        int free_bits = 8 - bit_offset;

        if (free_bits >= 6) {                               /* fits into current byte */
            curr_byte |= v << bit_offset;
            bit_offset += 6;
            if (bit_offset == 8) {
                out[out_i++] = (char)curr_byte;
                curr_byte  = 0;
                bit_offset = 0;
            }
        } else {                                            /* splits across bytes */
            curr_byte |= (v & ((1 << free_bits) - 1)) << bit_offset;
            out[out_i++] = (char)curr_byte;
            curr_byte   = v >> free_bits;
            bit_offset  = 6 - free_bits;
        }
    }
    /* Any leftover bits are padding zeros that the encoder added — ignore them */
    out[out_i] = '\0';
    return out;
}

/* --------------------  tests -------------------- */

int main(void)
{
    /*   the original forward‑only tests   */
    if (strcmp(MY_String2Blob("f|1|i|25470|v|1.0.1j|"),
               "MXxm8LgFYudn3adF2XxmUaJlXOgFa") != 0)
        printf("FAILED 1\n"); else printf("PASSED 1\n");

    if (strcmp(MY_String2Blob("f|204|i|25470|y|1|nid|0|l|en|u|ae87b081fddccaf8fc32180b52b639b10a662e26|"),
               "MXNmWqdFPXNm1qZnWWxE8fdFULgz8bdFSXxzUXxD8fwz4CJyWGtmMrgzJnwyMHJzJnJmXGdmIvJmIzZm5iwmWeMn2itzYydFa") != 0)
        printf("FAILED 2\n"); else printf("PASSED 2\n");

    /*   new reverse‑direction tests   */
    if (strcmp(MY_Blob2String("MXxm8LgFYudn3adF2XxmUaJlXOgFa"),
               "f|1|i|25470|v|1.0.1j|") != 0)
        printf("FAILED 3\n"); else printf("PASSED 3\n");

    if (strcmp(MY_Blob2String("MXNmWqdFPXNm1qZnWWxE8fdFULgz8bdFSXxzUXxD8fwz4CJyWGtmMrgzJnwyMHJzJnJmXGdmIvJmIzZm5iwmWeMn2itzYydFa"),
               "f|204|i|25470|y|1|nid|0|l|en|u|ae87b081fddccaf8fc32180b52b639b10a662e26|") != 0)
        printf("FAILED 4\n"); else printf("PASSED 4\n");

    return 0;
}
