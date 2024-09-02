import os
import json
import gradio as gr
from config import Config
from github_client import GitHubClient
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from logger import LOG
from datetime import datetime

config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file, config.subscriptions_custom_file)

gui_repo_list = []

def add_repo(repo_name, selected_repos):
    if repo_name and repo_name not in gui_repo_list:
        gui_repo_list.append(repo_name)
    return gr.update(choices=gui_repo_list, value=selected_repos)

def remove_repo(repo_name, selected_repos):
    if repo_name in gui_repo_list:
        gui_repo_list.remove(repo_name)
    selected_repos = [repo for repo in selected_repos if repo in gui_repo_list]
    return gr.update(choices=gui_repo_list, value=selected_repos)

def bulk_import_repos(file):
    global gui_repo_list
    try:
        with open(file.name, "r") as f:
            new_repos = json.load(f)
        gui_repo_list = list(set(gui_repo_list + new_repos))
    except Exception as e:
        return f"导入失败: {str(e)}", gr.update(choices=gui_repo_list, value=[])
    return f"成功导入{len(new_repos)}个repo", gr.update(choices=gui_repo_list, value=[])

def query_repos_daily(selected_repo):
    result = {}
    # subscription_manager.reset_subscription([selected_repo])  # 重置订阅，只对选中的单个仓库进行
    try:
        raw_file_path = github_client.export_daily_progress(selected_repo)
        report, report_file_path = report_generator.generate_daily_report_test_gradio(raw_file_path)
        result[selected_repo] = report
    except Exception as e:
        result[selected_repo] = f"查询失败: {str(e)}"
    return result

def query_repos(selected_repo, end_time_input, days):
    result = {}
    # subscription_manager.reset_subscription([selected_repo])  # 重置订阅，只对选中的单个仓库进行
    if end_time_input:
        try:
            end_time = datetime.strptime(end_time_input, '%Y-%m-%d').date()
        except ValueError:
            result[selected_repo] = f"查询失败: 输入时间格式无效，预期2024-08-30"
            return result
    else:
        end_time = datetime.now().date() # 默认使用当前时间
    print(f"查询 {selected_repo} 截止 {end_time} 的进展")
    try:
        raw_file_path = github_client.export_progress_by_date_range(selected_repo, end_time, days)  # 导出原始数据文件路径
        report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径
        result[selected_repo] = report
    except Exception as e:
        result[selected_repo] = f"查询失败: {str(e)}"
    return result

def download_markdown(markdown_content, repo_name):
    # 处理文件名，仅保留仓库名称部分
    file_name = repo_name.split('/')[-1] + ".md"
    file_path = os.path.join(os.getcwd(), file_name)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return file_path
    except Exception as e:
        LOG.error(f"Error saving markdown: {str(e)}")
        return None

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            repo_name = gr.Textbox(label="GitHub Repo", placeholder="输入GitHub Repo举例：ollama/ollama")
            with gr.Row():
                add_btn = gr.Button("Repo添加")
                remove_btn = gr.Button("Repo删除")
            file_input = gr.File(label="批量Repo导入", file_types=["json"])
            repo_radio = gr.Radio(label="【必选】选择订阅的Repos", choices=gui_repo_list)
            end_time_input = gr.Textbox(label="【可选】查询截止时间，默认当前时间", placeholder="例如：2024-01-01")
            day_slider = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="【可选】报告周期，默认2天", info="生成项目过去一段时间进展，单位：天")
            # 滑动条选择报告的时间范围
            query_btn = gr.Button("查询订阅项目进展")
            import_status = gr.Textbox(label="执行状态", interactive=False)
        
        with gr.Column(scale=2) as output_section:
            result_markdown = gr.Markdown(value="")
            download_button = gr.Button("下载为Markdown", visible=False)
            downloaded_file = gr.File(label="下载的Markdown文件", visible=False)  # Initially hidden

    add_btn.click(add_repo, inputs=[repo_name, repo_radio], outputs=[repo_radio])
    remove_btn.click(remove_repo, inputs=[repo_name, repo_radio], outputs=[repo_radio])
    file_input.upload(bulk_import_repos, inputs=file_input, outputs=[import_status, repo_radio])

    def display_result(selected_repo, end_time_input, days):
        repo_outputs = query_repos(selected_repo, end_time_input, days)
        for repo, content in repo_outputs.items():
            result_markdown.value = content
            download_button.visible = True
        return result_markdown.value, gr.update(visible=True)

    query_btn.click(display_result, inputs=[repo_radio,end_time_input,day_slider], outputs=[result_markdown, download_button])

    def handle_download(markdown_content, selected_repo):
        file_path = download_markdown(markdown_content, selected_repo)
        return gr.update(value=file_path, visible=True)

    download_button.click(handle_download, inputs=[result_markdown, repo_radio], outputs=downloaded_file)

def main():
    demo.launch(share=True)

if __name__ == "__main__":
    main()
