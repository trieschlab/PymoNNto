from SORNSim.Exploration.Network_UI.Sequence_Activation_Tabs.sidebar_grammar_module import *
from SORNSim.Exploration.Network_UI.Sequence_Activation_Tabs.sidebar_image_module import *
from SORNSim.Exploration.Network_UI.Sequence_Activation_Tabs.reconstruction_tab import *
from SORNSim.Exploration.Network_UI.Sequence_Activation_Tabs.sidebar_music_module import *
from SORNSim.Exploration.Network_UI.Sequence_Activation_Tabs.sidebar_drumbeat_module import *
from SORNSim.Exploration.Network_UI.Sequence_Activation_Tabs.sun_gravity_plot_tab import *
from SORNSim.Exploration.Network_UI.Sequence_Activation_Tabs.character_activation_tab import *

def get_my_default_UI_modules():
    return [
        # chain_tab(),
        sun_gravity_plot_tab(),
        sidebar_image_module(),
        sidebar_grammar_module(),
        sidebar_music_module(),
        sidebar_drumbeat_module(),
        reconstruction_tab(),
        character_activation_tab()
        ]