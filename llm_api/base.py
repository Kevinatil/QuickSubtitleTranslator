import random
import time


class LLMAPI:
    def __init__(self):
        pass

    def get_response(self, messages, thinking = True):
        pass

    def get_response_with_exponential_backoff(
            self,
            messages,
            thinking: bool = True,
            max_retries: int = 3,
            base_delay: float = 2.0,
            max_delay: float = 2.0 * 10,
            exponential_base: float = 2.0,
            jitter: bool = True):
        """
        带指数退避的重试调用
        
        Parameters
        ----------

        max_retries: int, default 3
            最大重试次数（不包括首次调用）
        base_delay: float, default 60
            初始延迟时间（秒）
        max_delay: float, default 600
            最大延迟时间（秒）
        exponential_base: float, default 2.0
            指数基数（默认 2，即 1, 2, 4, 8...）
        jitter: bool, default True
            是否添加随机抖动（避免惊群效应）
        """
        
        for attempt in range(max_retries + 1):
            
            try:
                return self.get_response(messages, thinking)
                
            except Exception as e:
                
                if attempt >= max_retries:
                    print("达到最大重试次数")
                    raise RuntimeError("大模型调用达到最大重复次数")
                
                # 计算下一次延迟
                delay = min(
                    base_delay * (exponential_base ** attempt),
                    max_delay
                )
                
                # 添加随机抖动 (±20%)
                if jitter:
                    delay = delay * (0.8 + random.random() * 0.4)
                
                print('第{}次调用大模型失败，错误原因：{}，{:.2f}秒后重试'.format(attempt+1, e, delay))
                time.sleep(delay)

    def get_single_response(self, prompt, backoff=False, thinking=True):
        message = [{'role': 'user', 'content': prompt}]
        if backoff:
            return self.get_response_with_exponential_backoff(message, thinking)
        else:
            return self.get_response(message, thinking)

