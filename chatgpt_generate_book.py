import logging
import json
import time
import asyncio
from flask import Flask, request, jsonify

import requests

# 初始化日志记录
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

sk = "app-wcfDRQLl065a5UV7IqKb3AWU"

def get_chat_gpt_response(messages):
    start_time = time.time()
    logger.info("开始请求模型，目的：获取模型回复")
    url = "https://api.dify.ai/v1/chat-messages"
    headers = {
        "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {},
        "query": messages[1]["content"],
        "user": "abc-123",
    }
    response = requests.post(url, headers=headers, json=payload)
    print("response = ", response.json())
    end_time = time.time()
    logger.info(f"请求模型完成，耗时：{end_time - start_time:.2f} 秒")
    return response.json()["answer"]


def determine_category_id(book_name, author):
    logger.info("开始确定书籍分类 ID")
    categories = [
        {"id": 1867241758165962752, "name": "心理"},
        {"id": 1867241883797950464, "name": "教育"},
        {"id": 1867241987208515584, "name": "历史"},
        {"id": 1867242052631269376, "name": "科学"},
        {"id": 1867242079994908672, "name": "哲学"},
        {"id": 1867242137347821568, "name": "经济"},
        {"id": 1867242426981289984, "name": "小说"},
        {"id": 1867242524909899776, "name": "政治"},
        {"id": 1867242572565581824, "name": "传记"},
        {"id": 1867242601053294592, "name": "技术"},
        {"id": 1880157230985252864, "name": "宗教"},
        {"id": 1880157270579482624, "name": "营养健康"},
        {"id": 1880157365358170112, "name": "自然环境"},
        {"id": 1880157425286385664, "name": "社会文明"},
        {"id": 1880157487672463360, "name": "社交&两性"},
        {"id": 1880157532476018688, "name": "管理与领导"},
        {"id": 1880157572904914944, "name": "企业建设"},
        {"id": 1880157625602150400, "name": "个人发展与职业"},
        {"id": 1880157667184480256, "name": "市场销售"},
        {"id": 1880157703926583296, "name": "投资理财"},
    ]
    categories_str = json.dumps(categories, indent=4)
    prompt = f"""
你非常擅长书籍归纳，书名：《{book_name}》，作者：{author}，
这本书属于下面的哪个分类，请只回答我分类对应的 id 即可：
{categories_str}
    """
    messages = [
        {
            "role": "system",
            "content": "你是一名文学分类专家，擅长将书籍归类到适合的类别中。",
        },
        {"role": "user", "content": prompt},
    ]
    response = get_chat_gpt_response(messages)
    print("resp = ", response)
    category_id = response.strip()
    logger.info("确定书籍分类 ID 完成")
    return category_id


def generate_book_description(book_name, author):
    logger.info("开始生成书籍描述")
    prompt = f"""
请用一句话，大约40个字，总结《{book_name}》（作者：{author}）的主要内容。总结要生动、有吸引力，让读者感兴趣。
1. 首先快速识别本书的类型
2. 准确把握该类型图书最需要突出的重点
3. 使用生动具体的描述语言
4. 确保内容完全基于这本书，避免主观臆测
5. 检查总结是否符合40字要求
    """
    messages = [
        {
            "role": "system",
            "content": "你是一位优秀的书籍内容总结者，能够精准概括书籍核心内容。",
        },
        {"role": "user", "content": prompt},
    ]
    response = get_chat_gpt_response(messages)
    book_description = response.strip()
    logger.info("生成书籍描述完成")
    return book_description


def generate_book_summary(book_name, author):
    logger.info("开始生成书籍总结")
    prompt = f"""
请写一段大约200字的内容介绍，用于全面呈现《{book_name}》（作者：{author}）的核心信息并吸引读者兴趣。
1. 明确书的类型及文本特质
2. 说明主题与情感基调
3. 使用生动、富有感染力的描述
4. 信息与吸引力需平衡，留有悬念
5. 字数控制在200字左右
6. 避免使用多余的格式标签
    """
    messages = [
        {
            "role": "system",
            "content": "你是一位资深的书籍推广人，擅长撰写引人入胜的书籍总结。",
        },
        {"role": "user", "content": prompt},
    ]
    response = get_chat_gpt_response(messages)
    book_summary = response.strip()
    logger.info("生成书籍总结完成")
    return book_summary


def generate_chapter_list(book_name, author):
    logger.info("开始生成书籍章节列表")
    prompt = f"""
请完整列出《{book_name}》（作者：{author}）章节结构，如果书中没有,需要你来自己总结生成最终10章的结构，要求如下：
1. 每一章包括编号、简短的章节标题、本章简介三部分
2. 章节简介生成什么是精彩内容，尽量在原文中找到关键事件和主要人物，章节之间不要有重叠的情节，每一章独立完整
3. 如果总章数超过10，则根据模型理解合并临近章节，生成最终10章的结构
4. 输出内容严格按照如下格式，不要其他输出：
[{{"chapterNum": "", "chapterName": "", "chapterDesc": ""}}]
    """
    messages = [
        {
            "role": "system",
            "content": "你是一位精通文学作品结构的专家，请严格按照指定格式输出书籍章节结构的 JSON 数据。",
        },
        {"role": "user", "content": prompt},
    ]
    response = get_chat_gpt_response(messages)
    content = response
    # 尝试提取 JSON 部分
    json_str = content
    if "```json" in content:
        start_index = content.find("```json") + len("```json")
        end_index = content.rfind("```")
        json_str = content[start_index:end_index]
    try:
        logger.info(f"解析章节列表JSON：{json_str}")
        chapter_list = json.loads(json_str)
    except json.JSONDecodeError:
        logger.error("解析章节列表JSON数据时出错")
        chapter_list = []
    logger.info("生成书籍章节列表完成")
    return chapter_list


def check_chapter_summary(content) -> bool:
    return True
    prompt = f"""
请严格根据原文检查以下内容是否符合原文
判断是否有编造和虚构等不符合原文的情节、人物、事件等，如果符合原文返回true，否则返回false，*不要返回任何其他的内容*
生成的内容如下：
{content}
    """
    messages = [
        {"role": "system", "content": "你是一位资深的书籍推广人，擅长撰写引人入胜的书籍总结。"},
        {"role": "user", "content": prompt},
    ]
    response = get_chat_gpt_response(messages)
    return response.strip() == "true"


def generate_single_chapter_content(book_name, author, chapter):
    chapter_num = chapter["chapterNum"]
    chapter_name = chapter["chapterName"]
    chapter_desc = chapter["chapterDesc"]
    logger.info(f"开始处理第 {chapter_num} 章《{chapter_name}》")
    prompt = f"""
你是一个专注于客观叙事的书籍摘要助手。请为书籍《{book_name}》（作者：{author}）的第 {chapter_num} 章《{chapter_name}》生成一段面向听众的章节概述。参考章节描述如下
{chapter_desc} 生成章节内容, 你可以在原文中搜寻并且总结出章节内容。不要过度发挥创造不存在的剧情、人物和场景。考虑听众的感受，章节内的剧情一定要连贯，剧情发展有逻辑，不能没有转折的突然跳转。
**严格遵循以下规则：**
1.  **聚焦客观行为与场景：**
    *   只复述本章发生的具体事件、人物的**可观察行为**（做了什么、说了什么）以及**环境/场景**的客观描写。

请立即为第 {chapter_num} 章《{chapter_name}》以*严谨*的风格生成字数在400-600字左右的客观完整的内容总结。不要出现类似 在本章中 等字样
"""
    messages = [
        {
            "role": "system",
            "content": "你是一位写实且富有感染力的故事讲述者，擅长总结书籍章节内容。",
        },
        {"role": "user", "content": prompt},
    ]
    response = get_chat_gpt_response(messages)
    content = response.strip()
    if check_chapter_summary(content):
        logger.info(f"完成处理第 {chapter_num} 章《{chapter_name}》")
    else:
        logger.error(f"第 {chapter_num} 章《{chapter_name}》内容不符合原文")
        # regenerate
        return generate_single_chapter_content(book_name, author, chapter)

    return {
        "chapterNum": chapter_num,
        "chapterName": chapter_name,
        "chapterDesc": chapter_desc,
        "chapterSummary": content,
    }


def generate_chapter_contents(book_name, author, chapter_list):
    logger.info("开始生成所有章节内容总结")
    chapter_contents = []
    for chapter in chapter_list:
        chapter_content = generate_single_chapter_content(book_name, author, chapter)
        chapter_contents.append(chapter_content)
    logger.info("生成章节内容总结完成")
    return chapter_contents


def get_accurate_book_info(book_name, author):
    logger.info("开始获取准确的书名和作者信息")
    prompt = f"""
请根据输入的书名《{book_name}》和作者 {author}，给出准确的书名和作者（如输入不准确，请纠正后返回），
以 JSON 格式输出，格式为: {{"bookName": "准确的书名", "author": "准确的作者"}}。
    """
    messages = [
        {"role": "system", "content": "你是一个能够准确识别和纠正书籍信息的专家。"},
        {"role": "user", "content": prompt},
    ]
    response = get_chat_gpt_response(messages)
    result = response
    json_str = result
    if "```json" in result:
        start_index = result.find("```json") + len("```json")
        end_index = result.rfind("```")
        json_str = result[start_index:end_index]
    try:
        info = json.loads(json_str)
        logger.info("获取准确书籍信息完成")
        return info["bookName"], info["author"]
    except (json.JSONDecodeError, KeyError):
        logger.error("获取准确书名和作者信息时出错")
        return book_name, author


def get_book_ten_sentence(book_name, author):
    logger.info("开始获取10个金句")
    prompt = f"""
请根据输入的书名《{book_name}》和作者 {author}，总结书中的10个金句，表达该书的核心思想，
必须是文本中的原话，禁止编造，以 JSON 格式输出，格式为: [{{"num": "1", "sentence": "金句1"}}, ...]。
    """
    messages = [
        {
            "role": "system",
            "content": "你是一位资深的书籍推广人，擅长提炼书中核心语句。",
        },
        {"role": "user", "content": prompt},
    ]
    result = get_chat_gpt_response(messages)
    json_str = result
    if "```json" in result:
        start_index = result.find("```json") + len("```json")
        end_index = result.rfind("```")
        json_str = result[start_index:end_index]
    try:
        info = json.loads(json_str)
        logger.info("获取金句成功")
        return info
    except (json.JSONDecodeError, KeyError):
        logger.error("获取金句信息时出错")
        return []


@app.route("/summarize", methods=["POST"])
def summarize():
    start_total_time = time.time()
    logger.info("开始处理书籍总结请求")
    data = request.get_json()
    book_name = data.get("bookName")
    author = data.get("author")

    if not book_name or not author:
        return jsonify({"error": "书名和作者不能为空"}), 400

    # 优先获取准确的书籍信息
    book_name, author = get_accurate_book_info(book_name, author)

    # 顺序执行各个任务
    category_id = determine_category_id(book_name, author)
    book_description = generate_book_description(book_name, author)
    book_summary = generate_book_summary(book_name, author)
    chapter_list = generate_chapter_list(book_name, author)
    ten_sentence = get_book_ten_sentence(book_name, author)

    # 生成章节内容
    chapter_contents = generate_chapter_contents(book_name, author, chapter_list)

    result = {
        "categoryId": category_id,
        "name": book_name,
        "author": author,
        "bookDescription": book_description,
        "bookSummary": book_summary,
        "chapterContents": chapter_contents,
        "ten_sentence": ten_sentence,
    }
    end_total_time = time.time()
    logger.info(
        f"处理书籍总结请求完成，总耗时：{end_total_time - start_total_time:.2f} 秒"
    )
    return jsonify(result)


if __name__ == "__main__":
    # 使用 asyncio.run 在开发环境下运行 Flask 的异步视图（建议生产环境使用 ASGI 服务器）
    app.run(host="0.0.0.0", port=6999, debug=True)
