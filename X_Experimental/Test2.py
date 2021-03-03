import tensorflow as tf
import numpy as np

v = tf.Variable(np.ones(100), dtype=tf.int32)
mask = np.zeros(100)
mask[0] = 1
mask[10] = 1
v2 = tf.constant(mask)
v3 = tf.constant([1,2,3], dtype=tf.int32)#, dtype='int32'

add = tf.add(v, v)

#print(add)

print(tf.boolean_mask(add, v2, axis=0))

#tf.compat.v1.scatter_nd_update(add, v3, tf.Variable([10,10,10], dtype=tf.int32))

#print(add)

