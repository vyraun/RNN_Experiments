import logging

import numpy as np

import theano

from blocks.graph import ComputationGraph
from blocks.extensions import SimpleExtension

import matplotlib
import matplotlib.pyplot as plt
# Force matplotlib to not use any Xwindows backend.
# matplotlib.use('Agg')

from rnn.datasets.dataset import get_character

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


class VisualizeGateSoft(SimpleExtension):

    def __init__(self, gate_values, updates, dataset, ploting_path=None,
                 **kwargs):
        kwargs.setdefault("after_batch", 1)
        self.text_length = 75
        self.dataset = dataset
        super(VisualizeGateSoft, self).__init__(**kwargs)

        cg = ComputationGraph(gate_values)
        assert(len(cg.inputs) == 1)
        assert(cg.inputs[0].name == "features")

        state_vars = [theano.shared(
            v[0:1, :].zeros_like().eval(), v.name + '-gen')
            for v, _ in updates]
        givens = [(v, x) for (v, _), x in zip(updates, state_vars)]
        f_updates = [(x, upd) for x, (_, upd) in zip(state_vars, updates)]
        self.generate = theano.function(inputs=cg.inputs, outputs=gate_values,
                                        givens=givens, updates=f_updates)

    def do(self, *args):
        init_ = next(self.main_loop.epoch_iterator)["features"][
            0: self.text_length, 0:1]
        # time x batch
        whole_sentence_code = init_
        vocab = get_character(self.dataset)
        # whole_sentence
        whole_sentence = ''
        for char in vocab[whole_sentence_code[:, 0]]:
            whole_sentence += str(char)

        last_output = self.generate(init_)
        layers = len(last_output)
        time = last_output[0].shape[0]
        for i in range(layers):
            plt.subplot(layers, 1, i + 1)
            plt.plot(np.arange(time), last_output[i][:, 0, 0])
            plt.xticks(range(self.text_length), tuple(init_[:, 0]))
            plt.grid(True)
            plt.title("gate of layer " + str(i))
        plt.show()


class VisualizeGateLSTM(SimpleExtension):

    def __init__(self, gate_values, updates, dataset, ploting_path=None,
                 **kwargs):
        kwargs.setdefault("after_batch", 1)
        self.text_length = 75
        self.dataset = dataset
        super(VisualizeGateLSTM, self).__init__(**kwargs)

        in_gates = gate_values["in_gates"]
        out_gates = gate_values["out_gates"]
        forget_gates = gate_values["forget_gates"]
        cg_in = ComputationGraph(in_gates)
        cg_out = ComputationGraph(out_gates)
        cg_forget = ComputationGraph(forget_gates)
        for cg in [cg_in, cg_forget, cg_out]:
            assert(len(cg.inputs) == 1)
            assert(cg.inputs[0].name == "features")

        state_vars = [theano.shared(
            v[0:1, :].zeros_like().eval(), v.name + '-gen')
            for v, _ in updates]
        givens = [(v, x) for (v, _), x in zip(updates, state_vars)]
        f_updates = [(x, upd) for x, (_, upd) in zip(state_vars, updates)]

        self.generate_in = theano.function(inputs=cg_in.inputs,
                                           outputs=in_gates,
                                           givens=givens,
                                           updates=f_updates)
        self.generate_out = theano.function(inputs=cg_out.inputs,
                                            outputs=out_gates,
                                            givens=givens,
                                            updates=f_updates)
        self.generate_forget = theano.function(inputs=cg_forget.inputs,
                                               outputs=forget_gates,
                                               givens=givens,
                                               updates=f_updates)

    def do(self, *args):
        init_ = next(self.main_loop.epoch_iterator)["features"][
            0: self.text_length, 0:1]

        # time x batch
        whole_sentence_code = init_
        vocab = get_character(self.dataset)
        # whole_sentence
        whole_sentence = ''
        for char in vocab[whole_sentence_code[:, 0]]:
            whole_sentence += str(char)

        last_output_in = self.generate_in(init_)
        last_output_out = self.generate_out(init_)
        last_output_forget = self.generate_forget(init_)
        layers = len(last_output_in)

        time = last_output_in[0].shape[0]

        for i in range(layers):

            plt.subplot(3, layers, i * 3 + 1)
            for j in range(last_output_in[i].shape[2]):
                plt.plot(np.arange(time), last_output_in[i][:, 0, j])
            plt.xticks(range(self.text_length), tuple(init_[:, 0]))
            plt.grid(True)
            plt.title("in_gate of layer " + str(i))

            plt.subplot(3, layers, i * 3 + 2)
            for j in range(last_output_in[i].shape[2]):
                plt.plot(np.arange(time), last_output_out[i][:, 0, j])
            plt.xticks(range(self.text_length), tuple(init_[:, 0]))
            plt.grid(True)
            plt.title("out_gate of layer " + str(i))

            plt.subplot(3, layers, i * 3 + 3)
            for j in range(last_output_in[i].shape[2]):
                plt.plot(np.arange(time), last_output_forget[i][:, 0, j])
            plt.xticks(range(self.text_length), tuple(init_[:, 0]))
            plt.grid(True)
            plt.title("forget_gate of layer " + str(i))

        plt.show()