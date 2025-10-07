"""
Sprint 8: Enterprise API Gateway
Advanced rate limiting, tenant isolation, and API management
"""

import asyncio
import json
import time
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import hmac

# Optional imports with fallbacks
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

try:
    from fastapi import Request, Response, HTTPException
    from fastapi.middleware.base import BaseHTTPMiddleware
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Mock classes for testing without FastAPI
    class Request:
        def __init__(self):
            self.url = type('obj', (object,), {'path': '/test'})()
            self.method = 'GET'
            self.headers = {}
            self.client = type('obj', (object,), {'host': '127.0.0.1'})()
    
    class Response:
        def __init__(self):
            self.status_code = 200
            self.headers = {}
    
    class BaseHTTPMiddleware:
        def __init__(self, app): pass
        async def dispatch(self, request, call_next): pass
    
    class JSONResponse:
        def __init__(self, status_code=200, content=None, headers=None):
            self.status_code = status_code
            self.content = content
            self.headers = headers or {}

class RateLimitType(Enum):
    """Rate limit types"""
    PER_USER = "per_user"
    PER_TENANT = "per_tenant"
    PER_IP = "per_ip"
    PER_API_KEY = "per_api_key"

class ThrottleStrategy(Enum):
    """Throttling strategies"""
    BLOCK = "block"  # Block requests when limit exceeded
    QUEUE = "queue"  # Queue requests when limit exceeded
    DEGRADE = "degrade"  # Degrade service quality

@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    name: str
    limit_type: RateLimitType
    max_requests: int
    window_seconds: int
    burst_capacity: int = 0  # Allow burst above normal rate
    strategy: ThrottleStrategy = ThrottleStrategy.BLOCK
    endpoints: List[str] = field(default_factory=list)  # Specific endpoints
    tenant_overrides: Dict[str, int] = field(default_factory=dict)  # Per-tenant limits

@dataclass
class APIKey:
    """API key configuration"""
    key_id: str
    tenant_id: str
    name: str
    key_hash: str
    permissions: List[str]
    rate_limits: Dict[str, int]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0

@dataclass
class RequestMetrics:
    """Request metrics tracking"""
    timestamp: datetime
    tenant_id: str
    user_id: Optional[str]
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    request_size: int
    response_size: int
    ip_address: str
    user_agent: str

class EnterpriseAPIGateway:
    """
    Enterprise API Gateway with advanced rate limiting and tenant isolation
    """
    
    def __init__(self, redis_client=None):
        self.logger = logging.getLogger(__name__)
        
        # Redis for distributed rate limiting (fallback to in-memory)
        self.redis_client = redis_client
        self.local_cache: Dict[str, Any] = {}
        
        # Configuration
        self.rate_limit_rules: List[RateLimitRule] = []
        self.api_keys: Dict[str, APIKey] = {}
        self.tenant_quotas: Dict[str, Dict[str, int]] = {}
        
        # Metrics storage
        self.request_metrics: List[RequestMetrics] = []
        self.metrics_buffer_size = 10000
        
        # Initialize default rate limits
        self._initialize_default_rules()
        
        # Background tasks
        self._cleanup_task = None
        
    def _initialize_default_rules(self):
        """Initialize default rate limiting rules"""
        default_rules = [
            # Per-user limits
            RateLimitRule(
                name="user_general",
                limit_type=RateLimitType.PER_USER,
                max_requests=1000,
                window_seconds=3600,  # 1 hour
                burst_capacity=100,
                strategy=ThrottleStrategy.BLOCK
            ),
            
            # Per-tenant limits
            RateLimitRule(
                name="tenant_general",
                limit_type=RateLimitType.PER_TENANT,
                max_requests=10000,
                window_seconds=3600,  # 1 hour
                burst_capacity=1000,
                strategy=ThrottleStrategy.QUEUE
            ),
            
            # Per-IP limits (DDoS protection)
            RateLimitRule(
                name="ip_protection",
                limit_type=RateLimitType.PER_IP,
                max_requests=100,
                window_seconds=60,  # 1 minute
                strategy=ThrottleStrategy.BLOCK
            ),
            
            # API-specific limits
            RateLimitRule(
                name="forecast_endpoint",
                limit_type=RateLimitType.PER_USER,
                max_requests=50,
                window_seconds=3600,  # 1 hour
                endpoints=["/api/v1/forecasting/predict", "/api/v1/forecasting/analyze"],
                strategy=ThrottleStrategy.DEGRADE
            ),
            
            # Export limits (expensive operations)
            RateLimitRule(
                name="export_operations",
                limit_type=RateLimitType.PER_TENANT,
                max_requests=10,
                window_seconds=3600,  # 1 hour
                endpoints=["/api/v1/reporting/export", "/api/v1/analytics/export"],
                strategy=ThrottleStrategy.BLOCK
            )
        ]
        
        self.rate_limit_rules.extend(default_rules)

    async def create_api_key(self, tenant_id: str, name: str, 
                           permissions: List[str], rate_limits: Dict[str, int] = None,
                           expires_days: int = None) -> Dict[str, Any]:
        """Create new API key for tenant"""
        try:
            key_id = str(uuid.uuid4())
            api_key = f"ak_{secrets.token_urlsafe(32)}"
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            expires_at = None
            if expires_days:
                expires_at = datetime.now() + timedelta(days=expires_days)
            
            api_key_obj = APIKey(
                key_id=key_id,
                tenant_id=tenant_id,
                name=name,
                key_hash=key_hash,
                permissions=permissions,
                rate_limits=rate_limits or {},
                expires_at=expires_at
            )
            
            self.api_keys[key_id] = api_key_obj
            
            return {
                "key_id": key_id,
                "api_key": api_key,  # Only returned once
                "name": name,
                "permissions": permissions,
                "rate_limits": rate_limits,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "status": "created"
            }
            
        except Exception as e:
            self.logger.error(f"API key creation failed: {str(e)}")
            raise

    async def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return key info"""
        try:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            for key_obj in self.api_keys.values():
                if key_obj.key_hash == key_hash and key_obj.is_active:
                    # Check expiration
                    if key_obj.expires_at and datetime.now() > key_obj.expires_at:
                        key_obj.is_active = False
                        return None
                    
                    # Update usage
                    key_obj.last_used = datetime.now()
                    key_obj.usage_count += 1
                    
                    return key_obj
            
            return None
            
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return None

    async def check_rate_limit(self, request: Request, tenant_id: str, 
                             user_id: Optional[str] = None, 
                             api_key_id: Optional[str] = None) -> Dict[str, Any]:
        """Check all applicable rate limits"""
        try:
            endpoint = request.url.path
            ip_address = self._get_client_ip(request)
            current_time = time.time()
            
            violations = []
            applied_limits = []
            
            # Check each rate limit rule
            for rule in self.rate_limit_rules:
                # Check if rule applies to this endpoint
                if rule.endpoints and endpoint not in rule.endpoints:
                    continue
                
                # Determine the key for rate limiting
                limit_key = self._get_rate_limit_key(rule, tenant_id, user_id, ip_address, api_key_id)
                if not limit_key:
                    continue
                
                # Get effective limit (check tenant overrides)
                effective_limit = rule.max_requests
                if rule.tenant_overrides.get(tenant_id):
                    effective_limit = rule.tenant_overrides[tenant_id]
                
                # Check the rate limit
                usage = await self._check_limit(limit_key, effective_limit, rule.window_seconds, current_time)
                
                applied_limits.append({
                    "rule": rule.name,
                    "limit": effective_limit,
                    "window": rule.window_seconds,
                    "current_usage": usage["current"],
                    "remaining": max(0, effective_limit - usage["current"]),
                    "reset_time": usage["reset_time"]
                })
                
                # Check if limit exceeded
                if usage["current"] >= effective_limit:
                    if rule.strategy == ThrottleStrategy.BLOCK:
                        violations.append({
                            "rule": rule.name,
                            "limit": effective_limit,
                            "current": usage["current"],
                            "strategy": "block"
                        })
                    elif rule.strategy == ThrottleStrategy.QUEUE:
                        # Add to queue (simplified implementation)
                        await self._queue_request(limit_key, request)
                    elif rule.strategy == ThrottleStrategy.DEGRADE:
                        # Mark for service degradation
                        violations.append({
                            "rule": rule.name,
                            "limit": effective_limit,
                            "current": usage["current"],
                            "strategy": "degrade"
                        })
            
            # Increment counters for successful check
            if not any(v["strategy"] == "block" for v in violations):
                for rule in self.rate_limit_rules:
                    if rule.endpoints and endpoint not in rule.endpoints:
                        continue
                    
                    limit_key = self._get_rate_limit_key(rule, tenant_id, user_id, ip_address, api_key_id)
                    if limit_key:
                        await self._increment_counter(limit_key, rule.window_seconds, current_time)
            
            return {
                "allowed": len([v for v in violations if v["strategy"] == "block"]) == 0,
                "violations": violations,
                "applied_limits": applied_limits,
                "degrade_service": any(v["strategy"] == "degrade" for v in violations)
            }
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            # Fail open - allow request if rate limiting fails
            return {"allowed": True, "violations": [], "applied_limits": []}

    def _get_rate_limit_key(self, rule: RateLimitRule, tenant_id: str, 
                           user_id: Optional[str], ip_address: str, 
                           api_key_id: Optional[str]) -> Optional[str]:
        """Generate rate limit key based on rule type"""
        if rule.limit_type == RateLimitType.PER_USER and user_id:
            return f"rate_limit:user:{user_id}:{rule.name}"
        elif rule.limit_type == RateLimitType.PER_TENANT:
            return f"rate_limit:tenant:{tenant_id}:{rule.name}"
        elif rule.limit_type == RateLimitType.PER_IP:
            return f"rate_limit:ip:{ip_address}:{rule.name}"
        elif rule.limit_type == RateLimitType.PER_API_KEY and api_key_id:
            return f"rate_limit:api_key:{api_key_id}:{rule.name}"
        
        return None

    async def _check_limit(self, key: str, limit: int, window: int, 
                          current_time: float) -> Dict[str, Any]:
        """Check current usage against limit"""
        try:
            if self.redis_client:
                # Use Redis for distributed rate limiting
                pipe = self.redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, current_time - window)
                pipe.zcard(key)
                pipe.expire(key, window)
                results = pipe.execute()
                current_usage = results[1]
            else:
                # Use local cache
                if key not in self.local_cache:
                    self.local_cache[key] = []
                
                # Clean old entries
                self.local_cache[key] = [
                    timestamp for timestamp in self.local_cache[key]
                    if timestamp > current_time - window
                ]
                
                current_usage = len(self.local_cache[key])
            
            return {
                "current": current_usage,
                "limit": limit,
                "reset_time": current_time + window
            }
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed for key {key}: {str(e)}")
            return {"current": 0, "limit": limit, "reset_time": current_time + window}

    async def _increment_counter(self, key: str, window: int, current_time: float):
        """Increment rate limit counter"""
        try:
            if self.redis_client:
                # Use Redis
                pipe = self.redis_client.pipeline()
                pipe.zadd(key, {str(uuid.uuid4()): current_time})
                pipe.expire(key, window)
                pipe.execute()
            else:
                # Use local cache
                if key not in self.local_cache:
                    self.local_cache[key] = []
                
                self.local_cache[key].append(current_time)
                
        except Exception as e:
            self.logger.error(f"Counter increment failed for key {key}: {str(e)}")

    async def _queue_request(self, limit_key: str, request: Request):
        """Queue request when rate limit exceeded (simplified implementation)"""
        # In production, this would use a proper message queue
        queue_key = f"queue:{limit_key}"
        
        if self.redis_client:
            self.redis_client.lpush(queue_key, json.dumps({
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
                "timestamp": time.time()
            }))
        else:
            # Local queue (not recommended for production)
            if queue_key not in self.local_cache:
                self.local_cache[queue_key] = []
            
            self.local_cache[queue_key].append({
                "url": str(request.url),
                "method": request.method,
                "timestamp": time.time()
            })

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"

    async def track_request_metrics(self, request: Request, response: Response,
                                  tenant_id: str, user_id: Optional[str],
                                  start_time: float, end_time: float):
        """Track request metrics for analytics"""
        try:
            metrics = RequestMetrics(
                timestamp=datetime.fromtimestamp(start_time),
                tenant_id=tenant_id,
                user_id=user_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                response_time_ms=(end_time - start_time) * 1000,
                request_size=int(request.headers.get("content-length", 0)),
                response_size=len(response.body) if hasattr(response, 'body') else 0,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            self.request_metrics.append(metrics)
            
            # Keep buffer size manageable
            if len(self.request_metrics) > self.metrics_buffer_size:
                self.request_metrics = self.request_metrics[-self.metrics_buffer_size:]
            
            # Log high response times
            if metrics.response_time_ms > 5000:  # 5 seconds
                self.logger.warning(
                    f"Slow request: {metrics.endpoint} took {metrics.response_time_ms:.2f}ms "
                    f"for tenant {tenant_id}"
                )
            
        except Exception as e:
            self.logger.error(f"Metrics tracking failed: {str(e)}")

    async def get_tenant_metrics(self, tenant_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get request metrics for tenant"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        tenant_metrics = [
            m for m in self.request_metrics
            if m.tenant_id == tenant_id and m.timestamp >= cutoff_time
        ]
        
        if not tenant_metrics:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "error_rate": 0,
                "top_endpoints": [],
                "request_volume": []
            }
        
        # Calculate metrics
        total_requests = len(tenant_metrics)
        avg_response_time = sum(m.response_time_ms for m in tenant_metrics) / total_requests
        error_count = len([m for m in tenant_metrics if m.status_code >= 400])
        error_rate = error_count / total_requests * 100
        
        # Top endpoints
        endpoint_counts = {}
        for metric in tenant_metrics:
            endpoint_counts[metric.endpoint] = endpoint_counts.get(metric.endpoint, 0) + 1
        
        top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Request volume by hour
        volume_by_hour = {}
        for metric in tenant_metrics:
            hour_key = metric.timestamp.strftime("%Y-%m-%d %H:00")
            volume_by_hour[hour_key] = volume_by_hour.get(hour_key, 0) + 1
        
        request_volume = [
            {"hour": k, "requests": v}
            for k, v in sorted(volume_by_hour.items())
        ]
        
        return {
            "total_requests": total_requests,
            "avg_response_time": round(avg_response_time, 2),
            "error_rate": round(error_rate, 2),
            "top_endpoints": [{"endpoint": ep, "requests": count} for ep, count in top_endpoints],
            "request_volume": request_volume,
            "period_hours": hours
        }

    async def update_tenant_quotas(self, tenant_id: str, quotas: Dict[str, int]):
        """Update tenant quotas"""
        self.tenant_quotas[tenant_id] = quotas
        
        # Update rate limit rules with tenant overrides
        for rule in self.rate_limit_rules:
            if rule.limit_type == RateLimitType.PER_TENANT:
                quota_key = f"rate_limit_{rule.name}"
                if quota_key in quotas:
                    rule.tenant_overrides[tenant_id] = quotas[quota_key]

    async def get_api_gateway_status(self) -> Dict[str, Any]:
        """Get API gateway status and metrics"""
        recent_metrics = [
            m for m in self.request_metrics
            if m.timestamp >= datetime.now() - timedelta(minutes=5)
        ]
        
        return {
            "status": "operational",
            "active_rate_limits": len(self.rate_limit_rules),
            "api_keys_count": len([k for k in self.api_keys.values() if k.is_active]),
            "recent_requests": len(recent_metrics),
            "avg_response_time_5min": (
                sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
                if recent_metrics else 0
            ),
            "cache_type": "redis" if self.redis_client else "local",
            "metrics_buffer_size": len(self.request_metrics),
            "last_updated": datetime.now().isoformat()
        }

class APIGatewayMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for API gateway functionality"""
    
    def __init__(self, app, gateway: EnterpriseAPIGateway, security_manager):
        super().__init__(app)
        self.gateway = gateway
        self.security_manager = security_manager
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            # Extract authentication info
            tenant_id = "unknown"
            user_id = None
            api_key_id = None
            
            # Check for API key
            api_key = request.headers.get("X-API-Key")
            if api_key:
                key_obj = await self.gateway.validate_api_key(api_key)
                if not key_obj:
                    return JSONResponse(
                        status_code=401,
                        content={"error": "Invalid API key"}
                    )
                tenant_id = key_obj.tenant_id
                api_key_id = key_obj.key_id
            else:
                # Check for JWT token
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    try:
                        user_info = await self.security_manager.validate_token(token)
                        tenant_id = user_info["tenant_id"]
                        user_id = user_info["user_id"]
                    except Exception:
                        pass  # Continue as unauthenticated
            
            # Check rate limits
            rate_limit_result = await self.gateway.check_rate_limit(
                request, tenant_id, user_id, api_key_id
            )
            
            if not rate_limit_result["allowed"]:
                # Rate limit exceeded
                violations = rate_limit_result["violations"]
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "violations": violations,
                        "retry_after": min(v.get("reset_time", 60) for v in violations)
                    },
                    headers={
                        "Retry-After": str(min(v.get("reset_time", 60) for v in violations)),
                        "X-RateLimit-Limit": str(max(v.get("limit", 0) for v in violations)),
                        "X-RateLimit-Remaining": "0"
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            if rate_limit_result["applied_limits"]:
                main_limit = rate_limit_result["applied_limits"][0]
                response.headers["X-RateLimit-Limit"] = str(main_limit["limit"])
                response.headers["X-RateLimit-Remaining"] = str(main_limit["remaining"])
                response.headers["X-RateLimit-Reset"] = str(int(main_limit["reset_time"]))
            
            # Track metrics
            end_time = time.time()
            await self.gateway.track_request_metrics(
                request, response, tenant_id, user_id, start_time, end_time
            )
            
            return response
            
        except Exception as e:
            # Log error and return generic error response
            self.gateway.logger.error(f"API Gateway error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )

# Initialize the API gateway
api_gateway = EnterpriseAPIGateway()