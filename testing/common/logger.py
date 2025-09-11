"""
测试日志记录系统

统一的测试日志格式和存储机制，支持结构化数据和自动分析。
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class TestLog:
    """单个测试日志记录"""
    timestamp: str
    module: str
    test_case: str
    user_input: str
    system_output: str
    execution_time: float
    success: bool
    error_message: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

@dataclass
class TestSession:
    """测试会话"""
    session_id: str
    module: str
    start_time: str
    end_time: str = ""
    test_logs: List[TestLog] = None
    summary: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.test_logs is None:
            self.test_logs = []
        if self.summary is None:
            self.summary = {}

class TestLogger:
    """测试日志记录器"""
    
    def __init__(self):
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
    
    def create_session(self, module: str) -> TestSession:
        """创建新的测试会话"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{module}_{timestamp}"
        
        session = TestSession(
            session_id=session_id,
            module=module,
            start_time=datetime.now().isoformat()
        )
        
        # 创建会话目录
        session_dir = self.logs_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        # 保存会话信息
        self._save_session_info(session)
        
        return session
    
    def log_test(self, session: TestSession, test_case: str, user_input: str,
                 system_output: str, execution_time: float, success: bool,
                 error_message: str = "", metadata: Dict[str, Any] = None):
        """记录单个测试日志"""
        
        test_log = TestLog(
            timestamp=datetime.now().isoformat(),
            module=session.module,
            test_case=test_case,
            user_input=user_input,
            system_output=system_output,
            execution_time=execution_time,
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        session.test_logs.append(test_log)
        
        # 立即写入日志文件
        self._append_log_to_file(session, test_log)
    
    def end_session(self, session: TestSession):
        """结束测试会话"""
        session.end_time = datetime.now().isoformat()
        
        # 计算摘要统计
        total_tests = len(session.test_logs)
        success_count = sum(1 for log in session.test_logs if log.success)
        avg_time = sum(log.execution_time for log in session.test_logs) / total_tests if total_tests > 0 else 0
        
        session.summary = {
            "total_tests": total_tests,
            "success_count": success_count,
            "failure_count": total_tests - success_count,
            "success_rate": success_count / total_tests if total_tests > 0 else 0,
            "average_execution_time": avg_time,
            "total_duration": self._calculate_duration(session.start_time, session.end_time)
        }
        
        # 更新会话信息文件
        self._save_session_info(session)
    
    def generate_report(self, session: TestSession) -> Optional[Path]:
        """生成测试报告"""
        try:
            session_dir = self.logs_dir / session.session_id
            report_file = session_dir / "test_report.md"
            
            report_content = self._generate_markdown_report(session)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return report_file
            
        except Exception as e:
            print(f"❌ 生成报告失败: {str(e)}")
            return None
    
    def _save_session_info(self, session: TestSession):
        """保存会话信息到JSON文件"""
        session_dir = self.logs_dir / session.session_id
        session_file = session_dir / "session_info.json"
        
        session_data = {
            "session_id": session.session_id,
            "module": session.module,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "summary": session.summary,
            "total_logs": len(session.test_logs)
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    def _append_log_to_file(self, session: TestSession, test_log: TestLog):
        """追加日志到JSONL文件"""
        session_dir = self.logs_dir / session.session_id
        log_file = session_dir / f"{session.module}_tests.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(test_log.to_dict(), f, ensure_ascii=False)
            f.write('\n')
    
    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """计算持续时间（秒）"""
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return (end - start).total_seconds()
        except:
            return 0.0
    
    def _generate_markdown_report(self, session: TestSession) -> str:
        """生成Markdown格式的测试报告"""
        report = f"""# {session.module} 测试报告

## 测试会话信息
- **会话ID**: {session.session_id}
- **测试模块**: {session.module}
- **开始时间**: {session.start_time}
- **结束时间**: {session.end_time}
- **总耗时**: {session.summary.get('total_duration', 0):.2f}秒

## 测试统计
- **总测试数**: {session.summary.get('total_tests', 0)}
- **成功次数**: {session.summary.get('success_count', 0)}
- **失败次数**: {session.summary.get('failure_count', 0)}
- **成功率**: {session.summary.get('success_rate', 0):.1%}
- **平均响应时间**: {session.summary.get('average_execution_time', 0):.2f}秒

## 详细测试记录

"""
        
        for i, log in enumerate(session.test_logs, 1):
            status = "✅ 成功" if log.success else "❌ 失败"
            report += f"""### 测试用例 {i}: {log.test_case}

**状态**: {status}  
**用户输入**: `{log.user_input}`  
**系统输出**: {log.system_output}  
**执行时间**: {log.execution_time:.2f}秒  
**时间戳**: {log.timestamp}

"""
            
            if log.error_message:
                report += f"**错误信息**: {log.error_message}\n\n"
            
            if log.metadata:
                report += "**元数据**:\n"
                for key, value in log.metadata.items():
                    report += f"- {key}: {value}\n"
                report += "\n"
        
        return report