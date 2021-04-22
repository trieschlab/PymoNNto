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


#Connectivity and Partitioning

One helpful function when designing bigger networks is the partitioning system.
When the implemented model is based on vector and matrix operations, the NeuronGroups can be divided into SubNeuronGroups with a mask.
Such a SubNeuronGroup allows partial access to variables of the original NeuronGroup.
To avoid giant connection matrices, the partitioning system can automatically divide the NeuronGroup into subgroups that are connected by many small SynapseGroups.
With this, we can conveniently combine fast processing with small computational overhead and avoid the quadratic growth of synaptic weight matrices for increasing numbers of neurons.

The following code creates a SynapseGroup with a specific connectivity, which is then partitioned into many smaller sub synapse groups.
"(s_id!=d_id)" means that the source id and the target id of the neurons have to be different to form a synapse.
"in_box(10)" means, that the neurons have a receptive field of 10 neurons in each direction, so the resulting patch has the size 11x11.
Because s_id, and the output of in_box() are boolean vectors, we cannot use "and" or "or", so we just multiply them to replace an "and" operator.
The connectivity attribute only changes the enabeled attribute of the synapse matrix.

If the partitioning attribute is True, the single Synapse group is splitted into many smaller SynapseGroups based on the enabeled matrix.
Only the SubSynapseGroups are added to MyNetwork and sg.dst as well as sg.src point to SubNeuronGroups is sg is one of the SubSynapseGroups.


```python
SynapseGroup(net=MyNetwork, src=sourceNG, dst=destinationNG, tag='GLU', connectivity='(s_id!=d_id)*in_box(10)', partition=True)
```

#Evolution

The Evolution package can be used to automatically optimize network parameters.
We are currently extending the evolution package to run on distributed devices and to be controlled with a separate user interface.

In this example we see a simple evolution setup

```python
#folder/slave.py
from PymoNNto.Exploration.Evolution.Interface_Functions import *

print('genes: ', get_genome())
print('gene a: ', get_gene('a', None))
print('gene b: ', gene('b', 1))

score = get_gene('a', 0) + get_gene('b', 0)

set_score(score)
```

```python
#master.py
from PymoNNto.Exploration.Evolution.Evolution import *

if __name__ == '__main__':
    genome = {'a': 1, 'b': 2}

    evo = Evolution(name='my_test_evo',
                    slave_file='folder/slave.py',
                    individual_count=10,
                    mutation=0.04,
                    death_rate=0.5,
                    constraints=['b>=a+1', 'a <= 1', 'b>1.5'],
                    inactive_genome_info={'info': 'my_info'},
                    ui=False,
                    start_genomes=[genome],
                    devices={'single_thread': 0,
                             'multi_thread': 5,
                             'ssh user@host': 0,
                             'ssh user2@host2': 0
                             }
                    )

    evo.start()
```