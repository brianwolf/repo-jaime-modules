import logging
import os

import tools
import yaml

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
namespaces = params['clusters']['from']['namespaces']

cluster_to = params['clusters']['to']['name']
pvc_storage_class = params['clusters']['to']['storage_class']


###########################################
# PVs
###########################################

# file BK
bk_file_path = f'/data/migrate_pv_{cluster_from}_to_{cluster_to}.txt'

if not os.path.exists(bk_file_path):
    tools.sh(f'> {bk_file_path}')

with open(bk_file_path, 'r') as f:
    migrated_bk = f.read().split('\n')


# login cluster from
oc_from = tools.get_client(cluster_from)
login_success = oc_from.login()
if not login_success:
    print(f'Error en login {cluster_from}')
    exit(1)


# obteniendo yamls
print(f"{cluster_from} -> Obtieniendo todos los pv")
pvs = [
    ob
    for ob
    in oc_from.exec(f'get pv -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
]

tools.sh('mkdir -p yamls/pvs')

pvs_to_migrate = []
for pv in pvs:

    if pv in migrated_bk:
        continue

    print(f'{cluster_from} -> Obteniendo pv {pv}')
    oc_from.exec(f'get pv {pv} -o yaml > yamls/pvs/{pv}.yaml')
    pvs_to_migrate.append(pv)

print(f'{cluster_from} -> por migrar {len(pvs_to_migrate)} pvs')


# login cluster to
oc_to = tools.get_client(cluster_to)
login_success = oc_to.login()
if not login_success:
    print(f'Error en login {cluster_to}')
    exit(1)


# migrar yamls
yamls_errors = []
for pv in pvs:
    try:
        with open(f'yamls/pvs/{pv}.yaml', 'r') as file:
            dic_yaml = yaml.load(file, Loader=yaml.FullLoader)
        
        dic_yaml['metadata'].pop('managedFields', None)
        dic_yaml['metadata'].pop('creationTimestamp', None)
        dic_yaml['metadata'].pop('namespace', None)
        dic_yaml['metadata'].pop('resourceVersion', None)
        dic_yaml['metadata'].pop('selfLink', None)
        dic_yaml['metadata'].pop('uid', None)
        dic_yaml.pop('status', None)
        
        dic_yaml['metadata'].pop('finalizers', None)
        dic_yaml['spec']['claimRef'].pop('uid', None)
        dic_yaml['spec']['claimRef'].pop('resourceVersion', None)

        yaml_to_apply = yaml.dump(dic_yaml, default_flow_style=False)
        with open(f'yamls/pvs/{pv}.yaml', 'w') as f:
            f.write(yaml_to_apply)

        oc_to.exec(f'apply -f yamls/pvs/{pv}.yaml')
        print(f'{cluster_to} -> Migrado {pv}')
        tools.sh(f"""echo "{pv}" >> {bk_file_path}""")

    except Exception as e:
        yamls_errors.append(pv)
        print(f'{cluster_to} -> ERROR al migrar {pv}')
        print(e.with_traceback())

if yamls_errors:
    print(f'{cluster_to} -> Yamls con ERRORES al migrar:')
    for y_error in yamls_errors:
        print(f'{cluster_to} -> {y_error}')

tools.sh(f'rm -fr {bk_file_path}')


###########################################
# PVCs
###########################################

for np in namespaces:

    # file BK
    bk_file_path = f'/data/migrate_pvc_{cluster_from}_{np}_to_{cluster_to}_{np}.txt'

    if not os.path.exists(bk_file_path):
        tools.sh(f'> {bk_file_path}')

    with open(bk_file_path, 'r') as f:
        migrated_bk = f.read().split('\n')


    # login cluster from
    oc_from = tools.get_client(cluster_from)
    login_success = oc_from.login()
    if not login_success:
        print(f'Error en login {cluster_from}')
        exit(1)


    # obteniendo yamls
    print(f"{cluster_from} -> Obtieniendo todos los pvc")
    pvcs = [
        ob
        for ob
        in oc_from.exec(f'get pvc -n {np} -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
    ]

    tools.sh('mkdir -p yamls/pvcs')

    pvcs_to_migrate = []
    for pvc in pvcs:

        if pvc in migrated_bk:
            continue

        print(f'{cluster_from} -> Obteniendo pvc {pvc}')
        oc_from.exec(f'get pvc {pvc} -n {np} -o yaml > yamls/pvcs/{pvc}.yaml')
        pvcs_to_migrate.append(pvc)

    print(f'{cluster_from} -> por migrar {len(pvcs_to_migrate)} pvcs')


    # login cluster to
    oc_to = tools.get_client(cluster_to)
    login_success = oc_to.login()
    if not login_success:
        print(f'Error en login {cluster_to}')
        exit(1)


    # migrar yamls
    yamls_errors = []
    for pvc in pvcs:
        try:
            with open(f'yamls/pvcs/{pvc}.yaml', 'r') as file:
                dic_yaml = yaml.load(file, Loader=yaml.FullLoader)
            
            dic_yaml['metadata'].pop('managedFields', None)
            dic_yaml['metadata'].pop('creationTimestamp', None)
            dic_yaml['metadata'].pop('namespace', None)
            dic_yaml['metadata'].pop('resourceVersion', None)
            dic_yaml['metadata'].pop('selfLink', None)
            dic_yaml['metadata'].pop('uid', None)
            dic_yaml.pop('status', None)
            
            dic_yaml['metadata'].pop('finalizers', None)
            dic_yaml['metadata'].pop('annotations', None)

            dic_yaml['spec']['storageClassName'] = pvc_storage_class

            yaml_to_apply = yaml.dump(dic_yaml, default_flow_style=False)
            with open(f'yamls/pvcs/{pvc}.yaml', 'w') as f:
                f.write(yaml_to_apply)

            oc_to.exec(f'apply -n {np} -f yamls/pvcs/{pvc}.yaml')
            print(f'{cluster_to} -> Migrado {pvc}')
            tools.sh(f"""echo "{pvc}" >> {bk_file_path}""")

        except Exception as e:
            yamls_errors.append(pvc)
            print(f'{cluster_to} -> ERROR al migrar {pvc}')
            print(e.with_traceback())

    if yamls_errors:
        logging.error(f'{cluster_to} -> Yamls con ERRORES al migrar:')
        for y_error in yamls_errors:
            print(f'{cluster_to} -> {y_error}')

    tools.sh(f'rm -fr {bk_file_path}')