import tools

params = tools.get_params()

size = params['lot']['size']
wait_time_seconds = params['lot']['wait_time_seconds']

cluster_to = params['clusters']['name']

jaime_url = params['jaime']['url']

namespaces = [
    ob
    for ob
    in tools.sh(f'oc get proyects -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
    if not 'openshift-' in ob
]

for np in namespaces:

    print(f"{cluster_to} -> Generando work para {np}")
    tools.new_jaime_work('migrate-bc', 'ocp_migrate', 'execute_buildconfigs', {
        'lot': {
            'size': size,
            'wait_time_seconds': wait_time_seconds
        },
        'clusters': {
            'name': cluster_to,
            'namespace': np
        }
    })

print(f"{cluster_to} -> Proceso terminado")
