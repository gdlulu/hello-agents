import re
import random
from typing import Optional

# 定义规则库：模式(正则表达式) -> 响应模板列表
rules = {
    r'I need (.*)': [
        "Why do you need {0}?",
        "Would it really help you to get {0}?",
        "Are you sure you need {0}?"
    ],
    r'Why don\'t you (.*)\?': [
        "Do you really think I don't {0}?",
        "Perhaps eventually I will {0}.",
        "Do you really want me to {0}?"
    ],
    r'Why can\'t I (.*)\?': [
        "Do you think you should be able to {0}?",
        "If you could {0}, what would you do?",
        "I don't know -- why can't you {0}?"
    ],
    r'I am (.*)': [
        "Did you come to me because you are {0}?",
        "How long have you been {0}?",
        "How do you feel about being {0}?"
    ],
    r'.* mother .*': [
        "Tell me more about your mother.",
        "What was your relationship with your mother like?",
        "How do you feel about your mother?"
    ],
    r'.* father .*': [
        "Tell me more about your father.",
        "How did your father make you feel?",
        "What has your father taught you?"
    ],
    r'.* (work|study) .*': [
        "How do you feel about your {0}?",
        "How is your current {0} going?",
        "Tell me more about your {0}."
    ],
    r'.*': [
        "Please tell me more.",
        "Let's change focus a bit... Tell me about your family.",
        "Can you elaborate on that?"
    ]
}

# 定义代词转换规则
pronoun_swap: dict[str, str] = {
    "i": "you", "you": "i", "me": "you", "my": "your",
    "am": "are", "are": "am", "was": "were", "i'd": "you would",
    "i've": "you have", "i'll": "you will", "yours": "mine",
    "mine": "yours"
}

# 简单会话记忆：仅在程序运行期间有效
memory: dict[str, Optional[str]] = {
    "name": None,
    "age": None,
    "job": None
}

def swap_pronouns(phrase: str) -> str:
    """
    对输入短语中的代词进行第一/第二人称转换
    """
    words = phrase.lower().split()
    swapped_words = [pronoun_swap.get(word, word) for word in words]
    return " ".join(swapped_words)

def clean_text(text: str) -> str:
    """
    清理捕获到的文本，去掉首尾空白和末尾标点
    """
    return re.sub(r'[.!?]+$', '', text.strip())

def update_memory(user_input: str) -> Optional[str]:
    """
    从用户输入中提取并保存关键信息：姓名、年龄、职业
    如果成功更新，返回一条确认回复；否则返回 None
    """
    replies = []

    # 1) 提取姓名
    name_match = re.search(
        r"\b(?:my name is|call me)\s+([A-Za-z][A-Za-z\s'-]*)",
        user_input,
        re.IGNORECASE
    )
    if name_match:
        name = clean_text(name_match.group(1)).title()
        if memory["name"] != name:
            memory["name"] = name
            replies.append(f"Nice to meet you, {name}. I'll remember your name.")

    # 2) 提取年龄
    age_match = re.search(
        r"\b(?:i am|i'm)\s+(\d{1,3})\s*(?:years old)?\b",
        user_input,
        re.IGNORECASE
    )
    if age_match:
        age = clean_text(age_match.group(1))
        if memory["age"] != age:
            memory["age"] = age
            replies.append(f"I'll remember that you are {age} years old.")

    # 3) 提取职业
    job_match = re.search(
        r"\b(?:i work as|my job is|i am a|i am an|i'm a|i'm an)\s+([A-Za-z][A-Za-z\s'-]*)",
        user_input,
        re.IGNORECASE
    )
    if job_match:
        job = clean_text(job_match.group(1)).lower()
        if memory["job"] != job:
            memory["job"] = job
            replies.append(f"I'll remember that you work as {job}.")

    if replies:
        return " ".join(replies)
    return None

def answer_memory_question(user_input: str) -> Optional[str]:
    """
    处理用户对“记忆”的直接提问
    """
    text = user_input.lower()

    # 询问姓名
    if re.search(r"\b(what is my name|what's my name|do you remember my name|who am i)\b", text):
        if memory["name"]:
            return f"Your name is {memory['name']}."
        return "You haven't told me your name yet."

    # 询问年龄
    if re.search(r"\b(what is my age|what's my age|how old am i|do you remember my age)\b", text):
        if memory["age"]:
            return f"You told me that you are {memory['age']} years old."
        return "You haven't told me your age yet."

    # 询问职业
    if re.search(r"\b(what is my job|what's my job|what do i do|do you remember my job|do you remember my occupation)\b", text):
        if memory["job"]:
            return f"You told me that you work as {memory['job']}."
        return "You haven't told me your job yet."

    # 总结已知信息
    if re.search(r"\b(what do you know about me|what do you remember about me)\b", text):
        facts = []
        if memory["name"]:
            facts.append(f"your name is {memory['name']}")
        if memory["age"]:
            facts.append(f"you are {memory['age']} years old")
        if memory["job"]:
            facts.append(f"you work as {memory['job']}")

        if facts:
            return "I remember that " + ", and ".join(facts) + "."
        return "I don't know much about you yet. You can tell me your name, age, or job."

    return None

def contextual_fallback(default_response: str) -> str:
    """
    当命中兜底规则时，优先使用带上下文记忆的回复
    """
    if memory["job"]:
        return f"You mentioned that you work as {memory['job']}. How does that relate to what you just said?"
    if memory["age"]:
        return f"You told me that you are {memory['age']} years old. Does that affect how you see this?"
    if memory["name"]:
        return f"{memory['name']}, can you tell me a little more about that?"
    return default_response

def respond(user_input: str) -> str:
    """
    根据规则库生成响应，并加入简单上下文记忆
    """
    # 先尝试更新记忆
    memory_update_reply = update_memory(user_input)
    if memory_update_reply:
        return memory_update_reply

    # 再处理对“记忆”的直接提问
    memory_answer = answer_memory_question(user_input)
    if memory_answer:
        return memory_answer

    # 最后走原有 ELIZA 规则
    for pattern, responses in rules.items():
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            captured_group = match.group(1) if match.groups() else ''
            swapped_group = swap_pronouns(captured_group)
            response = random.choice(responses).format(swapped_group)

            # 如果命中的是兜底规则，则尝试注入上下文记忆
            if pattern == r'.*':
                response = contextual_fallback(response)

            return response

    return random.choice(rules[r'.*'])

# 主聊天循环
if __name__ == '__main__':
    print("Therapist: Hello! How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Therapist: Goodbye. It was nice talking to you.")
            break
        response = respond(user_input)
        print(f"Therapist: {response}")