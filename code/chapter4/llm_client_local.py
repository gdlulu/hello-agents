import os
from typing import List, Dict, Optional

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 可选：使用 HF 镜像，避免部分环境下直连失败
os.environ.setdefault("HF_ENDPOINT", os.getenv("HF_ENDPOINT", "https://hf-mirror.com"))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class HelloAgentsLLM:
    """
    为本书 "Hello Agents" 定制的本地 LLM 客户端。
    它使用 transformers 直接加载本地/可下载模型，
    对外仍保持 think(messages) 的调用方式，尽量兼容现有 ReActAgent。
    """

    def __init__(
        self,
        model_id: Optional[str] = None,
        device: Optional[str] = None,
        dtype: str = "auto",
        max_new_tokens: Optional[int] = None,
        apiKey: str = None,
        baseUrl: str = None,
        timeout: int = None,
    ):
        """
        初始化本地模型。
        保留 apiKey/baseUrl/timeout 参数仅为兼容旧调用；本地推理时不会使用它们。
        """
        self.model_id = model_id or "Qwen/Qwen1.5-0.5B-Chat"
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_new_tokens = max_new_tokens or int(os.getenv("LLM_MAX_NEW_TOKENS", 512))
        self.temperature_default = float(os.getenv("LLM_TEMPERATURE", 0))

        print(f"Using device: {self.device}")
        print(f"Loading model: {self.model_id}")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            dtype=dtype,
        ).to(self.device)
        self.model.eval()

        # 某些模型未显式设置 pad_token_id，生成时补齐到 eos_token_id 更稳
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        print("模型和分词器加载完成！")

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> Optional[str]:
        """
        调用本地大模型进行思考，并返回响应文本。
        messages 格式保持与 OpenAI chat 接口一致：
        [{"role": "system/user/assistant", "content": "..."}, ...]
        """
        print(f"🧠 正在调用本地模型 {self.model_id} ...")
        try:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

            actual_temperature = self.temperature_default if temperature == 0 else temperature
            do_sample = actual_temperature > 0

            with torch.no_grad():
                generated_ids = self.model.generate(
                    input_ids=model_inputs.input_ids,
                    attention_mask=model_inputs.attention_mask,
                    max_new_tokens=2048,
                    do_sample=False
                )

            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            response = response.strip()

            print("✅ 本地模型响应成功:")
            print(response)
            return response

        except Exception as e:
            print(f"❌ 调用本地模型时发生错误: {e}")
            return None


# --- 客户端使用示例 ---
if __name__ == '__main__':
    llm_client = HelloAgentsLLM()

    example_messages = [
        {"role": "system", "content": "You are a helpful assistant that writes Python code."},
        {"role": "user", "content": "写一个快速排序算法"},
    ]

    print("--- 调用本地LLM ---")
    response_text = llm_client.think(example_messages)
    if response_text:
        print("\n--- 完整模型响应 ---")
        print(response_text)
