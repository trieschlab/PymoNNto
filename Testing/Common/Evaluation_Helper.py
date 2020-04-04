import numpy as np

def get_oscillation_score_hierarchical(SORN_Global, simulation_steps, evaluation_steps):
    result = 0
    parts = 0

    for mode in ['grammar input', 'free activity without learning', 'free activity with learning']:

        if mode is 'free activity without learning':
            SORN_Global['activator', 0].active = False
            SORN_Global.deactivate_mechanisms('STDP')

        if mode is 'free activity with learning':
            SORN_Global['activator', 0].active = False
            SORN_Global.activate_mechanisms('STDP')

        SORN_Global.simulate_iterations(simulation_steps+evaluation_steps, 100, measure_block_time=True)

        for group in SORN_Global['main_exc_group']:
            target = np.mean((group['IPTI'][0].min_th + group['IPTI'][0].max_th) / 2)
            activity = np.mean(np.array(group['n.output', 0])[-evaluation_steps:], axis=1)
            result += 1 - np.sum(np.abs(activity - target)) / evaluation_steps
            parts += 1

        for group in SORN_Global['main_inh_group']:
            activity = np.mean(np.array(group['n.output', 0])[-evaluation_steps:], axis=1)
            bad_count = (np.sum(activity < 0.0001) + np.sum(activity > 0.5))
            result += 1 - bad_count / evaluation_steps
            parts += 1

    return result/parts

def get_evolution_score_simple(SORN_Global, simulation_steps, evaluation_steps, e_ng):
    SORN_Global.simulate_iterations(simulation_steps, 100, measure_block_time=False)
    exc_avg_tar = np.mean((e_ng['IPTI'][0].min_th + e_ng['IPTI'][0].max_th) / 2)
    exc_avg = np.mean(np.array(e_ng['n.output', 0])[-evaluation_steps:], axis=1)
    exc_score = np.power(np.sum(np.abs(exc_avg - exc_avg_tar)), 2)
    return -exc_score

def get_evolution_score(SORN_Global, simulation_steps, evaluation_steps, inh_target_act, e_ng, i_ng):
    SORN_Global.simulate_iterations(simulation_steps, 100, measure_block_time=False)
    exc_avg_tar = np.mean((e_ng['IPTI'][0].min_th + e_ng['IPTI'][0].max_th) / 2)
    inh_avg_tar = inh_target_act#exc_avg_tar*2#inh_target_act  # 0.017
    exc_avg = np.mean(np.array(e_ng['n.output', 0])[-evaluation_steps:], axis=1)
    inh_avg = np.mean(np.array(i_ng['n.output', 0])[-evaluation_steps:], axis=1)
    exc_score = np.power(np.sum(np.abs(exc_avg - exc_avg_tar)), 2)
    inh_score = np.power(np.sum(np.abs(inh_avg - inh_avg_tar)), 2)

    print(exc_score, inh_score/20)
    score1 = -(exc_score + inh_score/20)

    SORN_Global.deactivate_mechanisms('STDP')

    SORN_Global.simulate_iterations(simulation_steps, 100, measure_block_time=False)
    exc_avg_tar = np.mean((e_ng['IPTI'][0].min_th + e_ng['IPTI'][0].max_th) / 2)
    inh_avg_tar = exc_avg_tar#inh_target_act  # 0.017
    exc_avg = np.mean(np.array(e_ng['n.output', 0])[-evaluation_steps:], axis=1)
    inh_avg = np.mean(np.array(i_ng['n.output', 0])[-evaluation_steps:], axis=1)
    exc_score = np.power(np.sum(np.abs(exc_avg - exc_avg_tar)), 2)
    inh_score = np.power(np.sum(np.abs(inh_avg - inh_avg_tar)), 2)

    score2 = -(exc_score + inh_score)

    return score1+score2