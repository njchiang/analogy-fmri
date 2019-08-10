import tensorflow as tf
import os
import json
import copy
"""
Designed to work with either Dataset api or feed-dict "standalone".

tf.reset_default_graph()

epochs = 1
batch_size = 32
in_placeholder = tf.placeholder(tf.float32, in_data.shape)
labels_placeholder = tf.placeholder(tf.float32, oh_labels.shape)
dataset = (tf.data.Dataset
           .from_tensor_slices((in_placeholder, labels_placeholder))
           .repeat()
           .shuffle(100)
           .batch(batch_size))

iterator = dataset.make_initializable_iterator()
inputs, targets = iterator.get_next()
iterator_init_op = iterator.initializer

test.build(inputs, targets)


with tf.Session() as sess:
    sess.run(iterator.initializer, 
             feed_dict = {
            in_placeholder: in_data,
            labels_placeholder: oh_labels
        })    
    sess.run(tf.global_variables_initializer())

    for i in range(epochs):
        _, loss_val, out = sess.run([test.optimizer, test.loss, test.out])
"""


# fixed architecture net
class fMRIConvNet(object):
    def __init__(self, params, n_classes, input_size, graph=None, l2=True, name="cnn-model", save_path="./model"):
        self.name = name
        self.model_path = os.path.join(save_path, "model")
        self.summary_path = os.path.join(save_path, "summary")
        self.n_classes = n_classes
        # pad up to make sure everything will be contained
        self.input_size = input_size
        self.l2 = l2
        self.params = copy.deepcopy(params)
        self.is_built = False
        if graph is not None:
            self.graph = graph
        else:
            self.graph = tf.Graph()

        for p in self.params:
            # if p["kernel_size"] is None:
            #     p["kernel_size"] = calculate_fc_kernel(self.input_size, params)
            if "logit" in p["name"] and p["filters"] is None:
                p["filters"] = self.n_classes

    def _parse_param(self, p, inputs):
        # someday this will be awesome
        op = p["name"].split("_")[0]
        with tf.variable_scope(p["name"]):
            if op == "conv":
                return self._add_conv_layer(p, inputs)
            elif op == "maxpool":
                return self._add_maxpool(p, inputs)
            elif op == "logit":
                return self._add_conv_layer(p, inputs)
            elif op == "drop":
                return self._add_dropout(p, inputs)
            elif op == "relu":
                return self._add_relu(p, inputs)
            elif op == "leaky":
                return self._add_leaky_relu(p, inputs)
            elif op == "batchnorm":
                return self._add_batchnorm(p, inputs)

    def _add_dropout(self, layer_params, inputs):
        return tf.layers.dropout(
            inputs=inputs,
            rate=layer_params["rate"],
            name=layer_params["name"]
        )

    def _build_iterators(self):
        with tf.variable_scope("datasets"):
            self.training_batch_size = tf.placeholder(tf.int64, name="training_batch_size")
            self.inference_batch_size = tf.placeholder(tf.int64, name="inference_batch_size")
            input_shape = [None] + list(self.input_size)
            output_shape = [None, self.n_classes]
            self.inputs = tf.placeholder(tf.float32, input_shape, name="inputs")
            self.targets = tf.placeholder(tf.float32, output_shape, name="targets")

            train_ds = (tf.data.Dataset
                        .from_tensor_slices((self.inputs, self.targets))
                        .repeat()
                        .shuffle(50000, reshuffle_each_iteration=True)
                        .batch(self.training_batch_size))
            test_ds = (tf.data.Dataset
                       .from_tensor_slices((self.inputs, self.targets))
                       .repeat()
                       .batch(self.inference_batch_size))
            self.handle = tf.placeholder(tf.string, shape=[], name="string_handle")

            iterator = tf.data.Iterator.from_string_handle(
                string_handle=self.handle,
                output_types=train_ds.output_types,
                output_shapes=train_ds.output_shapes
            )
            self.train_iterator = train_ds.make_initializable_iterator()
            self.test_iterator = test_ds.make_initializable_iterator()

        inputs, targets = iterator.get_next()
        return inputs, targets

    def _standalone_placeholders(self, input_size, n_classes):
        with tf.variable_scope("standalone_inputs"):
            input_shape = tuple([None] + list(input_size))
            self.inputs = tf.placeholder(tf.float32, input_shape, name="inputs")
            self.targets = tf.placeholder(tf.float32, [None, n_classes], name="targets")
        return self.inputs, self.targets

    def _add_relu(self, layer_params, inputs):
        return tf.nn.relu(inputs, name=layer_params["name"])

    def _add_batchnorm(self, layer_params, inputs):
        return tf.layers.batch_normalization(
            inputs, **layer_params
        )

    def _add_leaky_relu(self, layer_params, inputs):
        return tf.nn.leaky_relu(inputs, name=layer_params["name"])

    def _add_conv_layer(self, layer_params, inputs):
        if layer_params["kernel_size"] is None:
            layer_params["kernel_size"] = inputs.get_shape().as_list()[1:4]
        return tf.layers.conv3d(
            inputs=inputs,
            filters=layer_params["filters"],
            kernel_size=layer_params["kernel_size"],
            padding=layer_params["padding"],
            name=layer_params["name"],
            kernel_initializer=tf.glorot_uniform_initializer(),
            activation=None,
            use_bias=layer_params["use_bias"]
        )

    def _add_maxpool(self, layer_params, inputs):
        return tf.layers.max_pooling3d(
            inputs=inputs,
            pool_size=layer_params["pool_size"],
            name=layer_params["name"],
            strides=layer_params["strides"],
            padding=layer_params["padding"]
        )

    def _build_loss(self, logits, targets, **args):
        loss = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits_v2(
                logits=logits,
                labels=targets,
                **args
            )
        )
        return loss

    def _compute_accuracy(self, pred, label, **args):
        correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(label, 1))
        return tf.reduce_mean(tf.cast(correct_prediction, tf.float32), **args)

    def _build_optimizer(self, loss):
        self.learning_rate = tf.placeholder(tf.float32, shape=None, name="learning_rate")
        train_op = tf.train.AdamOptimizer(self.learning_rate)

        grads_and_vars = train_op.compute_gradients(loss)
        optimizer = train_op.apply_gradients(grads_and_vars)
        return optimizer, grads_and_vars

    def _build(self, standalone):
        if self.is_built is False:
            with self.graph.as_default():
                if standalone:
                    inputs, targets = self._standalone_placeholders(self.input_size, self.n_classes)
                else:
                    inputs, targets = self._build_iterators()
                # if train_mode
                # for p in self.params:
                #     self._parse_param(p)
                a = [tf.expand_dims(inputs, -1)]
                for i, layer_params in enumerate(self.params):
                    a.append(self._parse_param(layer_params, a[i]))

                logits = tf.squeeze(a[-1])
                self.out = tf.nn.softmax(logits, name="predictions")
                self.loss = self._build_loss(logits, targets, name="loss")
                self.accuracy = self._compute_accuracy(self.out, targets, name="accuracy")
                if self.l2:
                    self.loss += tf.losses.get_regularization_loss()
                self.optimizer, grads_and_vars = self._build_optimizer(self.loss)

                # tensorboard stuff
                with tf.name_scope("parameters"):
                    histogram_list = [tf.summary.histogram(var.name.replace(":", "_"), var) for var in tf.trainable_variables()]
                self.hist_summaries = tf.summary.merge(histogram_list)

                self.tf_loss_ph = tf.placeholder(tf.float32, shape=None, name="loss_summary")
                self.tf_accuracy_ph = tf.placeholder(tf.float32,shape=None, name='accuracy_summary')

                with tf.name_scope("metrics"):
                    loss_summary = tf.summary.scalar('loss', self.tf_loss_ph)
                    accuracy_summary = tf.summary.scalar('accuracy', self.tf_accuracy_ph)

                with tf.name_scope('gradients'):
                    grad_hist_list = [tf.summary.histogram(
                        v.name.replace(":", "_") + "/gradient", g) for g,v in grads_and_vars]
                    self.gradnorm_summary = tf.summary.merge(grad_hist_list)

                self.metrics = tf.summary.merge([loss_summary, accuracy_summary])

                self.saver = tf.train.Saver()
                self.is_built = True
        else:
            pass

    def build(self, standalone=False, rebuild=False):
        if rebuild is False:
            pass
        self._build(standalone)

    def save(self, sess, **params):
        self.saver.save(sess, os.path.join(self.model_path, self.name), **params)
        with open(os.path.join(self.model_path, "{}.json".format(self.name)), "w") as out:
            json.dump(self.params, out)

    def load(self, sess):
        restore_from = tf.train.latest_checkpoint(self.model_path)
        if restore_from is not None:
            self.saver.restore(sess, restore_from)
        else:
            pass

    def train(self, sess, x, y):
        pass

    def eval(self, sess, x, y):
        feed_dict = {
            self.inputs: x,
            self.targets: y
        }
        return sess.run(self.accuracy, feed_dict=feed_dict)

    def predict(self, sess, x):
        feed_dict = {
            self.inputs: x
        }
        return sess.run(self.out, feed_dict=feed_dict)


