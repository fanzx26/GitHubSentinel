import os
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self, model="gpt-3.5-turbo"):
        # 创建一个OpenAI客户端实例
        self.client = OpenAI(
                base_url="https://api.gptsapi.net/v1",
                api_key=os.getenv("OPENAI_KEY")
            )
        # 确定使用的模型版本
        self.model = model
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 构建一个用于生成报告的提示文本，要求生成的报告包含新增功能、主要改进和问题修复
        # prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报，至少包含：1）新增功能；2）主要改进；3）修复问题；:\n\n{markdown_content}"
        system_prompt = f"你是一个善于总结GitHub开源项目进展的中文智能助手。\n\n你将收到由issues和pull requests组成的详细进展信息，请你分析和解读后，归纳总结成一份中文简报，涵盖以下3类内容：1.新增功能；2.修复问题；3.优化改进。\n\n简报内容严格保持markdown格式，务必使用中文总结。每个类别的进展逐条展示，每条进展最后保留issue或PR的number号。\n\n要求整理和合并相似的issue和pull request，相同的number号仅需要在一个类别里。\n\n"
        user_prompt = f"{markdown_content}"
        
        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(system_prompt)
                f.write("\n\n")
                f.write(user_prompt)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model=self.model,  # 指定使用的模型版本
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}  # 提交用户角色的消息
                ]
            )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise
