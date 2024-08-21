import openai
import gradio as gr
import base64
import requests


def openai_api(prompt, key):
    openai.api_key = key
    completion = openai.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_content(base64_image, api_key):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": 
                        """
                        扮演影像識別專家，幫我把所有的細節都識別出來。
                        請找出交通工具種類(台鐵或高鐵)，車次，日期，出發和抵達時間，出發站和終點站。
                        """,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # 如果發生HTTP錯誤，則會引發HTTPError異常
        image_content = response.json()["choices"][0]["message"]["content"]
        return image_content
    except Exception as err:
        print(f"Other error occurred: {err}")
        return get_image_content(base64_image)


def image_recognition(image, api_key):
    base64_image = encode_image(image)
    image_content = get_image_content(base64_image, api_key)
    prompt = (
        """
        扮演文字處理專家，幫我把逐字稿整理成格式：\
        原則2：輸出格式(但不用出現本句)：
        $type:| 車種 $train no.:| 車次 $date:| 日期 $time:| 出發時間-抵達時間 $station :| 出發站-抵達站 $none :| none\
        原則3：Let's work this out in a step-by-step way to be sure we have the right answer.\
        原則4：以繁體中文來命題。逐字稿： 
        """
        + image_content
    )
    result = openai_api(prompt, api_key)
    print(result)
    qtype = result.split("$type:|")[1].split("$train no.:|")[0].strip()
    qtrain = result.split("$train no.:|")[1].split("$date:|")[0].strip()
    qdate = result.split("$date:|")[1].split("$time:|")[0].strip()
    qtime = result.split("$time:|")[1].split("$station:|")[0].strip()
    qstation = result.split("$station:|")[1].split("$none:|")[0].strip()

    return qtype, qtrain, qdate, qtime, qstation


with gr.Blocks() as demo:
    gr.Markdown("銀行存摺帳號識別")
    with gr.Tab("請依順序操作"):
        with gr.Row():
            file_input = gr.File(label="第一步：請上傳檔案")
            api_key_input = gr.Textbox(
                label="第二步：請輸入OpenAI API金鑰", placeholder="OpenAI API Key"
            )
            submit_button = gr.Button("第三步：開始識別")
        with gr.Row():
            qtype = gr.Textbox(label="車種", value="")
            qtrain = gr.Textbox(label="車次", value="")
            qdate = gr.Textbox(label="日期", value="")
            qtime = gr.Textbox(label="出發時間-抵達時間", value="")
            qstation = gr.Textbox(label="出發站-抵達站", value="")

    submit_button.click(
        image_recognition,
        inputs=[file_input, api_key_input],
        outputs=[qtype, qtrain, qdate, qtime, qstation],
    )
