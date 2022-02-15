import requests
import tools

params = tools.get_params()

server_from = params['servers']['from']['name']
namespaces = params['servers']['from']['namespaces']

server_to = params['servers']['to']['name']

jaime_url = params['jaime']['url']


def post_work(yaml_params: str):
    requests.post(
        url=f'{jaime_url}/api/v1/works',
        data=yaml_params,
        headers={'Content-Type': 'text/plain; charset=utf-8'}
    )


def generate_yaml_params(server_from, server_to, np, ob) -> str:
    return f"""
name: migrate-{np}-{ob}
module: _migrate_object
agent:
    type: OPENSHIFT
servers:
    from:
        name: {server_from}
        namespace: {np}
        object: {ob}        
        ignore: 
            - "system:*"
    to:
        name: {server_to}
        namespace: {np}
"""


for np in namespaces:

    # SERVICEACCOUNTS
    print(f"{server_to} -> Generando work para {np} sa")
    post_work(generate_yaml_params(server_from, server_to, np, 'sa'))

    # ROLES
    print(f"{server_to} -> Generando work para {np} roles")
    post_work(generate_yaml_params(server_from, server_to, np, 'roles'))

    # ROLEBINDINGS
    print(f"{server_to} -> Generando work para {np} rolebindings")
    post_work(generate_yaml_params(server_from, server_to, np, 'rolebindings'))


print(f"{server_to} -> Proceso terminado")
