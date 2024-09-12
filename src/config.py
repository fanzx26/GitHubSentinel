import json
import os

class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        # 尝试从环境变量获取配置或使用 config.json 文件中的配置作为回退
        with open('config.json', 'r') as f:
            config = json.load(f)
            
            # 使用环境变量或配置文件的 GitHub Token
            self.github_token = os.getenv('GITHUB_TOKEN', config.get('github_token'))

            # 初始化电子邮件设置
            self.email = config.get('email', {})
            # 使用环境变量或配置文件中的电子邮件密码
            self.email['password'] = os.getenv('EMAIL_PASSWORD', self.email.get('password', ''))

            self.llm_config = config.get('llm', {})
            self.llm_type = self.llm_config.get("llm_type", "ollama")
            self.openai_model_name = self.llm_config.get("openai_model_name", "ollama")
            self.openai_api_url = self.llm_config.get("openai_api_url", "https://api.gptsapi.net/v1")
            self.ollama_model_name = self.llm_config.get("ollama_model_name", "llama3.1")
            self.ollama_api_url = self.llm_config.get("ollama_api_url", "http://localhost:6006/api/chat")

            self.prompts_file = config.get('prompts', {})

            self.subscriptions_file = config.get('subscriptions_file')
            # 默认每天执行
            self.freq_days = config.get('github_progress_frequency_days', 1)
            # 默认早上8点更新 (操作系统默认时区是 UTC +0，08点刚好对应北京时间凌晨12点)
            self.exec_time = config.get('github_progress_execution_time', "08:00") 

            # 默认每天执行
            self.hacker_freq_days = config.get('hacker_progress_frequency_days', 1)
            self.hacker_freq_hours  = config.get('hacker_progress_frequency_hours', 6)
            # 默认早上8点更新 (操作系统默认时区是 UTC +0，08点刚好对应北京时间凌晨12点)
            self.hacker_exec_time = config.get('hacker_progress_execution_time', "08:00") 
