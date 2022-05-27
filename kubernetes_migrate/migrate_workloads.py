import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
cluster_to = params['clusters']['to']['name']


workloads = [
    'deployments',
    'statefulsets',
    'secrets',
    'configmaps',
    'cronjobs',
    'jobs',
    'DaemonSets',
    'HorizontalPodAutoscalers'
]

namespaces = [
    ob
    for ob
    in tools.sh(f'kubectl get namespaces -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
    if not 'kube-' in ob
]

for np in namespaces:

    for ob in workloads:

        print(f"{cluster_to} -> Generando work para {np} {ob}")
        tools.new_jaime_work(f'migrate-{ob}-{np}', 'ocp_migrate', 'migrate_object', {
            'clusters': {
                'from': {
                    'name': cluster_from,
                    'namespace': np,
                    'object': ob,
                    'ignore': [
                        "default-",
                        "builder-",
                        "deployer-"
                    ]
                },
                'to': {
                    'name': cluster_to,
                    'namespace': np
                }
            }
        })


print(f"{cluster_to} -> Proceso terminado")
