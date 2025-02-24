import tensorflow as tf
import numpy as np

sess = tf.Session()
tensor_3d = np.array([[[ 0,  1,  2],[ 3,  4,  5],[ 6,  7,  8]],
                      [[ 9, 10, 11],[12, 13, 14],[15, 16, 17]],
                      [[18, 19, 20],[21, 22, 23],[24, 25, 26]]])

tensor_3d = tf.convert_to_tensor(value=tensor_3d,dtype=tf.float64)

print("My new tensor 3D \n" +str( sess.run(tensor_3d)))