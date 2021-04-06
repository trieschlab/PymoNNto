from pathlib import Path

def py_to_md(py_file_name, md_file_name):

    if not Path(md_file_name).is_file():
        print('create', md_file_name)
        md_file = open(md_file_name, "x")
        md_text = '``` ```'
    else:
        md_file = open(md_file_name, "r")
        md_text = md_file.read()

    py_file = open(py_file_name, "r")
    py_text = py_file.read()

    #partial_py = py_text.split('\'\'\'\'\'')
    #description = ''
    #if len(partial_py) > 2:
    #    description = partial_py[1]
    #    print(description)

    text = '```python\r\n'+py_text+'\r\n```'#description+
    partial_md = md_text.split('```')
    if len(partial_md) > 2:
        partial_md[1] = text
    else:
        partial_md.append(text)
        print('not able to find code block in', md_file_name, '(add py file to end)')


    md_file.close()
    py_file.close()

    md_file = open(md_file_name, "w")

    for str in partial_md:
        md_file.write(str)

    md_file.close()



yml_file = open('mkdocs.yml', "r")

yml_text = yml_file.read()

for str in yml_text.split('\n'):
    if '.md' in str and '- ' in str and ':' in str and '.py' in str and '-->' in str and '<!---' in str:
        right_block=str.split('<!---')[1]
        while ' ' in right_block:
            right_block = right_block.replace(' ', '')
        right_block = right_block.replace('-->', '')

        files = right_block.split(':')

        print(files[0], '->', files[1])

        if len(files) == 2 and files[1][-3:] == '.md' and files[0][-3:] == '.py':
            py_to_md(files[0], 'docs/'+files[1])

yml_file.close()


'''
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
    py_to_md(py_file_name='Examples_Classical/'+n+'.py', md_file_name='docs/Classical/'+n+'.md')





content = [
]

for n in content:
    py_to_md(py_file_name='Examples_Behaviour/'+n+'.py', md_file_name='docs/Behaviours/'+n+'.md')






content = [
]

for n in content:
    py_to_md(py_file_name='Examples_Paper/'+n+'.py', md_file_name='docs/Experimental/'+n+'.md')

#tutorial manual...




content = [
]

for n in content:
    py_to_md(py_file_name='Examples_UI/'+n+'.py', md_file_name='docs/UI/'+n+'.md')
    
    
'''



