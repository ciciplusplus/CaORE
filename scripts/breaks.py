#python
# ---- configuration ----
# any mixture of function names, lines ("file.c:42"), or raw addresses ("0x4006f0")
bkpts = [
    "*0x0001b2fc",
    "*0x00104830",
#    "*0x00108074", # <-- login, 0x12
    "*0x00104c24",
    "*0x00104624",
#    "*0x0010618c", # <-- PLAY, 0x27
    "*0x0010465c",
    "*0x00105cd4",
    "*0x0010562c",
    "*0x0010881c",
    "*0x001051f4",
    "*0x0010513c",
    "*0x001050c0",
    "*0x00105050",
#    "*0x00105914", # <-- list character, 0x26
    "*0x00017eec",
    "*0x00018194",
    "*0x000180c4",
    "*0x00019020",
    "*0x00022e10",
    "*0x00018050",
    "*0x00022ccc",
    "*0x00022e88",
    "*0x00017bd0",
    "*0x00019218",
    "*0x000188c0",
    "*0x00019d3c",
    "*0x000187b0",
    "*0x0001830c",
    "*0x00018290",
    "*0x00019a18",
    "*0x000191c4",
    "*0x000a9ddc",
    "*0x000a9820",
    "*0x000a9790",
    "*0x0001cd84",
    "*0x00019b70",
    "*0x00019978",
    "*0x00018f80",
    "*0x00018ee0",
    "*0x00017c18",
    "*0x00120dcc",
    "*0x00017d1c",
    "*0x0001accc",
    "*0x0001c504",
    "*0x0001c0e0",
    "*0x0001be84",
    "*0x00018538",
    "*0x00018434",
    "*0x0001bc1c",
    "*0x0001b96c",
    "*0x0001e580",
    "*0x00018364",
    "*0x000183cc",
    "*0x0001e700",
    "*0x0001cecc",
    "*0x002b0510",
    "*0x002af7b8",
    "*0x002afd80",
    "*0x002afea4",
    "*0x002af508",
    "*0x002af598",
    "*0x002b03e4",
    "*0x002af76c",
    "*0x002af4e0",
    "*0x00247a58",
    "*0x00247064",
    "*0x002471ec",
    "*0x002476b4",
    "*0x00247840",
    "*0x00246e1c",
    "*0x002462b8",
    "*0x00246ab8",
    "*0x002497b4",
    "*0x00249418",
    "*0x00246074",
    "*0x0001b760"
]

# ---- implementation ----
import gdb

for spec in bkpts:
    # gdb.Breakpoint handles every location syntax gdb understands
    gdb.Breakpoint(spec)
    gdb.write(f"Set breakpoint at {spec}\n")
# end
