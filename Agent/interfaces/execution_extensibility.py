"""
执行引擎扩展性接口

为执行引擎提供扩展接口，支持后续重构和功能增强，
同时保持向后兼容性。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Type
from .data_structures import Intent, ExecutionResult
from .execution_interfaces import GameFunction, ExecutionEngine
from .state_management_interfaces import StateManagerRegistry, StateTransactionManager


class ExecutionHook(ABC):
    """执行钩子接口"""
    
    @abstractmethod
    def before_execution(self, intent: Intent, game_state: Any) -> Optional[Dict[str, Any]]:
        """执行前钩子"""
        pass
    
    @abstractmethod
    def after_execution(self, intent: Intent, result: ExecutionResult, game_state: Any) -> Optional[ExecutionResult]:
        """执行后钩子"""
        pass
    
    @abstractmethod
    def on_execution_error(self, intent: Intent, error: Exception, game_state: Any) -> Optional[ExecutionResult]:
        """执行错误钩子"""
        pass


class FunctionEnhancer(ABC):
    """Function增强器接口"""
    
    @abstractmethod
    def can_enhance(self, function: GameFunction) -> bool:
        """检查是否可以增强指定Function"""
        pass
    
    @abstractmethod
    def enhance_function(self, function: GameFunction) -> GameFunction:
        """增强Function功能"""
        pass
    
    @abstractmethod
    def get_enhancement_metadata(self) -> Dict[str, Any]:
        """获取增强信息"""
        pass


class ExecutionContextProvider(ABC):
    """执行上下文提供者接口"""
    
    @abstractmethod
    def provide_context(self, intent: Intent, game_state: Any) -> Dict[str, Any]:
        """提供执行上下文"""
        pass
    
    @abstractmethod
    def cleanup_context(self, context: Dict[str, Any]):
        """清理执行上下文"""
        pass


class ExecutionEngineExtensions:
    """执行引擎扩展管理器"""
    
    def __init__(self):
        self.hooks: List[ExecutionHook] = []
        self.enhancers: List[FunctionEnhancer] = []
        self.context_providers: List[ExecutionContextProvider] = []
        self.custom_validators: List[Callable[[Intent], bool]] = []
        
    def add_hook(self, hook: ExecutionHook):
        """添加执行钩子"""
        self.hooks.append(hook)
    
    def add_enhancer(self, enhancer: FunctionEnhancer):
        """添加Function增强器"""
        self.enhancers.append(enhancer)
    
    def add_context_provider(self, provider: ExecutionContextProvider):
        """添加上下文提供者"""
        self.context_providers.append(provider)
    
    def add_custom_validator(self, validator: Callable[[Intent], bool]):
        """添加自定义验证器"""
        self.custom_validators.append(validator)
    
    def apply_before_hooks(self, intent: Intent, game_state: Any) -> Dict[str, Any]:
        """应用执行前钩子"""
        metadata = {}
        for hook in self.hooks:
            try:
                hook_data = hook.before_execution(intent, game_state)
                if hook_data:
                    metadata.update(hook_data)
            except Exception as e:
                print(f"Warning: Hook {hook.__class__.__name__} failed: {str(e)}")
        return metadata
    
    def apply_after_hooks(self, intent: Intent, result: ExecutionResult, game_state: Any) -> ExecutionResult:
        """应用执行后钩子"""
        current_result = result
        for hook in self.hooks:
            try:
                modified_result = hook.after_execution(intent, current_result, game_state)
                if modified_result:
                    current_result = modified_result
            except Exception as e:
                print(f"Warning: Hook {hook.__class__.__name__} failed: {str(e)}")
        return current_result
    
    def enhance_function(self, function: GameFunction) -> GameFunction:
        """增强Function"""
        enhanced_function = function
        for enhancer in self.enhancers:
            if enhancer.can_enhance(enhanced_function):
                enhanced_function = enhancer.enhance_function(enhanced_function)
        return enhanced_function
    
    def gather_context(self, intent: Intent, game_state: Any) -> Dict[str, Any]:
        """收集执行上下文"""
        context = {}
        for provider in self.context_providers:
            try:
                provider_context = provider.provide_context(intent, game_state)
                context.update(provider_context)
            except Exception as e:
                print(f"Warning: Context provider {provider.__class__.__name__} failed: {str(e)}")
        return context
    
    def validate_intent(self, intent: Intent) -> bool:
        """验证意图"""
        for validator in self.custom_validators:
            try:
                if not validator(intent):
                    return False
            except Exception as e:
                print(f"Warning: Validator failed: {str(e)}")
                return False
        return True


class StateManagerIntegration:
    """状态管理器集成接口"""
    
    def __init__(self, state_registry: StateManagerRegistry):
        self.state_registry = state_registry
        self.transaction_manager = StateTransactionManager(state_registry)
    
    def create_transaction_context(self, intent: Intent, game_state: Any) -> StateTransactionManager:
        """为执行创建状态事务上下文"""
        self.transaction_manager.clear()
        return self.transaction_manager
    
    def can_integrate_with_execution_engine(self, engine: ExecutionEngine) -> bool:
        """检查是否可以与执行引擎集成"""
        return hasattr(engine, 'process') and hasattr(engine, 'registry')
    
    def wrap_function_with_state_management(self, function: GameFunction) -> GameFunction:
        """用状态管理包装Function"""
        # 这里可以在未来实现状态管理的包装逻辑
        return function


# 预定义的一些有用的扩展
class LoggingHook(ExecutionHook):
    """日志记录钩子"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
    
    def before_execution(self, intent: Intent, game_state: Any) -> Optional[Dict[str, Any]]:
        if self.enabled:
            print(f"[DEBUG] Executing intent: {intent.category} - {intent.action}")
        return {"logging_enabled": self.enabled}
    
    def after_execution(self, intent: Intent, result: ExecutionResult, game_state: Any) -> Optional[ExecutionResult]:
        if self.enabled:
            print(f"[DEBUG] Execution result: success={result.success}, changes={len(result.state_changes)}")
        return None
    
    def on_execution_error(self, intent: Intent, error: Exception, game_state: Any) -> Optional[ExecutionResult]:
        if self.enabled:
            print(f"[ERROR] Execution failed: {str(error)}")
        return None


class PerformanceContextProvider(ExecutionContextProvider):
    """性能监控上下文提供者"""
    
    def provide_context(self, intent: Intent, game_state: Any) -> Dict[str, Any]:
        import time
        return {
            "performance": {
                "start_time": time.time(),
                "intent_category": intent.category,
                "has_target": bool(intent.target)
            }
        }
    
    def cleanup_context(self, context: Dict[str, Any]):
        if "performance" in context:
            import time
            elapsed = time.time() - context["performance"]["start_time"]
            print(f"[PERF] Execution took {elapsed:.3f}s for {context['performance']['intent_category']}")


# 工厂函数
def create_default_extensions() -> ExecutionEngineExtensions:
    """创建默认的执行引擎扩展"""
    extensions = ExecutionEngineExtensions()
    
    # 添加默认的钩子和提供者
    extensions.add_hook(LoggingHook(enabled=False))  # 默认关闭，可配置开启
    extensions.add_context_provider(PerformanceContextProvider())
    
    return extensions


def create_state_aware_extensions(state_registry: StateManagerRegistry) -> ExecutionEngineExtensions:
    """创建状态感知的执行引擎扩展"""
    extensions = create_default_extensions()
    
    # 可以在这里添加状态管理相关的扩展
    # 未来实现状态管理集成时会用到
    
    return extensions