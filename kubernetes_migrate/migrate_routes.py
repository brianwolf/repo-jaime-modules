import os
import re

import yaml
import tools

###########################################
# VARS
###########################################

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
namespace = params['clusters']['from']['namespace']
only_from = params['clusters']['from'].get('only', [])
ignore_from = params['clusters']['from'].get('ignore', [])
host_replace_from = params['clusters']['from']['host_replace_from']

cluster_to = params['clusters']['to']['name']
host_replace_to = params['clusters']['to']['host_replace_to']


###########################################
# SCRIPT
###########################################

# file BK
bk_file_path = f'/data/migrate_routes_{cluster_from}_{namespace}_to_{cluster_to}_{namespace}.txt'

if not os.path.exists(bk_file_path):
    tools.sh(f'> {bk_file_path}')

with open(bk_file_path, 'r') as f:
    migrated_bk = f.read().split('\n')


# login cluster from
login_success = tools.login_kubernetes(cluster_from)
if not login_success:
    print(f'Error en login {cluster_from}')
    exit(1)


# obteniendo yamls
print(f"{cluster_from} -> Obtieniendo todos los objetos")
objects = [
    ob
    for ob
    in tools.sh(f'kubectl get routes -n {namespace} -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
]

tools.sh('mkdir yamls/')

objects_to_migrate = []
for ob in objects:

    if only_from:
        match_all_regex = len(
            [regex for regex in only_from if re.match(regex, ob)]) == len(only_from)
        if not match_all_regex:
            continue

    if ignore_from:
        match_any_regex = any(
            True for regex in ignore_from if re.match(regex, ob))
        if match_any_regex:
            continue

    if ob in migrated_bk:
        continue

    print(f'{cluster_from} -> Obteniendo {ob}')
    tools.sh(
        f'kubectl get routes {ob} -n {namespace} -o yaml > yamls/{ob}.yaml')
    objects_to_migrate.append(ob)

print(f'{cluster_from} -> por migrar {len(objects_to_migrate)} routes')


# login cluster to
login_success = tools.login_kubernetes(cluster_to)
if not login_success:
    print(f'Error en login {cluster_to}')
    exit(1)


# migrar yamls
tools.sh(f'kubectl new-project {namespace}')

yamls_errors = []
for ob in objects_to_migrate:
    try:
        with open(f'yamls/{ob}.yaml', 'w') as file:
            dic_yaml = yaml.load(file, Loader=yaml.FullLoader)

            dic_yaml['metadata'].pop('managedFields', None)
            dic_yaml['metadata'].pop('creationTimestamp', None)
            dic_yaml['metadata'].pop('namespace', None)
            dic_yaml['metadata'].pop('resourceVersion', None)
            dic_yaml['metadata'].pop('selfLink', None)
            dic_yaml['metadata'].pop('uid', None)
            dic_yaml.pop('status', None)

            dic_yaml['spec']['host'] = dic_yaml['spec']['host'].replace(
                host_replace_from, host_replace_to)

            f.write(yaml.dump(dic_yaml, default_flow_style=False))

        tools.sh(f'kubectl apply -n {namespace} -f yamls/{ob}.yaml')
        print(f'{cluster_to} -> Migrado {ob}')
        tools.sh(f"""echo "{ob}" >> {bk_file_path}""")

    except Exception as e:
        yamls_errors.append(ob)
        print(f'{cluster_to} -> ERROR al migrar {ob}')
        print(e.with_traceback())

if yamls_errors:
    print(f'{cluster_to} -> Yamls con errores al migrar:')
    for y_error in yamls_errors:
        print(f'{cluster_to} -> {y_error}')


print(f'{cluster_to} -> proceso terminado')
tools.sh(f'rm -fr {bk_file_path}')
