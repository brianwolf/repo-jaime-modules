from typing import Dict, List
import tools

params = tools.get_params()

cluster_from = params['cluster_name']

csv_file_path = '/data/report.csv'

row_items = [
    # WORKLOADS
    'deployments',
    'deploymentconfigs',
    'statefulsets',
    'secrets',
    'configmaps',
    'cronjobs',
    'jobs',
    'daemonSets',
    'horizontalPodAutoscalers',
    # NETWORKING
    'services',
    'routes',
    # STORAGE
    'pv',
    'pvc',
    # BUILDS
    'buildconfigs',
    'is',
    # USERS
    'users',
    'groups',
    'sa',
    'roles',
    'rolebinding',
]


def get_count(object: str, project: str) -> int:
    return len(oc_from.exec(f'get {object} -n {project} -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:])


oc_from = tools.get_client(cluster_from)
login_success = oc_from.login()
if not login_success:
    print(f'Error en login {cluster_from}')
    exit(1)


projects = [
    project
    for project in oc_from.exec(f'get projects -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
    if 'openshift-' not in project
]


list_rows = []

print('Generando encabezados')
row = 'projects;'
for object in row_items:
    row += f'{object};'

list_rows.append(row)


print('Obteniendo datos')
for project in projects:

    row = f'{project};'
    for object in row_items:
        print(f'Obteniendo datos de {object} para el proyecto {project}')
        row += f'{get_count(object, project)};'

    list_rows.append(row)


print(f'Generando archivo CSV en {csv_file_path}')
for row in list_rows:
    tools.sh(f'echo "{row}" >> {csv_file_path}')

print(f"{cluster_from} -> Proceso terminado OK")
