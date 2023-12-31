import time
import math
import sys
import pickle
import glob
import os
import tensorflow as tf
from seq2seq_model import Seq2SeqModel
from corpora_tools import *

path_l1_dict = "/tmp/l1_dict.p"
path_l2_dict = "/tmp/l2_dict.p"
model_dir = "/tmp/translate"
model_checkpoints = model_dir + "/translate.ckpt"

def build_dataset(use_stored_dictionary=False):
    sen_l1, sen_l2 = retrieve_corpora()
    clean_sen_l1 = [clean_sentence(s) for s in sen_l1]
    clean_sen_l2 = [clean_sentence(s) for s in sen_l2]
    filt_clean_sen_l1, filt_clean_sen_l2 = filter_sentence_length(clean_sen_l1, clean_sen_l2)
    if not use_stored_dictionary:
        dict_l1 = create_indexed_dictionary(filt_clean_sen_l1, dict_size=15000, storage_path=path_l1_dict)
        dict_l2 = create_indexed_dictionary(filt_clean_sen_l2, dict_size=10000, storage_path=path_l2_dict)
    else:
        dict_l1 = pickle.load(open(path_l1_dict, "rb"))
        dict_l2 = pickle.load(open(path_l2_dict, "rb"))

    dict_l1_length = len(dict_l1)
    dict_l2_length = len(dict_l2)

    idx_sentences_l1 = sentences_to_indexes(filt_clean_sen_l1, dict_l1)
    idx_sentences_l2 = sentences_to_indexes(filt_clean_sen_l2, dict_l2)

    max_length_l1 = extract_max_length(idx_sentences_l1)
    max_length_l2 = extract_max_length(idx_sentences_l2)

    data_set = prepare_sentences(idx_sentences_l1, idx_sentences_l2, max_length_l1, max_length_l2)
    
    return (filt_clean_sen_l1, filt_clean_sen_l2), data_set, (max_length_l1, max_length_l2), (dict_l1_length, dict_l2_length)

def cleanup_checkpoints(model_dir, model_checkpoints):
    for f in glob.glob(model_checkpoints + "*"):
        os.remove(f)
    try:
        os.mkdir(model_dir)
    except FileExistsError:
        pass

def train():
    with tf.Session() as sess:
        model = get_seq2seq_model(sess, False, dict_lengths, max_sentence_lengths, model_dir)
        step_time, loss = 0.0, 0.0
        current_step = 0
        bucket = 0
        steps_per_checkpoint = 100
        max_steps = 20000
        
        while current_step < max_steps:
            start_time = time.time()
            encoder_inputs, decoder_inputs, target_weights = model.get_batch([data_set], bucket)
            _, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs, target_weights, bucket, False)
            step_time += (time.time() - start_time) / steps_per_checkpoint
            loss += step_loss / steps_per_checkpoint
            current_step += 1
            
            if current_step % steps_per_checkpoint == 0:
                perplexity = math.exp(float(loss)) if loss < 300 else float("inf")
                print("global step {} learning rate {} step-time {} perplexity {}".format(
                    model.global_step.eval(), model.learning_rate.eval(), step_time, perplexity))
                sess.run(model.learning_rate_decay_op)
                model.saver.save(sess, model_checkpoints, global_step=model.global_step)
                step_time, loss = 0.0, 0.0
                
                encoder_inputs, decoder_inputs, target_weights = model.get_batch([data_set], bucket)
                _, eval_loss, _ = model.step(sess, encoder_inputs, decoder_inputs, target_weights, bucket, True)
                eval_ppx = math.exp(float(eval_loss)) if eval_loss < 300 else float("inf")
                print(" eval: perplexity {}".format(eval_ppx))
                sys.stdout.flush()

if __name__ == "__main__":
    _, data_set, max_sentence_lengths, dict_lengths = build_dataset(False)
    cleanup_checkpoints(model_dir, model_checkpoints)
    train()
