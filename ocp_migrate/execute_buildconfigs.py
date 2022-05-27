import os
import re
import time

import tools

###########################################
# VARS
###########################################

params = tools.get_params()

size = params['lot']['size']
wait_time_seconds = params['lot']['wait_time_seconds']

cluster = params['clusters']['name']
namespace = params['clusters']['namespace']
only = params['clusters'].get('only', [])
ignore = params['clusters'].get('ignore', [])


###########################################
# SCRIPT
###########################################

# file BK
bk_file_path = f'/data/execute_bc_{cluster}_{namespace}.txt'

if not os.path.exists(bk_file_path):
    tools.sh(f'> {bk_file_path}')

with open(bk_file_path, 'r') as f:
    migrated_bk = f.read().split('\n')


# login 
login_success = tools.login_openshift(cluster)
if not login_success:
    print(f'Error en login {cluster}')
    exit(0)


# obteniendo BCs
print(f"{cluster} -> Obtieniendo todos los buildconfigs")

bc_list = [
    bc
    for bc
    in tools.sh(f'oc get bc -n {namespace} -o custom-columns=NAME:.metadata.name').split('\n')[1:]
]

bc_list_to_execute = []
for bc in bc_list:

    if only:
        match_all_regex = len(
            [regex for regex in only if re.match(regex, bc)]) == len(only)
        if not match_all_regex:
            continue

    if ignore:
        match_any_regex = any(
            True for regex in ignore if re.match(regex, bc))
        if match_any_regex:
            continue

    if bc in migrated_bk:
        continue

    bc_list_to_execute.append(bc)

print(f"{cluster} -> bc para ejecutar: {len(bc_list_to_execute)}")


# ejecucion
print(f"{cluster} -> Comenzando ejecucion")

lot_exec_count = 0
for bc in bc_list_to_execute:

    lot_exec_count += 1

    print(f"{cluster} -> Ejecutando bc: {bc}")
    tools.sh(f'oc start-build {bc} -n {namespace}')
    tools.sh(f"""echo "{bc}" >> {bk_file_path}""")

    if lot_exec_count == size:
        lot_exec_count = 0
        time.sleep(float(wait_time_seconds))


print(f"{cluster} -> Proceso terminado")
tools.sh(f'rm -fr {bk_file_path}')