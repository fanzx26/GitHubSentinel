import os
import json
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块
import requests

class LLM:
    def __init__(self, llm_config):
        self.llm_config = llm_config
        # 创建一个OpenAI客户端实例
        self.client = OpenAI(
                base_url=self.llm_config.openai_api_url,
                api_key=os.getenv("OPENAI_KEY")
            )
        # if self.llm_config.llm_type == "openai":
        #     # 从TXT文件加载提示信息
        #     with open("prompts/github_daily_report_openai_prompt.txt", "r", encoding='utf-8') as file:
        #         self.github_system_prompt = file.read()
        #     # 从TXT文件加载提示信息
        #     with open("prompts/hacker_news_report_openai_prompt.txt", "r", encoding='utf-8') as file:
        #         self.hacker_system_prompt = file.read()
        # else:
        #     # 从TXT文件加载提示信息
        #     with open("prompts/github_daily_report_ollama_prompt.txt", "r", encoding='utf-8') as file:
        #         self.github_system_prompt = file.read()
        #     # 从TXT文件加载提示信息
        #     with open("prompts/hacker_news_report_ollama_prompt.txt", "r", encoding='utf-8') as file:
        #         self.hacker_system_prompt = file.read()

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 使用从TXT文件加载的提示信息
        messages = [
            {"role": "system", "content": self.github_system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt已保存到 daily_progress/prompt.txt")

            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("使用 GPT 模型开始生成报告。")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 指定使用的模型版本
                messages=messages
            )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def _generate_openai_report(self, messages):
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model=self.llm_config.openai_model_name,  # 指定使用的模型版本
                messages=messages
            )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def _generate_ollama_report(self, messages):
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": self.llm_config.ollama_model_name,
            "messages": messages,
            "stream": False
        }
        response = requests.post(self.llm_config.ollama_api_url, 
                                 headers=headers, 
                                 data=json.dumps(data))
        response_data = response.json()
        print(f"response_data={response_data}")

    def generate_report(self, markdown_content, dry_run=False):
        # 使用从TXT文件加载的提示信息
        if self.llm_config.llm_type == "openai":
            messages = [
                {"role": "system", "content": self.github_system_prompt},
                {"role": "user", "content": markdown_content},
            ]
        else:
            messages = [
                {"role": "system", "content": self.hacker_system_prompt},
                {"role": "user", "content": markdown_content},
            ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt已保存到 daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("使用 GPT 模型开始生成报告。")
        
        if self.llm_config.llm_type == "openai":
            return self._generate_openai_report(messages)
        else:
            return self._generate_ollama_report(messages)

        