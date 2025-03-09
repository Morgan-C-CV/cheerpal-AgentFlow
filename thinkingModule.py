import os
import dashscope

def get_model_response(user_input, system_prompt='You are a helpful assistant.'):
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_input}
    ]
    response = dashscope.Generation.call(
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        model="qwen-plus",
        messages=messages,
        result_format='message'
    )
    return response

if __name__ == '__main__':
    user_input = '你是谁？'
    response = get_model_response(user_input)
    print(response)