import os
import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Turn off TensorFlow warning messages in program output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Load training data set from CSV file
training_data_df = pd.read_csv("sales_data_training.csv", dtype=float)

# Pull out columns for X (data to train with) and Y (value to predict)
X_training = training_data_df.drop('total_earnings', axis=1).values
Y_training = training_data_df[['total_earnings']].values

# Load testing data set from CSV file
test_data_df = pd.read_csv("sales_data_test.csv", dtype=float)

# Pull out columns for X (data to train with) and Y (value to predict)
X_testing = test_data_df.drop('total_earnings', axis=1).values
Y_testing = test_data_df[['total_earnings']].values

# All data needs to be scaled to a small range like 0 to 1 for the neural
# network to work well. Create scalers for the inputs and outputs.
X_scaler = MinMaxScaler(feature_range=(0, 1))
Y_scaler = MinMaxScaler(feature_range=(0, 1))

# Scale both the training inputs and outputs
X_scaled_training = X_scaler.fit_transform(X_training)
Y_scaled_training = Y_scaler.fit_transform(Y_training)

# It's very important that the training and test data are scaled with the same scaler.
X_scaled_testing = X_scaler.transform(X_testing)
Y_scaled_testing = Y_scaler.transform(Y_testing)

# Define model parameters
LEARNING_RATE = 0.001
TRAINING_EPOCHS = 100
DISPLAY_STEP = 5

# Define how many inputs and outputs are in our neural network
NUMBER_OF_INPUTS = 9
NUMBER_OF_OUTPUTS = 1

# Define how many neurons we want in each layer of our neural network
LAYER_1_NODES = 50
LAYER_2_NODES = 100
LAYER_3_NODES = 50

# Section One: Define the layers of the neural network itself


# Input Layer
with tf.variable_scope('input'):
    X = tf.placeholder(tf.float32, shape=(None, NUMBER_OF_INPUTS))

# Layer 1
with tf.variable_scope('layer_1'):
    weights = tf.get_variable("weights1", shape=[NUMBER_OF_INPUTS, LAYER_1_NODES], initializer=tf.contrib.layers.xavier_initializer())
    biases = tf.get_variable(name="biases1", shape=[LAYER_1_NODES], initializer=tf.zeros_initializer())
    layer_1_output = tf.nn.relu(tf.matmul(X, weights) + biases)

# Layer 2
with tf.variable_scope('layer_2'):
    weights = tf.get_variable("weights2", shape=[LAYER_1_NODES, LAYER_2_NODES], initializer=tf.contrib.layers.xavier_initializer())
    biases = tf.get_variable(name="biases2", shape=[LAYER_2_NODES], initializer=tf.zeros_initializer())
    layer_2_output = tf.nn.relu(tf.matmul(layer_1_output, weights) + biases)

# Layer 3
with tf.variable_scope('layer_3'):
    weights = tf.get_variable("weights3", shape=[LAYER_2_NODES, LAYER_3_NODES], initializer=tf.contrib.layers.xavier_initializer())
    biases = tf.get_variable(name="biases3", shape=[LAYER_3_NODES], initializer=tf.zeros_initializer())
    layer_3_output = tf.nn.relu(tf.matmul(layer_2_output, weights) + biases)

# Output Layer
with tf.variable_scope('output'):
    weights = tf.get_variable("weights4", shape=[LAYER_3_NODES, NUMBER_OF_OUTPUTS], initializer=tf.contrib.layers.xavier_initializer())
    biases = tf.get_variable(name="biases4", shape=[NUMBER_OF_OUTPUTS], initializer=tf.zeros_initializer())
    prediction = tf.matmul(layer_3_output, weights) + biases

# Section Two: Define the cost function of the neural network that will be optimized during training

with tf.variable_scope('cost'):
    Y = tf.placeholder(tf.float32, shape=(None, 1))
    cost = tf.reduce_mean(tf.squared_difference(prediction, Y))

# Section Three: Define the optimizer function that will be run to optimize the neural network

with tf.variable_scope('train'):
    optimizer = tf.train.AdamOptimizer(LEARNING_RATE).minimize(cost)

# Create a summary operation to log the progress of the network
with tf.variable_scope('logging'):
    tf.summary.scalar('current_cost', cost)
    summary = tf.summary.merge_all()

with tf.variable_scope('summary'):  # Create a summary operation to log the progress of the network
    tf.summary.scalar('current_cost', cost)
    summary = tf.summary.merge_all()

saver = tf.train.Saver()

# Initialize a session so that we can run TensorFlow operations
with tf.Session() as session:

    # Run the global variable initializer to initialize all variables and layers of the neural network
    session.run(tf.global_variables_initializer())

    # Create log file writers to record training progress.
    # We'll store training and testing log data separately.
    training_writer = tf.summary.FileWriter('./logs/training', session.graph)
    testing_writer = tf.summary.FileWriter('./logs/testing', session.graph)

    # Run the optimizer over and over to train the network.
    # One epoch is one full run through the training data set.
    for epoch in range(TRAINING_EPOCHS):

        # Feed in the training data and do one step of neural network training
        session.run(optimizer, feed_dict={X: X_scaled_training, Y: Y_scaled_training})

        # Every few training steps, log our progress
        if epoch % DISPLAY_STEP == 0:
            # Get the current accuracy scores by running the "cost" operation on the training and test data sets
            training_cost, training_summary = session.run([cost, summary], feed_dict={X: X_scaled_training, Y:Y_scaled_training})
            testing_cost, testing_summary = session.run([cost, summary], feed_dict={X: X_scaled_testing, Y:Y_scaled_testing})

            # Write the current training status to the log files (Which we can view with TensorBoard)
            training_writer.add_summary(training_summary, epoch)
            testing_writer.add_summary(testing_summary, epoch)

            # Print the current training status to the screen
            print("Epoch: {} - Training Cost: {}  Testing Cost: {}".format(epoch, training_cost, testing_cost))

    # Training is now complete!

    # Get the final accuracy scores by running the "cost" operation on the training and test data sets
    final_training_cost = session.run(cost, feed_dict={X: X_scaled_training, Y: Y_scaled_training})
    final_testing_cost = session.run(cost, feed_dict={X: X_scaled_testing, Y: Y_scaled_testing})

    print("Final Training cost: {}".format(final_training_cost))
    print("Final Testing cost: {}".format(final_testing_cost))

    # Now that the neural network is trained, let's use it to make predictions for our test data.
    # Pass in the X testing data and run the "prediciton" operation
    Y_predicted_scaled = session.run(prediction, feed_dict={X: X_scaled_testing})

    # Unscale the data back to it's original units (dollars)
    Y_predicted = Y_scaler.inverse_transform(Y_predicted_scaled)

    real_earnings = test_data_df['total_earnings'].values[0]
    predicted_earnings = Y_predicted[0][0]

    print("The actual earnings of Game #1 were ${}".format(real_earnings))
    print("Our neural network predicted earnings of ${}".format(predicted_earnings))

    model_builder = tf.saved_model.builder.SavedModelBuilder("exported_model")

    inputs = {
        'input': tf.saved_model.utils.build_tensor_info(X)
        }
    outputs = {
        'earnings': tf.saved_model.utils.build_tensor_info(prediction)
        }

    signature_def = tf.saved_model.signature_def_utils.build_signature_def(
        inputs=inputs,
        outputs=outputs,
        method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME
    )

    model_builder.add_meta_graph_and_variables(
        session,
        tags=[tf.saved_model.tag_constants.SERVING],
        signature_def_map={
            tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: signature_def
        }
    )

    model_builder.save()
