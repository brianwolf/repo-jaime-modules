import requests
import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
cluster_to = params['clusters']['to']['name']


user_managment = [
    'sa',
    'roles',
    'rolebindings',
    'users',
    'groups'
]

namespaces = [
    ob
    for ob
    in tools.sh(f'oc get projects -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
    if not 'openshift-' in ob
]

for np in namespaces:

    for ob in user_managment:

        print(f"{cluster_to} -> Generando work para {np} {ob}")
        tools.new_jaime_work(f'migrate-{ob}-{np}', 'ocp_migrate', 'migrate_object', {
            'clusters': {
                'from': {
                    'name': cluster_from,
                    'namespace': np,
                    'object': ob,
                    'ignore': [
                        "system:*",
                        "default",
                        "builder",
                        "deployer"
                    ]
                },
                'to': {
                    'name': cluster_to,
                    'namespace': np
                }
            }
        })


print(f"{cluster_to} -> Proceso terminado")
