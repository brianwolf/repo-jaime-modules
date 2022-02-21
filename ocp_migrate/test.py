import tools
import re

params = tools.get_params()

server_from = params['servers']['from']['name']
namespace_from = params['servers']['from']['namespace']
object_from = params['servers']['from']['object']
only_from = params['servers']['from'].get('only', [])
ignore_from = params['servers']['from'].get('ignore', [])

oc_from = tools.get_client(server_from)
login_success = oc_from.login()
if not login_success:
    print(f'Error en login {server_from}')
    exit(0)

print(f"{server_from} -> Obtieniendo todos los objetos")
objects = [
    ob
    for ob
    in oc_from.exec(f'get {object_from} -n {namespace_from} -o custom-columns=NAME:.metadata.name', echo=False).split('\n')[1:]
]


objects_to_migrate = []
for ob in objects:

    if only_from:
        match_all_regex = len(
            [regex for regex in only_from if re.match(regex, ob)]) == len(only_from)
        if not match_all_regex:
            continue

    if ignore_from:
        match_any_regex = any(
            True for regex in ignore_from if re.match(regex, ob))
        if match_any_regex:
            continue

    objects_to_migrate.append(ob)

print(f"{server_from} -> Objetos entontrados: {len(objects_to_migrate)}")

for ob in objects_to_migrate:
    print(ob)

print(f"{server_from} -> Proceso terminado OK")
