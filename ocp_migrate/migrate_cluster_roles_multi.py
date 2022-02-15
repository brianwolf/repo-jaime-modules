import requests
import tools

params = tools.get_params()

server_from = params['servers']['from']['name']

server_to = params['servers']['to']['name']

jaime_url = params['jaime']['url']


def post_work(yaml_params: str):
    requests.post(
        url=f'{jaime_url}/api/v1/works',
        data=yaml_params,
        headers={'Content-Type': 'text/plain; charset=utf-8'}
    )


def generate_yaml_params(server_from, server_to, ob) -> str:
    return f"""
name: migrate-{ob}
module: _migrate_object
agent:
    type: OPENSHIFT
servers:
    from:
        name: {server_from}
        namespace: openshift
        object: {ob}        
        ignore: 
            - "system:*"
    to:
        name: {server_to}
        namespace: openshift
"""


# CLUSTERROLES
print(f"{server_to} -> Generando work para clusterroles")
post_work(generate_yaml_params(server_from, server_to, 'clusterroles'))

# CLUSTERROLEBINDINGS
print(f"{server_to} -> Generando work para clusterrolebindings")
post_work(generate_yaml_params(server_from, server_to, 'clusterrolebindings'))


print(f"{server_to} -> Proceso terminado")
