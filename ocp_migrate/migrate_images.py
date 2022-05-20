import os
import re

import tools
import yaml

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
namespace = params['clusters']['from']['namespace']
url_public_registry = params['clusters']['from']['url_public_registry']

cluster_to = params['clusters']['to']['name']


login_success = tools.login_openshift(cluster_from)
if not login_success:
    print(f'Error en login {cluster_from}')
    exit(1)


# buscando cosas en el cluster from
print(f"{cluster_from} -> Obtieniendo secrets")
secrets = [
    ob
    for ob
    in tools.sh(f'oc get secret -n {namespace} -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
]

print(f"{cluster_from} -> Obtieniendo imagestream")
images = [
    ob
    for ob
    in tools.sh(f'oc get is -n {namespace} -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
]


# buscando secret
for s in secrets:

    p = re.compile('default-dockercfg-*')
    m = p.match(s)
    if m:
        secret = s
        print('Encontrado secret -> ', s)

if not secret:
    print(f'Error en encontrar un secret con la forma -> default-dockercfg-*')
    exit(1)

tools.sh('mkdir -p yamls/secrets')
tools.sh(
    f'oc get secret {secret} -n {namespace} -o yaml > yamls/secrets/{secret}.yaml')


# logueando cluster to
login_success = tools.login_openshift(cluster_to)
if not login_success:
    print(f'Error en login {cluster_to}')
    exit(1)


# generando secret en cluster to
tools.sh(f'oc new-project {namespace}')

with open(f'yamls/secrets/{secret}.yaml', 'w') as file:
    dic_yaml = yaml.load(file, Loader=yaml.FullLoader)

    dic_yaml['metadata'].pop('managedFields', None)
    dic_yaml['metadata'].pop('creationTimestamp', None)
    dic_yaml['metadata'].pop('namespace', None)
    dic_yaml['metadata'].pop('resourceVersion', None)
    dic_yaml['metadata'].pop('selfLink', None)
    dic_yaml['metadata'].pop('uid', None)
    dic_yaml.pop('status', None)

    dic_yaml['metadata'].pop('ownerReferences', None)

    yaml_to_apply = yaml.dump(dic_yaml, default_flow_style=False)
    file.write(yaml_to_apply)

tools.sh(f'oc apply -n {namespace} -f yamls/secrets/{secret}.yaml')
print(f'{cluster_to} -> Creado secret -> {secret}')


# file BK
bk_file_path = f'/data/migrate_images_{cluster_from}_{namespace}_to_{cluster_to}_{namespace}.txt'

if not os.path.exists(bk_file_path):
    tools.sh(f'> {bk_file_path}')

with open(bk_file_path, 'r') as f:
    migrated_bk = f.read().split('\n')


# migrando imagenes
for image in images:

    if image in migrated_bk:
        continue

    tools.sh(
        f"oc import-image {image} --from={url_public_registry}/{namespace}/{image} --all --confirm --insecure=true -n {namespace}")
    tools.sh(f"""echo "{image}" >> {bk_file_path}""")


tools.sh(
    f"oc delete secret {secret} -n {namespace}")

print(f'{cluster_to} -> proceso terminado')
tools.sh(f'rm -fr {bk_file_path}')
