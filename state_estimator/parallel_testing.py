import multiprocessing
import numpy as np
import pandas as pd
import copy
import random
from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import time

def run_simulation(lmb_value, names_ataque, Meas_seguridad, names, Nodes, Lines, Cons, n_simus):
    """
    Run a single simulation and return the results.
    """
    Res_ide = []
    
    for _ in range(n_simus):
        Meas = copy.deepcopy(Meas_seguridad)
        
        random_entries = random.sample(names_ataque, 2)
        
        for ataque in random_entries:
            if ataque.startswith('P'):
                num = names.index(ataque)
                magnitud = 0.8 + np.random.rand()*0.4
            if ataque.startswith('Q'):
                num = names.index(ataque)
                magnitud = 0.8 + np.random.rand()*0.4
            if ataque.startswith('U'):
                num = names.index(ataque)
                magnitud = 0.98 + np.random.rand()*0.04
            Meas[num]['value'] = magnitud * Meas[num]['value']
        
        # Build the grid and run state estimation (WLS with normalized residuals)
        net = lib.grid(Nodes, Lines, Meas, Cons)
        Results_WLS = net.state_estimation(tol=1e-4, niter=50, Huber=False, lmb=None, rn=True)
        
        # Max normalized residual before discarding any measure -> adjust lambda
        lmb_value = 2  # You can replace this with Results_WLS['max_res']*0.5 if needed
        
        # Restore all measures and solve using Huber
        net = lib.grid(Nodes, Lines, Meas, Cons)
        Results_Huber = net.state_estimation(tol=1e-4, niter=50, Huber=True, lmb=lmb_value, rn=False)
        
        # Process results and try to identify the cyber attack
        df_evol_Q = pd.DataFrame(
            list(np.array([list(Results_Huber['Q'][index]) for index in range(len(Results_Huber['Q']))]).T), 
            index=names
        )
        df_evol_Q = df_evol_Q.iloc[:, 3:]
        
        # Identifying the attack
        n_cols = 3
        result_rows = []
        if df_evol_Q.shape[1] >= n_cols:
            final_value_condition = df_evol_Q.iloc[:, -1] < 1
            
            def is_decreasing(row):
                last_four_values = row.iloc[-n_cols:]
                return all(last_four_values.diff().dropna() < 0)
            
            decreasing_condition = df_evol_Q[final_value_condition].apply(is_decreasing, axis=1)
            result_rows = df_evol_Q[final_value_condition].index[decreasing_condition].tolist()
        
        print(f'Ataque sobre: {ataque}, identificación: {result_rows}\n')
        
        # Results interpretation
        if ataque in result_rows:
            if len(result_rows) == 1:
                Res_ide.append(0)  # Correct detection
            else:
                Res_ide.append(1)  # Detection with incorrect additional results
        else:
            if len(result_rows) == 0:
                Res_ide.append(3)  # No detection
            else:
                Res_ide.append(2)  # Incorrect detection
                
    return Res_ide



def parallelize_simulations(Nodes, Lines, Meas_seguridad, names, Cons, lmb_range, names_P, names_Q, names_U, n_simus, num_lmb):
    """
    Parallelize the simulations using multiprocessing.
    """
    results = []
    # Prepare the list of tasks to be parallelized (each task is a combination of lmb_value and names_ataque)
    tasks = []
    for lmb_value in lmb_range:
        for names_ataque in [names_P, names_Q, names_U]:
            tasks.append((lmb_value, names_ataque, Meas_seguridad, names, Nodes, Lines, Cons, n_simus))
    
    # Parallelize using multiprocessing Pool
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.starmap(run_simulation, tasks)
    
    return results

num_lmb = 10 #100
n_simus = 1 #1000

# Example of how to use this
if __name__ == "__main__":
    
    t0 = time.time()

    # Load your system topology and measurements (you would adapt these paths as needed)
    path = ['../data/pv_2_3_180_', '../data_Cati/pv_2_3_180_']
    case = ['090neg', '090pos', '100pos']
    
    for c in case:
        for hour in ['08', '09', '10', '11', '12', '13', '14']:
            for minute in ['00']:
                sheet_name = hour + '_' + minute + '_pf_' + c
                extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                                 path[1] + hour + '_' + minute + '_pf_' + c + '/']

                Nodes, Lines = system_topology('../data/pv_2_3.json')
                Meas, mjson, stdjson = system_measurements(extended_path, 'measurements.json', 'std_2.json', Nodes, Lines, add_noise=True)
                Cons = system_constraints(Nodes)
                Meas_seguridad = copy.deepcopy(Meas)

                # Prepare names list and measure groups
                names = [m['type'] + '_' + Nodes[m['node']]['name'] if m['line'] is None else m['type'] + '_' + Lines[np.abs(m['line'])]['From'] + '_' + Lines[np.abs(m['line'])]['To'] for m in Meas]
                for item in zip(Meas, names):
                    item[0]['name'] = item[1]
                
                names_P = [name for name in names if name.startswith('P_LV')]
                names_Q = [name for name in names if name.startswith('Q_LV')]
                names_U = [name for name in names if name.startswith('U_LV')]

                lmb_range = np.linspace(0.01, 50, num_lmb)

                # Run parallelized simulations
                results = parallelize_simulations(Nodes, Lines, Meas_seguridad, names, Cons, lmb_range, names_P, names_Q, names_U, n_simus, num_lmb)

                # Process or save results as needed
                print(results)

    t1 = time.time()
    print(t1-t0)
