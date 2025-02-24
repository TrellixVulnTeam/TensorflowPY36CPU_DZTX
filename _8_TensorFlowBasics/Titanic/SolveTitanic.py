import tensorflow as tf
import numpy as np
import os
from tensorflow.python.framework import ops

ops.reset_default_graph()

weight = tf.Variable(initial_value=tf.zeros([5,1]), name="Weight")
bias = tf.Variable(initial_value=0., name="Bias")
# victor
# 16/12/2017
# Created @ 2017-12-16 00:57
def combine_inputs(X):
    return tf.matmul(X, weight ) + bias


def inputs():
    assenger_id, survived, pclass, name, sex, age, sibsp, parch, ticket, fare, cabin, embarked = \
        read_csv(100, "train.csv", [[0.0], [0.0], [0], [""], [""], [0.0], [0.0], [0.0], [""], [0.0], [""], [""]])

    # convert categorical data
    is_first_class = tf.to_float(tf.equal(pclass, [1]))
    is_second_class = tf.to_float(tf.equal(pclass, [2]))
    is_third_class = tf.to_float(tf.equal(pclass, [3]))

    gender = tf.to_float(tf.equal(sex, ["female"]))

    # Finally we pack all the features in a single matrix;
    # We then transpose to have a matrix with one example per row and one feature per column.
    features = tf.transpose(tf.stack([is_first_class, is_second_class, is_third_class, gender, age]))
    survived = tf.reshape(survived, [100, 1])

    return features, survived


def inference(X):
    return tf.sigmoid(combine_inputs(X))


def loss(X, Y):
    return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=combine_inputs(X),labels= Y))


def evaluate(sess, X, Y):
    predicted = tf.cast(inference(X) > 0.5, tf.float32)

    print(sess.run(tf.reduce_mean(tf.cast(tf.equal(predicted, Y), tf.float32))))

def train(total_loss):

    learning_rate = 0.01
    return tf.train.GradientDescentOptimizer(learning_rate).minimize(total_loss)

model_saver = tf.train.Saver()


def read_csv(batch_size, file_name, record_defaults):
    filename_queue = tf.train.string_input_producer([os.path.join(os.getcwd(), file_name)])

    reader = tf.TextLineReader(skip_header_lines=1)
    key, value = reader.read(filename_queue)

    # decode_csv will convert a Tensor from type string (the text line) in
    # a tuple of tensor columns with the specified defaults, which also
    # sets the data type for each column
    decoded = tf.decode_csv(value, record_defaults=record_defaults)

    # batch actually reads the file and loads "batch_size" rows in a single tensor
    return tf.train.shuffle_batch(decoded,
                                  batch_size=batch_size,
                                  capacity=batch_size * 50,
                                  min_after_dequeue=batch_size)

with tf.Session() as sess:
    tf.global_variables_initializer().run()

    X, Y = inputs()

    total_loss = loss(X, Y)

    train_ops = train(total_loss)

    coord = tf.train.Coordinator()

    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    train_steps = 1000

    for steps in range(train_steps):
        sess.run([train_ops])

        if steps % 10 == 0:
            print("Loss ", sess.run([total_loss]))

    evaluate(sess,X, Y)

    import time
    time.sleep(5)

    coord.request_stop()
    coord.join(threads)

    model_saver.save(sess, 'my_model', global_step=train_steps)
    sess.close()


