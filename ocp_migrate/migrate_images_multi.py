from unicodedata import name
import requests
import tools

params = tools.get_params()

cluster_from = params['clusters']['from']['name']
url_public_registry = params['clusters']['from']['url_public_registry']

cluster_to = params['clusters']['to']['name']

namespaces = [
    ob
    for ob
    in tools.sh(f'oc get proyects -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
    if not 'openshift-' in ob
]

for np in namespaces:

    print(f"{cluster_to} -> Generando work para {np}")
    tools.new_jaime_work(f'migrate-is-{np}', 'ocp_migrate', 'migrate_images', {
        'clusters': {
            'from': {
                'name': cluster_from,
                'namespace': np,
                'url_public_registry': url_public_registry
            },
            'to': {
                'name': cluster_to
            }
        }
    })


print(f"{cluster_to} -> Proceso terminado")
