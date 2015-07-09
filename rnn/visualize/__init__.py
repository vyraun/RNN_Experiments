from blocks.model import Model
from blocks.serialization import load_parameter_values

from rnn.visualize.visualize_gates import (
    visualize_gates_soft, visualize_gates_lstm)
from rnn.visualize.visualize_states import visualize_states
from rnn.visualize.visualize_gradients import visualize_gradients


def run_visualizations(cost, updates,
                       train_stream, valid_stream,
                       args,
                       hidden_states=None, gate_values=None):

    # Load the parameters from a dumped model
    assert args.load_path is not None
    model = Model(cost)
    model.set_param_values(load_parameter_values(args.load_path))

    # Run a visualization
    if args.visualize == "gates" and (gate_values is not None):
        if args.rnn_type == "lstm":
            visualize_gates_lstm(gate_values, hidden_states, updates,
                                 train_stream, valid_stream,
                                 args)
        elif args.rnn_type == "soft":
            visualize_gates_soft(gate_values, hidden_states, updates,
                                 train_stream, valid_stream,
                                 args)
        else:
            assert False

    elif args.visualize == "states":
        visualize_states(hidden_states, updates,
                         train_stream, valid_stream,
                         args)

    elif args.visualize == "gradients":
        visualize_gradients(hidden_states, updates,
                            train_stream, valid_stream,
                            args)

    else:
        assert False
