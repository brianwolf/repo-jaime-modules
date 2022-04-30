import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
cluster_to = params['clusters']['to']['name']


# CLUSTERROLES
print(f"{cluster_to} -> Generando work para clusterroles")
tools.new_jaime_work(f'migrate-clusterroles', 'ocp_migrate', 'migrate_object', {
    'clusters': {
        'from': {
            'name': cluster_from,
            'namespace': 'openshift',
            'object': 'clusterroles',
            'ignore': [
                "system:*",
                "openshift-*",
                "registry-*",
                "admin",
                "cluster-admin"
            ]
        },
        'to': {
            'name': cluster_to,
            'namespace': 'openshift'
        }
    }
})

# CLUSTERROLEBINDINGS
print(f"{cluster_to} -> Generando work para clusterrolebindings")
tools.new_jaime_work(f'migrate-clusterrolebindings', 'ocp_migrate', 'migrate_object', {
    'clusters': {
        'from': {
            'name': cluster_from,
            'namespace': 'openshift',
            'object': 'clusterrolebindings',
            'ignore': [
                "system:*",
                "openshift-*",
                "registry-*",
                "admin",
                "cluster-admin"
            ]
        },
        'to': {
            'name': cluster_to,
            'namespace': 'openshift'
        }
    }
})

print(f"{cluster_to} -> Proceso terminado")
