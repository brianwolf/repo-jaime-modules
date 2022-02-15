import yaml
import tools

params = tools.get_params()

server = params['server']['name']
namespace = params['server']['namespace']

image_url = params['jenkins']['image']['url']
image_tag = params['jenkins']['image']['tag']

is_namespace = params['jenkins']['imageStream']['namespace']
is_name = params['jenkins']['imageStream']['name']
is_tag = params['jenkins']['imageStream']['tag']

conf_template = params['jenkins']['config']['template']
conf_ram = params['jenkins']['config']['memoryRAM']
conf_vol = params['jenkins']['config']['memoryVolume']
conf_storage_class = params['jenkins']['config']['storageClass']

oc = tools.get_client(server)
login_success = oc.login()
if not login_success:
    print(f'Error en login {server}')
    exit(0)


print(f'Creando {namespace}')
oc.exec(f'new-project {namespace}')
print(f'\n\n')


print(f'Creando PVC en {namespace} con nombre jenkins')
pvc_yaml = f"""
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: jenkins
  labels:
    app: jenkins-persistent
    template: {conf_template}-template
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: {conf_vol}
    storageClassName: {conf_storage_class}
  volumeMode: Filesystem
"""
with open('pvc.yaml', 'w') as f:
    f.write(pvc_yaml)
oc.exec(f'apply -f pvc.yaml')
print(f'\n\n')


print(f'Descargando imagen {image_url}:{image_tag} en {is_namespace}')
oc.exec(
    f'import-image openshift4/{is_name}:{is_tag} --from={image_url} --confirm -n {is_namespace}')
print(f'\n\n')


print(f'Instalando Jenkins en {namespace}')
oc.exec(f"""new-app -n {namespace} \
	--template={conf_template} \
	--param=NAMESPACE={is_namespace} \
	--param=MEMORY_LIMIT={conf_ram} \
	--param=VOLUME_CAPACITY={conf_vol} \
	--param=JENKINS_IMAGE_STREAM_TAG={is_name}:{is_tag}
""")
print(f'\n\n')


print(f'Creando CRB con nombre jenkins-cluster-admin')
crb_yaml = f"""
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: jenkins-admin
subjects:
  - kind: ServiceAccount
    name: jenkins
    namespace: {namespace}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
"""
with open('crb.yaml', 'w') as f:
    f.write(crb_yaml)
oc.exec(f'apply -f crb.yaml')
print(f'\n\n')


print(f'Configurando Jenkins')
oc.exec(f"""set -n {namespace} env dc jenkins \
JAVA_TOOL_OPTIONS="-Dhttps.protocols=TLSv1.2" \
JAVA_OPTS="-Dhttps.protocols=TLSv1.2 -Djdk.tls.client.protocols=TLSv1.2" """)
