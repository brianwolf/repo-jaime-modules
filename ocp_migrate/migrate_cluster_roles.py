import requests
import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']

cluster_to = params['clusters']['to']['name']

jaime_url = params['jaime']['url']


def post_work(yaml_params: str):
    requests.post(
        url=f'{jaime_url}/api/v1/works',
        data=yaml_params,
        headers={'Content-Type': 'text/plain; charset=utf-8'}
    )


def generate_yaml_params(cluster_from, cluster_to, ob) -> str:
    return f"""
name: migrate-{ob}
module: 
    name: migrate_object
    repo: ocp_migrate
agent:
    type: OPENSHIFT
clusters:
    from:
        name: {cluster_from}
        namespace: openshift
        object: {ob}        
        ignore: 
            - "system:*"
            - "openshift-*"
            - "registry-*"
    to:
        name: {cluster_to}
        namespace: openshift
"""


# CLUSTERROLES
print(f"{cluster_to} -> Generando work para clusterroles")
post_work(generate_yaml_params(cluster_from, cluster_to, 'clusterroles'))

# CLUSTERROLEBINDINGS
print(f"{cluster_to} -> Generando work para clusterrolebindings")
post_work(generate_yaml_params(cluster_from, cluster_to, 'clusterrolebindings'))


print(f"{cluster_to} -> Proceso terminado")
