
#  ```python
#  #PymoNNto/Examples_Docs/speed #initialize
#  src = np.random.rand(5000) < 0.01    # 5k pre synaptic neurons (1% spikes)
#  dst = np.random.rand(10000) < 0.01   # 10k post synaptic neurons (1% spikes)
#  ```

#search all markdown files

#select code sections

#check and extract first code line (path to py file)

#if file exists: and file is .py

#load py file content replace code block

# importing the library
import os

dirname = '../../PymoNNto'

def get_python_file_content(py_file_name, py_file_block):
    py_file = open(dirname + py_file_name, "r")
    py_text = py_file.read()
    py_file.close()

    if py_file_block is not None:
        for block in py_text.split('###'):
            block_split=block.split('\n')
            if len(block_split)>1:
                block_start = block_split[0].replace(' ','')
                block_content = '\n'.join(block_split[1:-1])
                if block_start == py_file_block:
                    return block_content

    return py_text
    # print(py_file_name)
    # print()

def check_and_replace_code_block(md_part):
    if len(md_part) > 8 and md_part[0:6] == 'python':  # partial is a python code block
        code_split = md_part[6:].split('\n')
        if len(code_split) > 2:
            replace_file_line = code_split[1]
            pfn_split = replace_file_line.replace(' ','').split('#')
            if len(pfn_split)>1:
                py_file_name = pfn_split[1]
                py_file_block = None
                if len(pfn_split)>2:
                    py_file_block = pfn_split[2]

                if os.path.isfile(dirname + py_file_name):
                    py_text = get_python_file_content(py_file_name, py_file_block)

                    return 'python\n'+replace_file_line+'\n'+py_text+'\n', True
    return md_part, False


def update_md_file(md_file_name):
    md_changed = False
    #open, read file and replace code blocks
    md_file = open(md_file_name, "r")
    md_text = md_file.read()
    md_split = md_text.split('```')  # python
    result = md_split[0]
    for partial in md_split[1:]:
        content, changed = check_and_replace_code_block(partial)
        result += '```' + content
        md_changed = md_changed or changed
    md_file.close()

    if md_changed:
        #overwrite file
        print(md_file_name)
        md_file = open(md_file_name, "w")
        md_file.write(result)
        md_file.close()


def create_readme(content):
    f = open("../readme.md", "w")
    f.write("https://pymonnto.readthedocs.io/\r\n\r\n")
    for c in content:
        text = open(c, "r").read()
        print(text)
        f.write(text)
        f.write("\r\n")
    f.close()

#update code blocks
for path, dirc, files in os.walk(dirname):
    for name in files:
        if name.endswith('.md'):
            md_file_name = path.replace('\\','/')+'/'+name
            update_md_file(md_file_name)


#overwrite readme file
create_readme([
        "../docs/index.md",
        "../docs/Introduction/installation.md",
        "../docs/Introduction/basics.md",
        "../docs/Introduction/Tagging.md",
        "../docs/Introduction/User_Interface.md",
        "../docs/Introduction/input_switch.md",
])

