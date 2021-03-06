import tensorflow as tf
from models._embedding import EmbeddingLayer
from models._normalization import BatchNormalization,LayerNormalization


class CLSTM(object):
    def __init__(self, training,params):
        self.training = training
        self.params=params
        self.embedding_layer = EmbeddingLayer(vocab_size=params['vocab_size'],
                                               embed_size=params['embedding_size'],
                                               embedding_type=params['embedding_type'],
                                               params=params)
        self.bn_layer = BatchNormalization()

    def build(self, inputs):
        with tf.name_scope("embed"):
            embedded_outputs=self.embedding_layer(inputs)

        if self.training:
            embedded_outputs=tf.nn.dropout(embedded_outputs,self.params['embedding_dropout_keep'])

        conv_output = []
        for i, kernel_size in enumerate(self.params['kernel_sizes']):
            with tf.name_scope("conv_%s" % kernel_size):
                conv1=tf.layers.conv1d(inputs=embedded_outputs,
                                       filters=self.params['filters'],
                                       kernel_size=[kernel_size],
                                       strides=1,
                                       padding='same',
                                       activation=tf.nn.relu)
                conv_output.append(conv1)
        cnn_output_concat=tf.concat(conv_output,2)

        with tf.name_scope('bi_lstm'):
            cell_fw = tf.nn.rnn_cell.LSTMCell(self.params['rnn_hidden_size'])
            cell_bw = tf.nn.rnn_cell.LSTMCell(self.params['rnn_hidden_size'])
            if self.training:
                cell_fw = tf.nn.rnn_cell.DropoutWrapper(cell_fw, output_keep_prob=self.params['rnn_dropout_keep'])
                cell_bw = tf.nn.rnn_cell.DropoutWrapper(cell_bw, output_keep_prob=self.params['rnn_dropout_keep'])
            all_outputs, _ = tf.nn.bidirectional_dynamic_rnn(cell_fw=cell_fw, cell_bw=cell_bw,
                                                             inputs=cnn_output_concat,
                                                             sequence_length=None, dtype=tf.float32)
            all_outputs = tf.concat(all_outputs, 2)

        if self.params['use_pooling']:
            rnn_outputs=self.build_pool(all_outputs)
        else:
            rnn_outputs = tf.reduce_max(all_outputs, axis=1)

        if self.training:
            rnn_outputs=tf.nn.dropout(rnn_outputs,self.params['dropout_keep'])
        with tf.name_scope('output'):
            logits = tf.layers.dense(rnn_outputs,units=self.params['n_class'], name="logits")
        return logits

    def __call__(self,inputs,targets=None):
        logits=self.build(inputs)
        return logits

    def build_pool(self,inputs):
        with tf.name_scope('pool'):
            # rnn_outputs = tf.reduce_max(all_outputs, axis=1)
            max_pool = tf.layers.max_pooling1d(inputs=inputs,
                                               pool_size=self.params['seq_length'],
                                               strides=1)  # => batch_size * 1 * filters
            avg_pool = tf.layers.average_pooling1d(inputs=inputs,
                                                   pool_size=self.params['seq_length'],
                                                   strides=1)
            pool_outputs = tf.squeeze(tf.concat([max_pool, avg_pool], axis=-1), axis=1)
            pool_outputs = self.bn_layer(pool_outputs)
        return pool_outputs
