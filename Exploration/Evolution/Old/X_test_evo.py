import sys
sys.path.append('../../')
import numpy as np
import time


def run(tag='test', ind=[], thread_index=None):
    #process
    print(type(ind), ind)
    score = np.sum(ind)
    time.sleep(10)
    return score


if __name__ == '__main__':
    import Exploration.Evolution.Old.Distributed_Evolution as DistEvo
    tag, ind, thread = DistEvo.parse_sys()
    score = run(tag, ind, thread)
    DistEvo.save_score(score, tag, ind, thread)
