#Storage Manager

To store recording data, parameters, results and variables, a Storage-Manager is included in PymoNNto.
It searches for a ``Data'' folder inside of the project directory and can create a directory with a custom name for a group of simulation runs.
At every run, it creates a separate sub-folder to save and load vectors, matrices, images, and parameters.
Furthermore, the Storage-Manager allows to sort, compare, and analyse multiple runs with respect to different parameters of interest.

The code below creates a storage manager object with a given name. When there ist a "Data" folder in the Project it which creates the following folder structure 
Project/Data/StorageManager/MyName/MyName1234/ where 1234 is a unique random number for the current run. With random_nr=False it will enumerate the subfolders, which, however can lead to problems when we do multithreading and multiple threads want wo create the same folder at the same time.

```python
from PymoNNto import *

sm = StorageManager('MyName', random_nr=True)

sm.save_param_dict({'a':1,'b':True,'c':[1,2,3]})# saves dict to ini file
sm.save_param(key, value, section='Parameters') # saves key value pair to ini file
sm.load_param(key, section='Parameters', default=None) #loads params from ini file

sm.save_recorder(tag, recorder) #saves recorder

sm.save_np(key, obj) #saves numpy object
sm.load_np(key) #loads numpy object

sm.save_obj(key, obj) #saves any python object
sm.load_obj(key) #loads python object
sm.has_obj(key) #checks whether object has been saved already

sm.save_frame(image, key) #saves image and increases frame counter (key1.png, key2.png, ...)
sm.render_video(key, delete_images) # renders video with ffmpeg from frames (key1.png, key2.png, ...)

sm.copy_project_files() #=> backup.zip

```

#Storage Manager Group
As we have seen, the Storage manager creates the following folder structure Project/Data/StorageManager/MyName/MyName1234/.

When we want to extract data from multiple runs (MyName1, MyName2, MyName3,...), we can use the StorageManagerGroup.
It loads all subfolders located in Project/Data/StorageManager/MyName/ and allows you to extract all values of a given parameter from all the different runs, for example.
Alternatively you can also use it to cenveniently iterate over all storage manager instances within the main folder.


```python
smg = StorageManagerGroup('MyName')

for sm in smg.StorageManagerList:
    print(sm.load_param('param_name'))

smg.sort_by('score') #sorts the smg.StorageManagerList list by the parameter "score" inside of the inividual ini files

smg['score'] #scores sorted because of sort_by call
smg['number_of_neurons>1000'] #=> number_of_neurons_list with values above 1000, sorted by score because of previous sort_by call

scores=smg.get_param_list('score', remove_None=False) => score_list #all (not finished) runs without score value have a "None" in the result list, which can be removed automatically. (sorted/sort_by)

param_lists = smg.get_multi_param_list(['score','number_of_neurons','spikes_per_second'], remove_None=False)
#=> [score_list, n_o_n_list, s_p_s_list] all sorted by score because of previous sort_by call

smg.get_np_list(np_name, remove_None=False) #list of saved numpy objects across runs
smg.get_obj_list(obj_name, remove_None=False) #list of saved python objects across runs

n_o_n=param_lists[1]#number of neurons list
unique_score_list, average_nummber_of_neuron_list_per_score = smg.remove_duplicates_get_eval(scores, n_o_n, evalstr='np.average(a)') 
#Lets imagine we have a parameter list with duplicates (runs with same score for example) which you can plot on an x axis and a list with corresponding values (number of neurons) for the y axis.
#In this case can use the remove_duplicates_get_eval function to combine all corresponding values with the same score.
#In this example we combine them with an average function, but we can also use np.std(a) for the standard deviation or other functions f(a).
#The function outputs two list with the same length with the unique x values(scores) and the corresponding y values(average number of neurons), which can then be used for plotting.
```