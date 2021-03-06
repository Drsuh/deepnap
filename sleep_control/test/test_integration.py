import sys
sys.path.append('../../')  # add project home into search path

import time
import pandas as pd

from sleep_control.integration import Emulation
from sleep_control.traffic_emulator import TrafficEmulator
from sleep_control.traffic_server import TrafficServer
from sleep_control.controller import QController, DummyController
from rl.qtable import QAgent
from rl.qnn_theano import QAgentNN

pd.set_option('mode.chained_assignment', None)

# Setting up data
print "Reading data..."
session_df =pd.read_csv(
    filepath_or_buffer='../../data/trace_dh3.dat',
    parse_dates=['startTime_datetime', 'endTime_datetime']
)

print "Setting up Emulation environment..."
# Setting up Emulation
te = TrafficEmulator(session_df=session_df, time_step=pd.Timedelta(minutes=30), verbose=1)
ts = TrafficServer(verbose=2)
# ACTIONS = [(s, c) for s in [True, False] for c in ['serve_all', 'queue_all', 'random_serve_and_queue']]
actions = [(True, None), (False, 'serve_all')]
# agent = QAgent(ACTIONS=ACTIONS, alpha=0.5, gamma=0.5, explore_strategy='epsilon', epsilon=0.1)
agent = QAgentNN(dim_state=(1, 1, 3), range_state=((((0, 10), (0, 10), (0, 10),),),),
                 learning_rate=0.01, reward_scaling=10, batch_size=100, freeze_period=50, memory_size=200, num_buffer=2,
                 actions=actions, alpha=0.5, gamma=0.5, explore_strategy='epsilon', epsilon=0.1,
                 verbose=2
                 )
c = QController(agent=agent)
emu = Emulation(te=te, ts=ts, c=c)

print "Emulation starting"
print
# run...
while emu.te.epoch is not None:
    # log time
    print "Epoch {}, ".format(emu.epoch),
    left = emu.te.head_datetime + emu.te.epoch*emu.te.time_step
    right = left + emu.te.time_step
    print "{} - {}".format(left.strftime("%Y-%m-%d %H:%M:%S"), right.strftime("%Y-%m-%d %H:%M:%S"))
    emu.step()
    print

