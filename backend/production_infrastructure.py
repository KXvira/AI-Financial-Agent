"""
Sprint 8: Production Infrastructure Configuration
Kubernetes, Docker, monitoring, and auto-scaling setup
"""

import yaml
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class DeploymentEnvironment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class ServiceType(Enum):
    """Service types for deployment"""
    API_GATEWAY = "api-gateway"
    BACKEND_API = "backend-api"
    FRONTEND = "frontend"
    AI_SERVICE = "ai-service"
    DATABASE = "database"
    REDIS = "redis"
    MONITORING = "monitoring"

@dataclass
class ResourceLimits:
    """Container resource limits"""
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"

@dataclass
class AutoScaling:
    """Auto-scaling configuration"""
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_percent: int = 70
    target_memory_percent: int = 80

@dataclass
class ServiceConfig:
    """Service configuration for deployment"""
    name: str
    service_type: ServiceType
    image: str
    port: int
    environment: DeploymentEnvironment
    resources: ResourceLimits
    auto_scaling: AutoScaling
    env_vars: Dict[str, str] = field(default_factory=dict)
    config_maps: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    health_check_path: str = "/health"

class ProductionInfrastructure:
    """
    Production infrastructure management for Kubernetes deployment
    """
    
    def __init__(self):
        self.namespace = "ai-financial-agent"
        self.domain = "ai-finance.company.com"
        
        # Service configurations
        self.services = self._initialize_services()
        
        # Infrastructure components
        self.monitoring_stack = self._initialize_monitoring()
        self.security_configs = self._initialize_security()

    def _initialize_services(self) -> Dict[str, ServiceConfig]:
        """Initialize service configurations"""
        return {
            "api-gateway": ServiceConfig(
                name="api-gateway",
                service_type=ServiceType.API_GATEWAY,
                image="ai-finance/api-gateway:latest",
                port=8000,
                environment=DeploymentEnvironment.PRODUCTION,
                resources=ResourceLimits(
                    cpu_request="200m",
                    cpu_limit="1000m",
                    memory_request="256Mi",
                    memory_limit="1Gi"
                ),
                auto_scaling=AutoScaling(
                    min_replicas=2,
                    max_replicas=20,
                    target_cpu_percent=70
                ),
                env_vars={
                    "REDIS_URL": "redis://redis-service:6379",
                    "JWT_SECRET": "${JWT_SECRET}",
                    "RATE_LIMIT_ENABLED": "true"
                },
                secrets=["jwt-secret", "api-keys"]
            ),
            
            "backend-api": ServiceConfig(
                name="backend-api",
                service_type=ServiceType.BACKEND_API,
                image="ai-finance/backend:latest",
                port=8001,
                environment=DeploymentEnvironment.PRODUCTION,
                resources=ResourceLimits(
                    cpu_request="500m",
                    cpu_limit="2000m",
                    memory_request="1Gi",
                    memory_limit="4Gi"
                ),
                auto_scaling=AutoScaling(
                    min_replicas=3,
                    max_replicas=50,
                    target_cpu_percent=60
                ),
                env_vars={
                    "MONGODB_URL": "${MONGODB_URL}",
                    "GEMINI_API_KEY": "${GEMINI_API_KEY}",
                    "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                    "ENVIRONMENT": "production"
                },
                secrets=["mongodb-credentials", "ai-api-keys"]
            ),
            
            "ai-service": ServiceConfig(
                name="ai-service",
                service_type=ServiceType.AI_SERVICE,
                image="ai-finance/ai-orchestrator:latest",
                port=8002,
                environment=DeploymentEnvironment.PRODUCTION,
                resources=ResourceLimits(
                    cpu_request="1000m",
                    cpu_limit="4000m",
                    memory_request="2Gi",
                    memory_limit="8Gi"
                ),
                auto_scaling=AutoScaling(
                    min_replicas=2,
                    max_replicas=30,
                    target_cpu_percent=80
                ),
                env_vars={
                    "MODEL_CACHE_SIZE": "1000",
                    "PREDICTION_TIMEOUT": "300",
                    "GPU_ENABLED": "false"
                },
                secrets=["ai-api-keys"]
            ),
            
            "frontend": ServiceConfig(
                name="frontend",
                service_type=ServiceType.FRONTEND,
                image="ai-finance/frontend:latest",
                port=3000,
                environment=DeploymentEnvironment.PRODUCTION,
                resources=ResourceLimits(
                    cpu_request="100m",
                    cpu_limit="500m",
                    memory_request="128Mi",
                    memory_limit="512Mi"
                ),
                auto_scaling=AutoScaling(
                    min_replicas=2,
                    max_replicas=10,
                    target_cpu_percent=70
                ),
                env_vars={
                    "NEXT_PUBLIC_API_URL": "https://api.ai-finance.company.com",
                    "NODE_ENV": "production"
                }
            )
        }

    def _initialize_monitoring(self) -> Dict[str, Any]:
        """Initialize monitoring stack configuration"""
        return {
            "prometheus": {
                "enabled": True,
                "retention": "30d",
                "storage_size": "50Gi",
                "scrape_interval": "15s"
            },
            "grafana": {
                "enabled": True,
                "admin_password": "${GRAFANA_ADMIN_PASSWORD}",
                "dashboards": [
                    "api-performance",
                    "infrastructure-health",
                    "business-metrics",
                    "ai-model-performance"
                ]
            },
            "alertmanager": {
                "enabled": True,
                "webhook_url": "${SLACK_WEBHOOK_URL}",
                "email_smtp": "${SMTP_CONFIG}"
            },
            "jaeger": {
                "enabled": True,
                "storage": "elasticsearch"
            }
        }

    def _initialize_security(self) -> Dict[str, Any]:
        """Initialize security configurations"""
        return {
            "network_policies": {
                "enabled": True,
                "default_deny": True,
                "allow_rules": [
                    "api-gateway -> backend-api",
                    "backend-api -> ai-service",
                    "backend-api -> database",
                    "frontend -> api-gateway"
                ]
            },
            "pod_security": {
                "run_as_non_root": True,
                "read_only_filesystem": True,
                "no_privilege_escalation": True
            },
            "secrets_management": {
                "external_secrets_operator": True,
                "vault_integration": True,
                "auto_rotation": True
            }
        }

    def generate_kubernetes_manifests(self, environment: DeploymentEnvironment) -> Dict[str, str]:
        """Generate Kubernetes manifests for all services"""
        manifests = {}
        
        # Generate namespace
        manifests["namespace.yaml"] = self._generate_namespace()
        
        # Generate service manifests
        for service_name, config in self.services.items():
            if config.environment == environment:
                manifests[f"{service_name}-deployment.yaml"] = self._generate_deployment(config)
                manifests[f"{service_name}-service.yaml"] = self._generate_service(config)
                manifests[f"{service_name}-hpa.yaml"] = self._generate_hpa(config)
        
        # Generate ingress
        manifests["ingress.yaml"] = self._generate_ingress()
        
        # Generate monitoring
        manifests.update(self._generate_monitoring_manifests())
        
        # Generate security policies
        manifests.update(self._generate_security_manifests())
        
        return manifests

    def _generate_namespace(self) -> str:
        """Generate namespace manifest"""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.namespace,
                "labels": {
                    "name": self.namespace,
                    "environment": "production"
                }
            }
        }
        return yaml.dump(namespace, default_flow_style=False)

    def _generate_deployment(self, config: ServiceConfig) -> str:
        """Generate deployment manifest for service"""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.name,
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value,
                    "environment": config.environment.value
                }
            },
            "spec": {
                "replicas": config.auto_scaling.min_replicas,
                "selector": {
                    "matchLabels": {
                        "app": config.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.name,
                            "service-type": config.service_type.value
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": str(config.port),
                            "prometheus.io/path": "/metrics"
                        }
                    },
                    "spec": {
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000,
                            "fsGroup": 1000
                        },
                        "containers": [
                            {
                                "name": config.name,
                                "image": config.image,
                                "ports": [
                                    {
                                        "containerPort": config.port,
                                        "name": "http"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": config.resources.cpu_request,
                                        "memory": config.resources.memory_request
                                    },
                                    "limits": {
                                        "cpu": config.resources.cpu_limit,
                                        "memory": config.resources.memory_limit
                                    }
                                },
                                "env": [
                                    {"name": k, "value": v}
                                    for k, v in config.env_vars.items()
                                ],
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": config.health_check_path,
                                        "port": config.port
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                    "timeoutSeconds": 5,
                                    "failureThreshold": 3
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": config.health_check_path,
                                        "port": config.port
                                    },
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 5,
                                    "timeoutSeconds": 3,
                                    "failureThreshold": 3
                                },
                                "securityContext": {
                                    "allowPrivilegeEscalation": False,
                                    "readOnlyRootFilesystem": True,
                                    "capabilities": {
                                        "drop": ["ALL"]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        # Add volume mounts for secrets and config maps
        if config.secrets or config.config_maps:
            volumes = []
            volume_mounts = []
            
            for secret in config.secrets:
                volumes.append({
                    "name": f"{secret}-volume",
                    "secret": {"secretName": secret}
                })
                volume_mounts.append({
                    "name": f"{secret}-volume",
                    "mountPath": f"/etc/secrets/{secret}",
                    "readOnly": True
                })
            
            for config_map in config.config_maps:
                volumes.append({
                    "name": f"{config_map}-volume",
                    "configMap": {"name": config_map}
                })
                volume_mounts.append({
                    "name": f"{config_map}-volume",
                    "mountPath": f"/etc/config/{config_map}",
                    "readOnly": True
                })
            
            deployment["spec"]["template"]["spec"]["volumes"] = volumes
            deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = volume_mounts
        
        return yaml.dump(deployment, default_flow_style=False)

    def _generate_service(self, config: ServiceConfig) -> str:
        """Generate service manifest"""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{config.name}-service",
                "namespace": self.namespace,
                "labels": {
                    "app": config.name,
                    "service-type": config.service_type.value
                }
            },
            "spec": {
                "selector": {
                    "app": config.name
                },
                "ports": [
                    {
                        "port": 80,
                        "targetPort": config.port,
                        "protocol": "TCP",
                        "name": "http"
                    }
                ],
                "type": "ClusterIP"
            }
        }
        return yaml.dump(service, default_flow_style=False)

    def _generate_hpa(self, config: ServiceConfig) -> str:
        """Generate horizontal pod autoscaler manifest"""
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{config.name}-hpa",
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": config.name
                },
                "minReplicas": config.auto_scaling.min_replicas,
                "maxReplicas": config.auto_scaling.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": config.auto_scaling.target_cpu_percent
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": config.auto_scaling.target_memory_percent
                            }
                        }
                    }
                ],
                "behavior": {
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 100,
                                "periodSeconds": 60
                            }
                        ]
                    },
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 10,
                                "periodSeconds": 60
                            }
                        ]
                    }
                }
            }
        }
        return yaml.dump(hpa, default_flow_style=False)

    def _generate_ingress(self) -> str:
        """Generate ingress manifest"""
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "ai-finance-ingress",
                "namespace": self.namespace,
                "annotations": {
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/rate-limit": "1000",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m",
                    "nginx.ingress.kubernetes.io/cors-allow-origin": "*",
                    "nginx.ingress.kubernetes.io/cors-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "nginx.ingress.kubernetes.io/cors-allow-headers": "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization"
                }
            },
            "spec": {
                "tls": [
                    {
                        "hosts": [self.domain, f"api.{self.domain}"],
                        "secretName": "ai-finance-tls"
                    }
                ],
                "rules": [
                    {
                        "host": self.domain,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "frontend-service",
                                            "port": {"number": 80}
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "host": f"api.{self.domain}",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "api-gateway-service",
                                            "port": {"number": 80}
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return yaml.dump(ingress, default_flow_style=False)

    def _generate_monitoring_manifests(self) -> Dict[str, str]:
        """Generate monitoring stack manifests"""
        manifests = {}
        
        # Prometheus configuration
        prometheus_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "prometheus-config",
                "namespace": self.namespace
            },
            "data": {
                "prometheus.yml": yaml.dump({
                    "global": {
                        "scrape_interval": self.monitoring_stack["prometheus"]["scrape_interval"],
                        "evaluation_interval": "15s"
                    },
                    "scrape_configs": [
                        {
                            "job_name": "kubernetes-pods",
                            "kubernetes_sd_configs": [{"role": "pod"}],
                            "relabel_configs": [
                                {
                                    "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_scrape"],
                                    "action": "keep",
                                    "regex": "true"
                                }
                            ]
                        }
                    ]
                }, default_flow_style=False)
            }
        }
        manifests["prometheus-config.yaml"] = yaml.dump(prometheus_config, default_flow_style=False)
        
        # ServiceMonitor for custom metrics
        service_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": "ai-finance-monitor",
                "namespace": self.namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": "backend-api"
                    }
                },
                "endpoints": [
                    {
                        "port": "http",
                        "path": "/metrics",
                        "interval": "30s"
                    }
                ]
            }
        }
        manifests["service-monitor.yaml"] = yaml.dump(service_monitor, default_flow_style=False)
        
        return manifests

    def _generate_security_manifests(self) -> Dict[str, str]:
        """Generate security policy manifests"""
        manifests = {}
        
        # Network policy
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "ai-finance-network-policy",
                "namespace": self.namespace
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "name": "ingress-nginx"
                                    }
                                }
                            }
                        ]
                    }
                ],
                "egress": [
                    {
                        "to": [],
                        "ports": [
                            {"protocol": "TCP", "port": 53},
                            {"protocol": "UDP", "port": 53},
                            {"protocol": "TCP", "port": 443},
                            {"protocol": "TCP", "port": 80}
                        ]
                    }
                ]
            }
        }
        manifests["network-policy.yaml"] = yaml.dump(network_policy, default_flow_style=False)
        
        # Pod security policy
        pod_security_policy = {
            "apiVersion": "policy/v1beta1",
            "kind": "PodSecurityPolicy",
            "metadata": {
                "name": "ai-finance-psp"
            },
            "spec": {
                "privileged": False,
                "allowPrivilegeEscalation": False,
                "requiredDropCapabilities": ["ALL"],
                "volumes": ["configMap", "emptyDir", "projected", "secret", "downwardAPI", "persistentVolumeClaim"],
                "runAsUser": {"rule": "MustRunAsNonRoot"},
                "seLinux": {"rule": "RunAsAny"},
                "fsGroup": {"rule": "RunAsAny"}
            }
        }
        manifests["pod-security-policy.yaml"] = yaml.dump(pod_security_policy, default_flow_style=False)
        
        return manifests

    def generate_docker_compose(self, environment: DeploymentEnvironment) -> str:
        """Generate Docker Compose for local development"""
        services = {}
        
        for service_name, config in self.services.items():
            if config.environment == environment:
                services[service_name] = {
                    "image": config.image,
                    "ports": [f"{config.port}:{config.port}"],
                    "environment": config.env_vars,
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": [f"curl -f http://localhost:{config.port}{config.health_check_path} || exit 1"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                }
        
        # Add supporting services
        services.update({
            "mongodb": {
                "image": "mongo:5.0",
                "ports": ["27017:27017"],
                "environment": {
                    "MONGO_INITDB_ROOT_USERNAME": "admin",
                    "MONGO_INITDB_ROOT_PASSWORD": "password"
                },
                "volumes": ["mongodb_data:/data/db"]
            },
            "redis": {
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
                "volumes": ["redis_data:/data"]
            }
        })
        
        compose = {
            "version": "3.8",
            "services": services,
            "volumes": {
                "mongodb_data": {},
                "redis_data": {}
            }
        }
        
        return yaml.dump(compose, default_flow_style=False)

    def generate_deployment_scripts(self) -> Dict[str, str]:
        """Generate deployment scripts"""
        scripts = {}
        
        # Kubernetes deployment script
        scripts["deploy.sh"] = """#!/bin/bash
set -e

NAMESPACE="ai-financial-agent"
ENVIRONMENT=${1:-production}

echo "Deploying AI Financial Agent to $ENVIRONMENT environment..."

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply all manifests
kubectl apply -f manifests/ -n $NAMESPACE

# Wait for deployments to be ready
kubectl rollout status deployment/api-gateway -n $NAMESPACE
kubectl rollout status deployment/backend-api -n $NAMESPACE
kubectl rollout status deployment/ai-service -n $NAMESPACE
kubectl rollout status deployment/frontend -n $NAMESPACE

echo "Deployment completed successfully!"

# Show service status
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE
"""
        
        # Health check script
        scripts["health-check.sh"] = """#!/bin/bash
set -e

NAMESPACE="ai-financial-agent"
DOMAIN="ai-finance.company.com"

echo "Running health checks..."

# Check pod status
echo "Checking pod status..."
kubectl get pods -n $NAMESPACE

# Check service endpoints
echo "Checking service endpoints..."
curl -f https://api.$DOMAIN/health || echo "API Gateway health check failed"
curl -f https://$DOMAIN/ || echo "Frontend health check failed"

# Check resource usage
echo "Checking resource usage..."
kubectl top pods -n $NAMESPACE

echo "Health checks completed!"
"""
        
        # Backup script
        scripts["backup.sh"] = """#!/bin/bash
set -e

NAMESPACE="ai-financial-agent"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)

echo "Creating backup for $BACKUP_DATE..."

# Backup MongoDB
kubectl exec -n $NAMESPACE deployment/mongodb -- mongodump --out /tmp/backup_$BACKUP_DATE
kubectl cp $NAMESPACE/mongodb-pod:/tmp/backup_$BACKUP_DATE ./backups/mongodb_$BACKUP_DATE

# Backup configurations
kubectl get configmaps -n $NAMESPACE -o yaml > ./backups/configmaps_$BACKUP_DATE.yaml
kubectl get secrets -n $NAMESPACE -o yaml > ./backups/secrets_$BACKUP_DATE.yaml

echo "Backup completed: $BACKUP_DATE"
"""
        
        return scripts

# Initialize production infrastructure
production_infra = ProductionInfrastructure()