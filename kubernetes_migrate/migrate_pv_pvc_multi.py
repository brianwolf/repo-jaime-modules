import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']

cluster_to = params['clusters']['to']['name']
storage_class = params['clusters']['to']['storage_class']

namespaces = [
    ob
    for ob
    in tools.sh(f'kubectl get namespaces -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
    if not 'kube-' in ob
]

for np in namespaces:

    print(f"{cluster_to} -> Generando work para {np}")
    tools.new_jaime_work(f'migrate-pv-pvc-{np}', 'ocp_migrate', 'migrate_pv_pvc', {
        'clusters': {
            'from': {
                'name': cluster_from,
                'namespace': np,
            },
            'to': {
                'name': cluster_to,
                'storage_class': storage_class
            }
        }
    })


print(f"{cluster_to} -> Proceso terminado")
