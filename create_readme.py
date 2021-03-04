content = [
    "docs/index.md",
    "docs/Introduction/installation.md",
    "docs/Introduction/installation2.md",
    "docs/Tutorials/basics.md",
    "docs/Tutorials/Synapses_and_Input.md",
    "docs/Tutorials/User_Interface.md"]


f = open("readme.md", "w")

f.write("https://pymonnto.readthedocs.io/\r\n\r\n")

for c in content:
    text = open(c, "r").read()
    print(text)
    f.write(text)
    f.write("\r\n")


f.close()

