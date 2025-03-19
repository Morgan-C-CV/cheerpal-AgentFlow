import os
import dashscope

def get_model_response(user_input, messages, system_prompt='You are a helpful assistant.'):
    response = dashscope.Generation.call(
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        model="qwen-plus",
        messages=messages,
        result_format='message'
    )
    res = response['output']['choices'][0]['message']['content']
    messages.append({'role': 'assistant', 'content': res})
    return res
