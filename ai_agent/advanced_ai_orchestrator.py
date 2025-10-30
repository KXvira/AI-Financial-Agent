"""
Sprint 8: Advanced AI Orchestration System
Multi-provider AI support with intelligent model selection
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib

class AIProvider(Enum):
    """Available AI providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"
    LOCAL_LLM = "local_llm"

@dataclass
class AIModelConfig:
    """Configuration for an AI model"""
    provider: AIProvider
    model_name: str
    strengths: List[str]
    use_cases: List[str]
    cost_per_token: float
    max_tokens: int
    response_time_avg: float  # in seconds
    accuracy_score: float  # 0-1
    reliability_score: float  # 0-1

@dataclass
class AIRequest:
    """Request for AI processing"""
    task_type: str
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"  # low, normal, high, critical
    max_response_time: float = 30.0
    quality_threshold: float = 0.8
    budget_limit: float = None  # cost limit in USD

@dataclass
class AIResponse:
    """Response from AI processing"""
    content: str
    provider: AIProvider
    model_used: str
    confidence_score: float
    processing_time: float
    cost_incurred: float
    quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdvancedAIOrchestrator:
    """
    Advanced AI orchestration system with multi-provider support
    Intelligently selects optimal AI models based on task requirements
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI model configurations
        self.models = self._initialize_model_configs()
        
        # Performance tracking
        self.performance_history = {}
        self.model_usage_stats = {provider.value: 0 for provider in AIProvider}
        
        # Intelligent routing cache
        self.routing_cache = {}
        
        # Advanced prompt templates
        self.prompt_templates = self._initialize_prompt_templates()

    def _initialize_model_configs(self) -> Dict[str, AIModelConfig]:
        """Initialize configurations for available AI models"""
        return {
            "gemini_pro": AIModelConfig(
                provider=AIProvider.GEMINI,
                model_name="gemini-pro",
                strengths=["reasoning", "analysis", "financial_modeling"],
                use_cases=["cash_flow_forecasting", "risk_assessment", "business_insights"],
                cost_per_token=0.0005,
                max_tokens=8192,
                response_time_avg=2.1,
                accuracy_score=0.87,
                reliability_score=0.94
            ),
            "gemini_flash": AIModelConfig(
                provider=AIProvider.GEMINI,
                model_name="gemini-1.5-flash",
                strengths=["speed", "efficiency", "quick_analysis"],
                use_cases=["real_time_alerts", "simple_calculations", "data_validation"],
                cost_per_token=0.0002,
                max_tokens=4096,
                response_time_avg=0.8,
                accuracy_score=0.82,
                reliability_score=0.96
            ),
            "gpt4_turbo": AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-4-turbo",
                strengths=["complex_reasoning", "creative_solutions", "detailed_analysis"],
                use_cases=["strategic_planning", "complex_forecasting", "market_analysis"],
                cost_per_token=0.003,
                max_tokens=4096,
                response_time_avg=3.2,
                accuracy_score=0.91,
                reliability_score=0.89
            ),
            "gpt35_turbo": AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                strengths=["speed", "cost_efficiency", "general_purpose"],
                use_cases=["data_processing", "simple_insights", "content_generation"],
                cost_per_token=0.0005,
                max_tokens=4096,
                response_time_avg=1.1,
                accuracy_score=0.79,
                reliability_score=0.92
            ),
            "claude_opus": AIModelConfig(
                provider=AIProvider.CLAUDE,
                model_name="claude-3-opus",
                strengths=["analytical_depth", "ethical_reasoning", "nuanced_insights"],
                use_cases=["risk_analysis", "compliance_checking", "strategic_insights"],
                cost_per_token=0.015,
                max_tokens=4096,
                response_time_avg=4.1,
                accuracy_score=0.93,
                reliability_score=0.87
            ),
            "claude_sonnet": AIModelConfig(
                provider=AIProvider.CLAUDE,
                model_name="claude-3-sonnet",
                strengths=["balanced_performance", "reliability", "cost_effectiveness"],
                use_cases=["general_analysis", "reporting", "data_interpretation"],
                cost_per_token=0.003,
                max_tokens=4096,
                response_time_avg=2.8,
                accuracy_score=0.85,
                reliability_score=0.91
            )
        }

    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize advanced prompt templates for different tasks"""
        return {
            "financial_forecasting": """
You are an expert financial analyst with deep expertise in {domain}. 

CONTEXT:
{context}

HISTORICAL DATA:
{historical_data}

TASK: {task_description}

REQUIREMENTS:
- Provide detailed analysis with confidence intervals
- Include risk assessment and mitigation strategies
- Explain methodology and assumptions
- Offer actionable business recommendations

FORMAT: Structured JSON response with:
- forecast_data: detailed predictions
- confidence_metrics: accuracy indicators
- risk_analysis: potential issues and probabilities
- recommendations: specific actionable advice
- methodology: explanation of approach used

BUSINESS CONTEXT: {business_context}
""",
            
            "risk_assessment": """
You are a senior risk management specialist analyzing financial data.

CURRENT SITUATION:
{current_data}

HISTORICAL PATTERNS:
{historical_patterns}

TASK: {task_description}

FOCUS AREAS:
- Market risk exposure
- Operational risk factors
- Liquidity risk assessment
- Credit risk evaluation
- Regulatory compliance risks

DELIVERABLES:
- Risk scoring (1-10 scale)
- Probability assessments
- Impact analysis
- Mitigation strategies
- Monitoring recommendations

ANALYSIS CONTEXT: {analysis_context}
""",
            
            "business_insights": """
You are a strategic business consultant specializing in {industry}.

FINANCIAL METRICS:
{financial_metrics}

PERFORMANCE DATA:
{performance_data}

OBJECTIVE: {objective}

ANALYSIS FRAMEWORK:
- Performance vs benchmarks
- Trend identification
- Opportunity assessment
- Competitive positioning
- Growth potential

OUTPUT REQUIREMENTS:
- Executive summary
- Key findings with evidence
- Strategic recommendations
- Implementation roadmap
- Success metrics

BUSINESS GOALS: {business_goals}
""",
            
            "market_analysis": """
You are a market research analyst with expertise in {market_sector}.

MARKET DATA:
{market_data}

COMPANY DATA:
{company_data}

RESEARCH QUESTION: {research_question}

ANALYSIS SCOPE:
- Market positioning
- Competitive landscape
- Industry trends
- Growth opportunities
- Threat assessment

DELIVERABLES:
- Market overview
- Competitive analysis
- SWOT assessment
- Opportunity matrix
- Strategic recommendations

MARKET CONTEXT: {market_context}
"""
        }

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process AI request with intelligent model selection"""
        try:
            start_time = time.time()
            
            # Step 1: Intelligent model selection
            selected_model = await self._select_optimal_model(request)
            self.logger.info(f"Selected model: {selected_model} for task: {request.task_type}")
            
            # Step 2: Advanced prompt engineering
            enhanced_prompt = await self._enhance_prompt(request, selected_model)
            
            # Step 3: Execute AI request
            response_content = await self._execute_ai_request(
                enhanced_prompt, selected_model, request
            )
            
            # Step 4: Quality assessment
            quality_score = await self._assess_response_quality(
                response_content, request, selected_model
            )
            
            # Step 5: Cost calculation
            cost_incurred = self._calculate_cost(response_content, selected_model)
            
            processing_time = time.time() - start_time
            
            # Step 6: Update performance metrics
            await self._update_performance_metrics(
                selected_model, processing_time, quality_score, cost_incurred
            )
            
            # Create response
            ai_response = AIResponse(
                content=response_content,
                provider=self.models[selected_model].provider,
                model_used=selected_model,
                confidence_score=quality_score,
                processing_time=processing_time,
                cost_incurred=cost_incurred,
                quality_score=quality_score,
                metadata={
                    "task_type": request.task_type,
                    "prompt_tokens": len(enhanced_prompt.split()),
                    "response_tokens": len(response_content.split()),
                    "selection_reason": await self._get_selection_reason(selected_model, request)
                }
            )
            
            return ai_response
            
        except Exception as e:
            self.logger.error(f"AI request processing failed: {str(e)}")
            raise

    async def _select_optimal_model(self, request: AIRequest) -> str:
        """Intelligently select the optimal AI model for the request"""
        
        # Create cache key for routing decisions
        cache_key = self._create_cache_key(request)
        
        # Check cache first
        if cache_key in self.routing_cache:
            cached_selection = self.routing_cache[cache_key]
            if self._is_cache_valid(cached_selection):
                return cached_selection['model']
        
        # Score all available models
        model_scores = {}
        
        for model_id, config in self.models.items():
            score = await self._score_model_for_request(config, request)
            model_scores[model_id] = score
        
        # Select highest scoring model
        optimal_model = max(model_scores, key=model_scores.get)
        
        # Cache the decision
        self.routing_cache[cache_key] = {
            'model': optimal_model,
            'score': model_scores[optimal_model],
            'timestamp': datetime.now(),
            'reasoning': await self._generate_selection_reasoning(model_scores, request)
        }
        
        return optimal_model

    async def _score_model_for_request(self, config: AIModelConfig, request: AIRequest) -> float:
        """Score a model's suitability for a specific request"""
        score = 0.0
        
        # Task type alignment (40% weight)
        task_alignment = self._calculate_task_alignment(config, request.task_type)
        score += task_alignment * 0.4
        
        # Performance requirements (25% weight)
        performance_score = self._calculate_performance_score(config, request)
        score += performance_score * 0.25
        
        # Cost efficiency (20% weight)
        cost_score = self._calculate_cost_efficiency(config, request)
        score += cost_score * 0.2
        
        # Historical performance (15% weight)
        historical_score = self._get_historical_performance(config.model_name, request.task_type)
        score += historical_score * 0.15
        
        return score

    def _calculate_task_alignment(self, config: AIModelConfig, task_type: str) -> float:
        """Calculate how well a model aligns with the task type"""
        if task_type in config.use_cases:
            return 1.0
        
        # Check for related strengths
        task_keywords = task_type.split('_')
        strength_matches = 0
        
        for strength in config.strengths:
            for keyword in task_keywords:
                if keyword in strength:
                    strength_matches += 1
        
        return min(strength_matches / len(task_keywords), 1.0)

    def _calculate_performance_score(self, config: AIModelConfig, request: AIRequest) -> float:
        """Calculate performance score based on requirements"""
        score = 0.0
        
        # Response time requirement
        if request.max_response_time:
            if config.response_time_avg <= request.max_response_time:
                score += 0.4
            else:
                score += max(0, 0.4 * (1 - (config.response_time_avg - request.max_response_time) / request.max_response_time))
        
        # Quality threshold
        if config.accuracy_score >= request.quality_threshold:
            score += 0.3
        else:
            score += 0.3 * (config.accuracy_score / request.quality_threshold)
        
        # Reliability score
        score += 0.3 * config.reliability_score
        
        return score

    def _calculate_cost_efficiency(self, config: AIModelConfig, request: AIRequest) -> float:
        """Calculate cost efficiency score"""
        if not request.budget_limit:
            return 1.0  # No budget constraint
        
        # Estimate cost for typical request
        estimated_tokens = 1000  # Average estimation
        estimated_cost = config.cost_per_token * estimated_tokens
        
        if estimated_cost <= request.budget_limit:
            # Favor more cost-effective models within budget
            return 1.0 - (estimated_cost / request.budget_limit) * 0.5
        else:
            # Penalize over-budget models
            return max(0, 1.0 - (estimated_cost - request.budget_limit) / request.budget_limit)

    def _get_historical_performance(self, model_name: str, task_type: str) -> float:
        """Get historical performance score for model and task combination"""
        key = f"{model_name}_{task_type}"
        
        if key in self.performance_history:
            history = self.performance_history[key]
            # Calculate weighted average of recent performance
            recent_scores = history[-10:]  # Last 10 requests
            if recent_scores:
                return sum(recent_scores) / len(recent_scores)
        
        # Default to model's base accuracy if no history
        return self.models.get(model_name, AIModelConfig(
            AIProvider.GEMINI, "", [], [], 0, 0, 0, 0.8, 0.8
        )).accuracy_score

    async def _enhance_prompt(self, request: AIRequest, selected_model: str) -> str:
        """Enhance prompt using advanced prompt engineering techniques"""
        
        # Get base template
        template = self.prompt_templates.get(request.task_type, "{prompt}")
        
        # Apply model-specific optimizations
        model_config = self.models[selected_model]
        
        if model_config.provider == AIProvider.GEMINI:
            # Gemini optimizations
            enhanced_prompt = self._optimize_for_gemini(request.prompt, template, request.context)
        elif model_config.provider == AIProvider.OPENAI:
            # OpenAI optimizations
            enhanced_prompt = self._optimize_for_openai(request.prompt, template, request.context)
        elif model_config.provider == AIProvider.CLAUDE:
            # Claude optimizations
            enhanced_prompt = self._optimize_for_claude(request.prompt, template, request.context)
        else:
            enhanced_prompt = template.format(prompt=request.prompt, **request.context)
        
        return enhanced_prompt

    def _optimize_for_gemini(self, prompt: str, template: str, context: Dict[str, Any]) -> str:
        """Optimize prompt for Gemini models"""
        context_str = json.dumps(context, indent=2) if context else "No additional context"
        
        return f"""
SYSTEM: You are an expert financial AI assistant with deep analytical capabilities.

TASK: {prompt}

CONTEXT: {context_str}

INSTRUCTIONS:
- Provide comprehensive analysis with clear reasoning
- Include quantitative data when possible
- Offer specific, actionable recommendations
- Explain your methodology and assumptions
- Format response as structured JSON when appropriate

RESPONSE REQUIREMENTS:
- Be precise and data-driven
- Include confidence levels for predictions
- Highlight key risks and opportunities
- Provide implementation guidance
"""

    def _optimize_for_openai(self, prompt: str, template: str, context: Dict[str, Any]) -> str:
        """Optimize prompt for OpenAI models"""
        return f"""
You are a sophisticated financial analysis AI with expertise in data interpretation and strategic insights.

User Request: {prompt}

Context Information: {json.dumps(context, indent=2) if context else 'None provided'}

Please provide a comprehensive response that includes:
1. Detailed analysis of the provided information
2. Key insights and patterns identified
3. Specific recommendations with rationale
4. Potential risks and mitigation strategies
5. Confidence levels for your assessments

Format your response in clear, structured sections with supporting data.
"""

    def _optimize_for_claude(self, prompt: str, template: str, context: Dict[str, Any]) -> str:
        """Optimize prompt for Claude models"""
        return f"""
I need your expertise as a financial analyst to help with the following:

{prompt}

Additional Context:
{json.dumps(context, indent=2) if context else 'No additional context provided'}

Please approach this systematically:
- First, analyze the key factors and data points
- Consider multiple perspectives and scenarios
- Identify potential risks and opportunities
- Provide clear, actionable recommendations
- Explain your reasoning and methodology

I value thorough analysis with practical insights that can drive business decisions.
"""

    async def _execute_ai_request(self, prompt: str, model_id: str, request: AIRequest) -> str:
        """Execute the AI request using the selected model"""
        model_config = self.models[model_id]
        
        # For demonstration, we'll simulate responses based on model characteristics
        # In production, this would call actual AI APIs
        
        if model_config.provider == AIProvider.GEMINI:
            response = await self._simulate_gemini_response(prompt, model_config)
        elif model_config.provider == AIProvider.OPENAI:
            response = await self._simulate_openai_response(prompt, model_config)
        elif model_config.provider == AIProvider.CLAUDE:
            response = await self._simulate_claude_response(prompt, model_config)
        else:
            response = await self._simulate_generic_response(prompt, model_config)
        
        # Update usage statistics
        self.model_usage_stats[model_config.provider.value] += 1
        
        return response

    async def _simulate_gemini_response(self, prompt: str, config: AIModelConfig) -> str:
        """Simulate Gemini AI response"""
        await asyncio.sleep(config.response_time_avg * 0.1)  # Simulate processing time
        
        return json.dumps({
            "analysis": "Comprehensive financial analysis using Gemini's advanced reasoning capabilities",
            "insights": [
                "Strong revenue growth trajectory identified",
                "Cash flow optimization opportunities detected",
                "Risk factors properly assessed and mitigated"
            ],
            "recommendations": [
                "Implement automated forecasting system",
                "Optimize working capital management",
                "Establish proactive risk monitoring"
            ],
            "confidence_score": 0.87,
            "methodology": "Advanced time-series analysis with seasonal decomposition",
            "provider": "gemini",
            "model_capabilities": config.strengths
        }, indent=2)

    async def _simulate_openai_response(self, prompt: str, config: AIModelConfig) -> str:
        """Simulate OpenAI response"""
        await asyncio.sleep(config.response_time_avg * 0.1)
        
        return json.dumps({
            "executive_summary": "Strategic financial analysis with creative solutions approach",
            "detailed_analysis": {
                "performance_metrics": "Above industry average with strong fundamentals",
                "growth_opportunities": "Multiple expansion vectors identified",
                "risk_assessment": "Moderate risk profile with good mitigation strategies"
            },
            "strategic_recommendations": [
                "Diversify revenue streams for stability",
                "Invest in technology automation",
                "Expand market presence strategically"
            ],
            "implementation_roadmap": {
                "phase_1": "Infrastructure optimization (0-3 months)",
                "phase_2": "Market expansion (3-6 months)",
                "phase_3": "Technology scaling (6-12 months)"
            },
            "confidence_level": 0.91,
            "provider": "openai",
            "reasoning_depth": "high"
        }, indent=2)

    async def _simulate_claude_response(self, prompt: str, config: AIModelConfig) -> str:
        """Simulate Claude AI response"""
        await asyncio.sleep(config.response_time_avg * 0.1)
        
        return json.dumps({
            "thoughtful_analysis": "Comprehensive evaluation with ethical considerations",
            "key_findings": {
                "financial_health": "Strong fundamentals with sustainable growth patterns",
                "operational_efficiency": "Good performance with optimization potential",
                "market_position": "Competitive advantage in key segments"
            },
            "nuanced_insights": [
                "Balance between growth and sustainability is crucial",
                "Stakeholder interests align with long-term value creation",
                "Risk management should be proactive, not reactive"
            ],
            "ethical_considerations": [
                "Ensure fair customer treatment in pricing strategies",
                "Maintain transparency in financial reporting",
                "Consider environmental impact of growth initiatives"
            ],
            "balanced_recommendations": [
                "Pursue growth while maintaining financial discipline",
                "Invest in customer success for long-term relationships",
                "Build resilient systems for market volatility"
            ],
            "confidence_assessment": 0.93,
            "provider": "claude",
            "analytical_depth": "very_high"
        }, indent=2)

    async def _simulate_generic_response(self, prompt: str, config: AIModelConfig) -> str:
        """Simulate generic AI response"""
        await asyncio.sleep(config.response_time_avg * 0.1)
        
        return json.dumps({
            "response": "Standard AI analysis completed",
            "summary": "Basic financial insights generated",
            "recommendations": ["Continue monitoring", "Review monthly"],
            "confidence": config.accuracy_score,
            "provider": config.provider.value
        }, indent=2)

    async def _assess_response_quality(self, response: str, request: AIRequest, model_id: str) -> float:
        """Assess the quality of the AI response"""
        quality_score = 0.0
        
        try:
            # Parse response if JSON
            parsed_response = json.loads(response)
            
            # Check for completeness (30% weight)
            completeness_score = self._assess_completeness(parsed_response, request.task_type)
            quality_score += completeness_score * 0.3
            
            # Check for actionability (25% weight)
            actionability_score = self._assess_actionability(parsed_response)
            quality_score += actionability_score * 0.25
            
            # Check for specificity (25% weight)
            specificity_score = self._assess_specificity(parsed_response)
            quality_score += specificity_score * 0.25
            
            # Check for confidence indicators (20% weight)
            confidence_score = self._assess_confidence_indicators(parsed_response)
            quality_score += confidence_score * 0.2
            
        except json.JSONDecodeError:
            # Non-JSON response, use basic text analysis
            quality_score = self._assess_text_quality(response, request.task_type)
        
        # Cap at model's maximum accuracy
        model_max_accuracy = self.models[model_id].accuracy_score
        return min(quality_score, model_max_accuracy)

    def _assess_completeness(self, response: Dict[str, Any], task_type: str) -> float:
        """Assess response completeness"""
        required_elements = {
            "financial_forecasting": ["analysis", "recommendations", "confidence_score"],
            "risk_assessment": ["risk_analysis", "mitigation_strategies", "probability"],
            "business_insights": ["insights", "recommendations", "implementation"],
            "market_analysis": ["market_overview", "competitive_analysis", "opportunities"]
        }
        
        required = required_elements.get(task_type, ["analysis", "recommendations"])
        found_elements = sum(1 for element in required if element in str(response).lower())
        
        return found_elements / len(required)

    def _assess_actionability(self, response: Dict[str, Any]) -> float:
        """Assess how actionable the recommendations are"""
        actionable_keywords = [
            "implement", "establish", "create", "develop", "optimize",
            "increase", "reduce", "monitor", "review", "invest"
        ]
        
        text = str(response).lower()
        found_keywords = sum(1 for keyword in actionable_keywords if keyword in text)
        
        return min(found_keywords / 5, 1.0)  # Normalize to 0-1

    def _assess_specificity(self, response: Dict[str, Any]) -> float:
        """Assess how specific the response is"""
        specific_indicators = [
            "percent", "%", "days", "months", "dollar", "revenue",
            "cost", "roi", "margin", "ratio", "score"
        ]
        
        text = str(response).lower()
        found_indicators = sum(1 for indicator in specific_indicators if indicator in text)
        
        return min(found_indicators / 4, 1.0)

    def _assess_confidence_indicators(self, response: Dict[str, Any]) -> float:
        """Assess presence of confidence indicators"""
        confidence_keys = [
            "confidence", "probability", "likelihood", "certainty",
            "score", "level", "assessment"
        ]
        
        text = str(response).lower()
        found_confidence = sum(1 for key in confidence_keys if key in text)
        
        return min(found_confidence / 2, 1.0)

    def _assess_text_quality(self, response: str, task_type: str) -> float:
        """Basic text quality assessment for non-JSON responses"""
        # Length check
        length_score = min(len(response) / 500, 1.0)  # Prefer longer, detailed responses
        
        # Keyword relevance
        task_keywords = task_type.split('_')
        keyword_score = sum(1 for keyword in task_keywords if keyword in response.lower()) / len(task_keywords)
        
        return (length_score + keyword_score) / 2

    def _calculate_cost(self, response: str, model_id: str) -> float:
        """Calculate the cost of the AI request"""
        model_config = self.models[model_id]
        
        # Estimate tokens (rough approximation)
        response_tokens = len(response.split())
        
        return response_tokens * model_config.cost_per_token

    async def _update_performance_metrics(self, model_id: str, processing_time: float, 
                                        quality_score: float, cost: float):
        """Update performance metrics for the model"""
        key = f"{model_id}_overall"
        
        if key not in self.performance_history:
            self.performance_history[key] = []
        
        # Store performance data
        self.performance_history[key].append({
            'timestamp': datetime.now(),
            'processing_time': processing_time,
            'quality_score': quality_score,
            'cost': cost
        })
        
        # Keep only recent history (last 100 requests)
        if len(self.performance_history[key]) > 100:
            self.performance_history[key] = self.performance_history[key][-100:]

    async def _get_selection_reason(self, model_id: str, request: AIRequest) -> str:
        """Get human-readable reason for model selection"""
        config = self.models[model_id]
        
        reasons = []
        
        if request.task_type in config.use_cases:
            reasons.append(f"Specialized for {request.task_type}")
        
        if config.response_time_avg <= request.max_response_time:
            reasons.append("Meets response time requirements")
        
        if config.accuracy_score >= request.quality_threshold:
            reasons.append("Exceeds quality threshold")
        
        reasons.append(f"Strong in: {', '.join(config.strengths[:2])}")
        
        return "; ".join(reasons)

    def _create_cache_key(self, request: AIRequest) -> str:
        """Create cache key for routing decisions"""
        key_data = f"{request.task_type}_{request.priority}_{request.max_response_time}_{request.quality_threshold}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_cache_valid(self, cached_selection: Dict[str, Any]) -> bool:
        """Check if cached selection is still valid"""
        cache_age = datetime.now() - cached_selection['timestamp']
        return cache_age < timedelta(hours=1)  # Cache valid for 1 hour

    async def _generate_selection_reasoning(self, model_scores: Dict[str, float], 
                                          request: AIRequest) -> str:
        """Generate reasoning for model selection"""
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        
        reasoning = f"Selected {sorted_models[0][0]} (score: {sorted_models[0][1]:.2f}) "
        reasoning += f"over alternatives: "
        
        for model, score in sorted_models[1:3]:  # Show top 3
            reasoning += f"{model} ({score:.2f}), "
        
        return reasoning.rstrip(", ")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "available_models": len(self.models),
            "model_usage_stats": self.model_usage_stats,
            "performance_history_size": len(self.performance_history),
            "cache_size": len(self.routing_cache),
            "system_health": "operational",
            "last_updated": datetime.now().isoformat()
        }

    async def get_model_comparison(self) -> Dict[str, Any]:
        """Get detailed model comparison metrics"""
        comparison = {}
        
        for model_id, config in self.models.items():
            comparison[model_id] = {
                "provider": config.provider.value,
                "strengths": config.strengths,
                "use_cases": config.use_cases,
                "cost_per_token": config.cost_per_token,
                "avg_response_time": config.response_time_avg,
                "accuracy_score": config.accuracy_score,
                "reliability_score": config.reliability_score,
                "usage_count": self.model_usage_stats.get(config.provider.value, 0)
            }
        
        return comparison

# Initialize the advanced AI orchestrator
advanced_ai_orchestrator = AdvancedAIOrchestrator()