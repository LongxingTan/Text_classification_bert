import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score,roc_auc_score,precision_score,recall_score


def metric_fn():
    pass


def create_eval(labels,predictions):
    accuracy=tf.metrics.accuracy(labels,predictions)
    eval_metrics = {'acc': accuracy}
    return eval_metrics



def create_eval_binary(labels,predictions):
    labels=tf.cast(labels,tf.int16)
    predictions=tf.cast(predictions,tf.int16)

    accuracy = tf.metrics.accuracy(labels=labels,
                                   predictions=predictions,
                                   name='acc_op')
    micro_f1=tf.contrib.metrics.f1_score(labels=labels,
                                         predictions=predictions,
                                         name='f1')
    auc=tf.metrics.auc(labels=labels,
                       predictions=predictions,
                       name='auc')

    tf.summary.scalar('accuracy', accuracy[1])
    eval_metrics = {'accuracy': accuracy,'f1':micro_f1,'auc':auc}

    return eval_metrics

def create_eval_sk(labels,predictions):
    accuracy = accuracy_score(labels,predictions)
    pre=precision_score(labels,predictions,average='micro')
    rec=recall_score(labels,predictions,average='micro')
    micro_f1=f1_score(labels,predictions,average='micro')
    auc=roc_auc_score(labels,predictions,average='micro')
    eval_metrics = {'accuracy': accuracy,'precision':pre,'recall':rec,'f1':micro_f1,'auc':auc}
    return eval_metrics