docs_ce_folder = '../docs/Classical_Examples/'
ex_folder = '../Examples/'
content = [
    "Brunel_Hakim",
    "Wang_Buzaki",
    "Diesmann_Synfire",
    "Hindmarsh_Rose",
    "Hodgkin_Huxley",
    "Hopfield",
    "Izhikevich",
    "LeakyIntegrateAndFire"]


for n in content:
    md_file_name = docs_ce_folder+n+'.md'
    py_file_name = ex_folder+n+'.py'

    md_file = open(md_file_name, "r")
    py_file = open(py_file_name, "r")

    md_text = md_file.read()
    py_text = py_file.read()

    partial_md = md_text.split('```')
    partial_md[1] = '\r\n```python\r\n'+py_text+'\r\n```\r\n'


    md_file.close()
    py_file.close()



    md_file = open(md_file_name, "w")

    for str in partial_md:
        md_file.write(str)

    md_file.close()


#f = open("readme.md", "w")

#for c in content:
#    text = open(c, "r").read()
#    print(text)
#    f.write(text)
#    f.write("\r\n")

#f.close()

