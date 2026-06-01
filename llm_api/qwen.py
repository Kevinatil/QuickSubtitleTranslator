from openai import OpenAI
from .base import LLMAPI
from .utils import get_llm_config

config = get_llm_config("qwen")

class LLMAPI_QWEN(LLMAPI):
    def __init__(self):
        super().__init__()

        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["llm_url"]
        )

        self.model_name = "qwen3.7-max"

        self.input_price = 0.012
        self.output_price = 0.036
    
    def get_response(self, messages, thinking = True):
        '''
        Parameters
        ----------
        messages: List[Dict[str, str]]
        
        Returns
        -------
        Dict
            {'thinking': '', 'answer': ''}
        '''
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            extra_body={"enable_thinking": thinking},
            stream=False
        )
        return {
            'thinking': response.choices[0].message.reasoning_content,
            'answer': response.choices[0].message.content,
            'token_num': {
                'input': response.usage.prompt_tokens,
                'output': response.usage.completion_tokens
            }
        }


if __name__ == "__main__":
    model = LLMAPI_QWEN()
    model.get_single_response('你好')