from kubernetes import client, config


def generate_pod():
    metadata = client.V1ObjectMeta(
        name="platform-app-958795556-2nqgj",
        namespace="production",
        generate_name="platform-app-958795556-",
        labels={
            "app": "platform",
            "chart": "platform",
            "component": "app",
            "heritage": "Helm",
            "pod-template-hash": "958795556",
            "release": "platform-production",
            "version": "1.0.3",
        },
        owner_references=[
            client.V1OwnerReference(
                api_version="apps/v1",
                kind="ReplicaSet",
                name="platform-app-958795556",
                uid="35ba938b-681d-11eb-a74a-16e1a04d726b",
                controller=True,
                block_owner_deletion=True,
            )
        ],
    )

    container = client.V1Container(
        name="app",
        image="platform.azurecr.io/app:master",
        image_pull_policy="Always",
        termination_message_policy="File",
        termination_message_path="/dev/termination-log",
        env=[],
        resources=client.V1ResourceRequirements(
            limits={"cpu": "1200m", "memory": "1Gi"},
            requests={"cpu": "1", "memory": "768Mi"},
        ),
        ports=[client.V1ContainerPort(container_port=3000, protocol="TCP")],
        volume_mounts=[
            client.V1VolumeMount(
                name="default-token-2cg25",
                read_only=True,
                mount_path="/var/run/secrets/kubernetes.io/serviceaccount",
            )
        ],
        liveness_probe=client.V1Probe(
            initial_delay_seconds=10,
            timeout_seconds=5,
            period_seconds=10,
            success_threshold=1,
            failure_threshold=6,
            http_get=client.V1HTTPGetAction(
                path="/health/liveness", port=3000, scheme="HTTP"
            ),
        ),
        readiness_probe=client.V1Probe(
            initial_delay_seconds=10,
            timeout_seconds=5,
            period_seconds=10,
            success_threshold=2,
            failure_threshold=6,
            http_get=client.V1HTTPGetAction(
                path="/health/readness", port=3000, scheme="HTTP"
            ),
        ),
    )

    spec = client.V1PodSpec(
        containers=[container],
        volumes=[
            client.V1Volume(
                name="default-token-2cg25",
                secret=client.V1SecretVolumeSource(
                    secret_name="default-token-2cg25", default_mode=420
                ),
            )
        ],
        restart_policy="Always",
        termination_grace_period_seconds=30,
        dns_policy="ClusterFirst",
        service_account_name="default",
        service_account="default",
        node_name="aks-agentpool-26722002-vmss00039t",
        security_context=client.V1PodSecurityContext(run_as_user=1000, fs_group=1000),
        scheduler_name="default-scheduler",
        tolerations=[
            client.V1Toleration(
                key="node.kubernetes.io/not-ready",
                operator="Exists",
                effect="NoExecute",
                toleration_seconds=300,
            ),
            client.V1Toleration(
                key="node.kubernetes.io/unreachable",
                operator="Exists",
                effect="NoExecute",
                toleration_seconds=300,
            ),
        ],
        priority=0,
        enable_service_links=True,
    )

    return client.V1Pod(metadata=metadata, spec=spec)


def generate_ingress(ingress_name: str):

    metadata = client.V1ObjectMeta(
        name=ingress_name,
        namespace="production",
        labels={"certmanager-solver": "nginx-platform-production"},
        annotations={
            "kubernetes.io/ingress.class": "nginx-platform-production",
            "kubernetes.io/tls-acme": "true",
            "meta.helm.sh/release-name": "platform-ingress",
            "meta.helm.sh/release-namespace": "production",
            "certmanager.k8s.io/cluster-issuer": "letsencrypt-prod",
            "nginx.ingress.kubernetes.io/ssl-redirect": "true",
            "nginx.ingress.kubernetes.io/proxy-body-size": "0",
            "nginx.ingress.kubernetes.io/server-snippet": "location = /check-dns {\n  return 200;\n}",
            "nginx.ingress.kubernetes.io/configuration-snippet": 'proxy_set_header Host $host;\nproxy_set_header whitelabel "$host";',
        },
    )

    spec = client.ExtensionsV1beta1IngressSpec(
        rules=[
            client.ExtensionsV1beta1IngressRule(
                host=ingress_name,
                http=client.ExtensionsV1beta1HTTPIngressRuleValue(
                    paths=[
                        client.ExtensionsV1beta1HTTPIngressPath(
                            path="/",
                            backend=client.ExtensionsV1beta1IngressBackend(
                                service_name="platform-app", service_port=3000
                            ),
                        )
                    ]
                ),
            )
        ],
        tls=[
            client.ExtensionsV1beta1IngressTLS(
                hosts=[ingress_name], secret_name=ingress_name + "-tls"
            )
        ],
    )

    return client.ExtensionsV1beta1Ingress(
        kind="Ingress", api_version="extensions/v1beta1", metadata=metadata, spec=spec
    )


def pod_test():
    config.load_kube_config()
    azure_core_v1api = client.CoreV1Api()

    pod = generate_pod()

    azure_core_v1api.list_namespaced_pod("production")
    azure_core_v1api.create_namespaced_pod("production", pod)
    azure_core_v1api.delete_namespaced_pod(pod.metadata.name, "production")


def ingress_test():
    config.load_kube_config()
    extensions_v1_beta1_api = client.ExtensionsV1beta1Api()

    ingress = generate_ingress("test_ingress")

    extensions_v1_beta1_api.list_namespaced_ingress("production")
    extensions_v1_beta1_api.create_namespaced_ingress("production", ingress)
    extensions_v1_beta1_api.delete_namespaced_ingress(
        ingress.metadata.name, "production"
    )


ingress_test()
pod_test()