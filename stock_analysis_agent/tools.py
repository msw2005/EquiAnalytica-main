import os
import markdown
from numpy import str_
from weasyprint import HTML, CSS
from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import time
import schedule

from .config import *





def get_current_time() -> dict:
    """Returns the current date and time.

    Args:

    Returns:
        dict: current date and time.
    """

    now = datetime.now()
    report = f'The current time is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    return {"current date and time": report}



google_search_agent = LlmAgent(
    model=GEMINI_LIST[0],
    name='google_search_agent',
    instruction="""
    You're a spealist in Google Search who take a search query and return the results.
    """,
    tools=[google_search]
)



def combine_reports(provided_ticker: str, company_name: str) -> dict:
    """
    Combines Markdown files from a hard-coded 'reports' folder into a single report.

    Args:
        provided_ticker (str): Stock ticker symbol, must be a string.
        company_name (str): Name of the company, must be a string.

    Returns:
        dict: A dictionary containing status information with the following structure:
            On success: {"status": "success", "output_report_name": str, "report_path": str}
            On error: {"status": "error", "error_message": str}
    """
    # Hard-coded input folder
    input_folder = 'reports'
    # Generate date string in YYYYMMDD format
    date_str = datetime.now().strftime('%Y%m%d')
    # Validate inputs
    if not isinstance(provided_ticker, str):
        return {"status": "error", "error_message": "provided_ticker must be a string"}
    if not isinstance(company_name, str):
        return {"status": "error", "error_message": "company_name must be a string"}

    # Construct output basename with underscores
    output_basename = f"equity_research_report_{company_name}_{provided_ticker}_{date_str}"
    combined_md_path = os.path.join(input_folder, f"{output_basename}.md")

    try:
        # Define the expected order of files
        categories = ['fundamental', 'technical', 'fund', 'policy']

        # Ensure reports directory exists
        os.makedirs(input_folder, exist_ok=True)

        # Combine Markdown files
        with open(combined_md_path, 'w', encoding='utf-8') as outfile:

            # Write content from each category
            for category in categories:
                filename = f"{category}_agent_report.md"
                filepath = os.path.join(input_folder, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(f"<!-- ===== {category.upper()} SECTION ===== -->\n\n")
                        outfile.write(content + "\n\n")
                else:
                    print(f"Warning: {filename} not found in {input_folder}. Skipping...")

        # Normalize output_format
        # 读取 Markdown 文件
        with open(combined_md_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        # 转换为 HTML
        html_content = markdown.markdown(md_text, extensions=["tables"])

        html_full = f"""
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <title>导出文档</title>
            <style>
                body {{
                    font-family: "Arial", sans-serif;
                    font-size: 12pt;
                    line-height: 1.6;
                    padding: 2em;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 1em 0;
                }}
                th, td {{
                    border: 1px solid #333;
                    padding: 6px 10px;
                    text-align: center;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """

        # 写入 HTML 文件
        output_file_html = os.path.join(input_folder, f"{output_basename}.html")

        with open(output_file_html, "w", encoding="utf-8") as f:
            f.write(html_full)


        # 自定义页面样式
        css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: "Arial", sans-serif;
                font-size: 12pt;
                line-height: 1.6;
            }
            h1, h2, h3 {
                color: #2e6c80;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
            }
            th, td {
                border: 1px solid #333;
                padding: 6px 10px;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
        ''')

        output_file_pdf = os.path.join(input_folder, f"{output_basename}.pdf")

        HTML(string=html_content).write_pdf(output_file_pdf, stylesheets=[css])



        return {
            "status": "success",
            "output_report_name": output_basename,
            "report_path": output_file_pdf
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error occurred during output: {str(e)}"
        }




def email_report(report_path: str, recipient_email: str) -> dict:
    """
    Placeholder function to email the report.
    
    Args:
        report_path (str): Path of the report to be emailed.
        recipient_email (str): Email address of the recipient.
    
    Returns:
        dict: A dictionary containing status information.
    """
    
    
    # 1. 读取本地 HTML 文件
    html_file_path = f"{report_path}"
    report_name = os.path.basename(report_path)
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 2. 构造邮件内容
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'{report_name}'         # 邮件主题
    msg['From'] = 'sender@example.com'    # 发件人地址
    msg['To'] = recipient_email   # 收件人地址，可以用逗号分隔多个

    # 将 HTML 内容封装为 MIMEText，指定 subtype='html'
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)

    # 3. 通过 SMTP 发送邮件
    smtp_server = 'smtp.example.com'  # SMTP 服务器地址，例如 smtp.gmail.com
    smtp_port = 587                   # SMTP 端口（若使用 STARTTLS，一般是 587；SSL/TLS 一般是 465）
    smtp_user = 'sender@example.com'  # SMTP 登录用户名（通常就是发件人邮箱地址）
    smtp_password = 'your_password'   # SMTP 登录密码（注意有的邮箱需要开“SMTP/IMAP 服务”并用授权码）

    server = None
    try:
        # 建立到 SMTP 服务器的连接（这里以 STARTTLS 模式为例）
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(msg['From'], msg['To'].split(','), msg.as_string())
        print("邮件发送成功！")
    except Exception as e:
        print("发送邮件时发生异常：", e)
    finally:
        if server:
            server.quit()


    return {
        "status": "success",
        "message": f"Report {report_name} has been emailed to {recipient_email}."
    }



def schedule_email_report(report_path: str, recipient_email: str, schedule_time: str) -> dict:
    """
    Schedules an email to be sent at a specific time.
    
    Args:
        report_path (str): Path to the report file to be emailed.
        recipient_email (str): Email address of the recipient.
        schedule_time (str): Time to send the email in HH:MM format.
    
    Returns:
        dict: A dictionary containing status information.
    """
    
    def job():
        email_report(report_path, recipient_email)
    
    # Schedule the job
    schedule.every().day.at(schedule_time).do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for a short time to avoid busy-waiting


