1. 同步依赖

    - 公司

    容器内安装新包并给更新依赖文件:

    ```
    pip install ...
    python gen_requirement.py
    ```

    更新容器并提交

    ```
    docker compose up --build -d
    git add requirements.txt
    git commit -m "chore: add pydantic"
    git push
    ```

    - 回家后

    ```
    git pull
    docker compose up --build -d
    ```

2. 家里电脑第一次接手

    ```
    git clone https://github.com/yourname/my-python-project.git
    cd my-python-project
    docker compose up --build -d
    docker compose exec app python app/main.py
    ```

3. 若要忽略缓存, 完全重新构建容器, 则使用 
    ```
    docker compose build --no-cache
    docker compose up -d
    ```

4. 如果要安装 torch, 则主依赖文件不要出现以下这些包:
    ```
    torch==
    torchvision==
    torchaudio==
    triton==
    nvidia-
    ```

5. 验证 torch 是否兼容及 gpu 是否已经加载

    ```
    python - <<'PY'
    import torch
    print("torch =", torch.__version__)
    print("cuda available =", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("gpu =", torch.cuda.get_device_name(0))
    PY
    ```