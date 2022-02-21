import requests
import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
namespaces = params['clusters']['from']['namespaces']

cluster_to = params['clusters']['to']['name']

jaime_url = params['jaime']['url']

networking = [
    'services',
    'routes'
]


def post_work(yaml_params: str):
    requests.post(
        url=f'{jaime_url}/api/v1/works',
        data=yaml_params,
        headers={'Content-Type': 'text/plain; charset=utf-8'}
    )


def generate_yaml_params(cluster_from, cluster_to, np, ob) -> str:
    return f"""
name: migrate-{np}-{ob}
module: 
    name: migrate_object
    repo: ocp_migrate
agent:
    type: OPENSHIFT
clusters:
    from:
        name: {cluster_from}
        namespace: {np}
        object: {ob}
    to:
        name: {cluster_to}
        namespace: {np}
"""


for np in namespaces:

    for ob in networking:

        print(f"{cluster_to} -> Generando work para {np} {ob}")
        post_work(generate_yaml_params(cluster_from, cluster_to, np, ob))


print(f"{cluster_to} -> Proceso terminado")
