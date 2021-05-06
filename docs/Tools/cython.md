#Cython Modules

For the behaviour modules it can make sense to speed up the computations. 
Whether it brings additional performance is heavily dependent on the code of this module.
NumPy already uses C so the increases should be smaller than computations which use many pure Python loops. 
But even code that relies on NumPy operations can achieve speed increases if its done right, by adding types, memoryviews, \textit{cython.boundscheck(False)} or \textit{cython.wraparound(False)} decorators. 
There are many tutorials on how to improve NumPy code with cython so we will not go in to detail here. 
The simplest way to use cython is to perform the following six steps:



1. Write behaviour module `MyBehaviour.py`.
2. Add decorators and types.
3. Save file as `MyBehaviour.pyx` and remove `MyBehaviour.py` file
4. Install cython with `pip install Cython` and maybe some C compiler
5. Move to folder and execute `cython -3 MyBehaviour.pyx` which creates `MyBehaviour.c`
6. Import the pyx and c file with `import pyximport; pyximport.install(); import MyBehaviour`



With this simple steps all behaviour modules or only some slow ones can be sped up while the rest of the code stays unaffected. 
This is useful, because the rest of the code does not have to be compiled on every single run, so the execution of PymoNNto stays very fast and simple. 
Most of the steps are derived from the cython readthedocs page where they are explained in more detail: 
https://cython.readthedocs.io/en/latest/src/tutorial/cython_tutorial.html
