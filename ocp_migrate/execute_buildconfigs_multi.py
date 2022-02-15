import requests
import tools

params = tools.get_params()

size = params['lot']['size']
wait_time_seconds = params['lot']['wait_time_seconds']

server_to = params['servers']['name']
namespaces = params['servers']['namespaces']

jaime_url = params['jaime']['url']


def post_work(yaml_params: str):
    requests.post(
        url=f'{jaime_url}/api/v1/works',
        data=yaml_params,
        headers={'Content-Type': 'text/plain; charset=utf-8'}
    )


def generate_yaml_params(server_to, np) -> str:
    return f"""
name: execute_buildconfigs-{np}
module: _execute_buildconfigs
agent:
    type: OPENSHIFT
lot:
    size: {size}
    wait_time_seconds: {wait_time_seconds}
servers:
    name: {server_to}
    namespace: {np}
"""


for np in namespaces:

    print(f"{server_to} -> Generando work para {np}")
    post_work(generate_yaml_params(server_to, np))


print(f"{server_to} -> Proceso terminado")