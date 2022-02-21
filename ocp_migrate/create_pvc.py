import logging
import os

import tools
import yaml

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
namespace_from = params['clusters']['from']['namespace']

cluster_to = params['clusters']['to']['name']
namespace_to = params['clusters']['to']['namespace']

pvc_storage_class = params['pvc']['storage_class']


# PVs
# ------------------------

# GET
oc_from = tools.get_client(cluster_from)
login_success = oc_from.login()
if not login_success:
    print(f'Error en login {cluster_from}')
    exit(0)


print(f"{cluster_from} -> Obtieniendo todos los pvs")
pvc_to_migrate = [
    ob
    for ob
    in oc_from.exec(f'get pv -n {namespace_from} -o custom-columns=NAME:.metadata.name').split('\n')[1:]
]

tools.sh('mkdir yamls/')

for ob in pvc_to_migrate:

    content = oc_from.exec(f'get pv {ob} -n {namespace_from} -o yaml')
    if not pvc_storage_class in content:
        continue

    print(f'{cluster_from} -> Obteniendo {ob}')

    with open(f'yamls/{ob}.yaml', 'w') as f:
        f.write(content)

# POST
oc_to = tools.get_oc(cluster_to)
oc_to.login()

oc_to.exec(f'new-project {namespace_to}')

yamls_to_migrate = []
for _, _, file_name in os.walk('yamls/'):
    yamls_to_migrate.extend(file_name)
print(f'{cluster_to} -> Por migrar {len(yamls_to_migrate)} pvs')

for yaml_to_migrate in yamls_to_migrate:
    try:
        with open(f'yamls/{yaml_to_migrate}', 'r') as file:
            dic_yaml = yaml.load(file, Loader=yaml.FullLoader)

        dic_yaml['metadata'].pop('creationTimestamp', None)
        dic_yaml['metadata'].pop('namespace', None)
        dic_yaml['metadata'].pop('resourceVersion', None)
        dic_yaml['metadata'].pop('selfLink', None)
        dic_yaml['metadata'].pop('uid', None)
        dic_yaml['metadata'].pop('managedFields', None)
        dic_yaml.pop('status', None)

        dic_yaml['spec']['claimRef'].pop('uid', None)
        dic_yaml['spec']['claimRef'].pop('apiVersion', None)
        dic_yaml['spec']['claimRef'].pop('resourceVersion', None)
        dic_yaml['spec']['claimRef']['namespace'] = namespace_to
        dic_yaml['spec'].pop('csi', None)

        yaml_to_apply = yaml.dump(dic_yaml, default_flow_style=False)
        with open(f'yamls/{yaml_to_migrate}', 'w') as f:
            f.write(yaml_to_apply)

        oc_to.exec(f'apply -n {namespace_to} -f yamls/{yaml_to_migrate}')
        print(f'{cluster_to} -> Migrado {yaml_to_migrate}')

    except Exception as e:
        logging.exception(e)
        print(e.args)

# PVCs
# ------------------------

# GET
oc_from = tools.get_oc(cluster_from)
oc_from.login()

print(f"{cluster_from} -> Obtieniendo todos los pvcs")
pvc_to_migrate = [
    ob
    for ob
    in oc_from.exec(f'get pvc -n {namespace_from} -o custom-columns=NAME:.metadata.name').split('\n')[1:-1]
]

tools.sh('mkdir yamls/')

for ob in pvc_to_migrate:

    content = oc_from.exec(f'get pvc {ob} -n {namespace_from} -o yaml')
    if not pvc_storage_class in content:
        continue

    print(f'{cluster_from} -> Obteniendo {ob}')

    with open(f'yamls/{ob}.yaml', 'w') as f:
        f.write(content)

# POST
oc_to = tools.get_oc(cluster_to)
oc_to.login()

yamls_to_migrate = []
for _, _, file_name in os.walk('yamls/'):
    yamls_to_migrate.extend(file_name)
print(f'{cluster_to} -> Por migrar {len(yamls_to_migrate)} pvcs')

for yaml_to_migrate in yamls_to_migrate:
    try:
        with open(f'yamls/{yaml_to_migrate}', 'r') as file:
            dic_yaml = yaml.load(file, Loader=yaml.FullLoader)

        dic_yaml['metadata'].pop('creationTimestamp', None)
        dic_yaml['metadata'].pop('namespace', None)
        dic_yaml['metadata'].pop('resourceVersion', None)
        dic_yaml['metadata'].pop('selfLink', None)
        dic_yaml['metadata'].pop('uid', None)
        dic_yaml['metadata'].pop('managedFields', None)
        dic_yaml.pop('status', None)

        yaml_to_apply = yaml.dump(dic_yaml, default_flow_style=False)
        with open(f'yamls/{yaml_to_migrate}', 'w') as f:
            f.write(yaml_to_apply)

        oc_to.exec(f'apply -n {namespace_to} -f yamls/{yaml_to_migrate}')
        print(f'{cluster_to} -> Migrado {yaml_to_migrate}')

    except Exception as e:
        logging.exception(e)
        print(e.args)
