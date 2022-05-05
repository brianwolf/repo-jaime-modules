import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
host_replace_from = params['clusters']['from']['host_replace_from']

cluster_to = params['clusters']['to']['name']
host_replace_to = params['clusters']['from']['host_replace_to']

namespaces = [
    ob
    for ob
    in tools.sh(f'oc get projects -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
    if not 'openshift-' in ob
]

for np in namespaces:

    # ROUTES
    print(f"{cluster_to} -> Generando work para routes")
    tools.new_jaime_work(f'migrate-routes-{np}', 'ocp_migrate', 'migrate_routes', {
        'clusters': {
            'from': {
                'name': cluster_from,
                'namespace': np,
                'host_replace_from': host_replace_from
            },
            'to': {
                'name': cluster_to,
                'namespace': np,
                'host_replace_to': host_replace_to
            }
        }
    })

    # SERVICES
    print(f"{cluster_to} -> Generando work para services")
    tools.new_jaime_work(f'migrate-routes-{np}', 'ocp_migrate', 'migrate_services', {
        'clusters': {
            'from': {
                'name': cluster_from,
                'namespace': np
            },
            'to': {
                'name': cluster_to,
                'namespace': np
            }
        }
    })

print(f"{cluster_to} -> Proceso terminado")
