from SORNSim.NetworkCore.Behaviour import *
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf


class TensorflowBehaviour(Behaviour):

    def set_variables(self, neurons):
        if not hasattr(neurons, 'tf'):
            neurons.tf = tf
        super().set_variables(neurons)
