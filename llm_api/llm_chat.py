#coding: utf-8
class LLMChat:
    def __init__(self, use_model):
        if use_model == 'kimi':
            from .kimi import LLMAPI_KIMI
            self.client = LLMAPI_KIMI()
        else:
            raise NotImplementedError

        self.input_token_num = 0
        self.output_token_num = 0

    def get_response(self, content, backoff=False, thinking=True):

        response = self.client.get_single_response(content, backoff=backoff, thinking=thinking)

        self.input_token_num += response['token_num']['input']
        self.output_token_num += response['token_num']['output']

        return response

    def get_price(self):
        return self.input_token_num / 1000.0 * self.client.input_price + self.output_token_num / 1000.0 * self.client.output_price

