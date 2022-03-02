import requests
import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
namespaces = params['clusters']['from']['namespaces']
url_public_registry = params['clusters']['from']['url_public_registry']

cluster_to = params['clusters']['to']['name']

jaime_url = params['jaime']['url']


def post_work(yaml_params: str):
    requests.post(
        url=f'{jaime_url}/api/v1/works',
        data=yaml_params,
        headers={'Content-Type': 'text/plain; charset=utf-8'}
    )


def generate_yaml_params(cluster_from, cluster_to, np, url_public_registry) -> str:
    return f"""
name: migrate-{np}-images
module: 
    name: migrate_images
    repo: ocp_migrate
agent:
    type: OPENSHIFT
clusters:
    from:
        name: {cluster_from}
        namespace: {np}
        url_public_registry: {url_public_registry}
    to:
        name: {cluster_to}
"""


for np in namespaces:

    print(f"{cluster_to} -> Generando work para {np}")
    post_work(generate_yaml_params(cluster_from,
              cluster_to, np, url_public_registry))


print(f"{cluster_to} -> Proceso terminado")
