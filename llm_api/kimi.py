from openai import OpenAI
from .base import LLMAPI
from .utils import get_llm_config

config = get_llm_config("kimi")

class LLMAPI_KIMI(LLMAPI):
    def __init__(self, model_name = 'k2.6'):
        super().__init__()

        print('use model: {}'.format(model_name))

        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["llm_url"]
        )

        self.model_name = "kimi-{}".format(model_name)

        if model_name == 'k2.5':
            self.input_price = 0.004
            self.output_price = 0.021
        elif model_name == 'k2.6':
            self.input_price = 0.0065
            self.output_price = 0.027
    
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
        if thinking:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                extra_body={
                    "thinking": {"type": "disabled"}
                }
            )
        return {
            'thinking': response.choices[0].message.reasoning_content if thinking else '',
            'answer': response.choices[0].message.content,
            'token_num': {
                'input': response.usage.prompt_tokens,
                'output': response.usage.completion_tokens
            }
        }


if __name__ == "__main__":
    model = LLMAPI_KIMI()
    print(model.get_single_response('你好'))

