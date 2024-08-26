import openai
import gradio as gr
import base64
import requests
import os


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_content(base64_image, api_key):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": """
             請扮演一位臺灣人且你的專業是影像辨識專家，你需要達成以下目的
             1.辨識圖片的車票類型是臺灣鐵路或台灣高鐵
             台鐵的車種有:太魯閣、普悠瑪、自強、莒光、區間車
             高鐵車票上不太會看到車種，通常會顯示台灣高鐵或不顯示
             回答時請回答"台鐵"或"高鐵"
             2.辨識車票的日期
             3.辨識車票的車次
             4.辨識車票的出發時間-抵達時間
             5.辨識車票的出發站-抵達站
             """,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                    請辨識圖片的車票，並整理成以下格式:
                    範例如下\n
                    車種:高鐵
                    日期:2022/10/24
                    車次:125
                    出發站 出發時間 → 抵達站 抵達時間:台中 11:20 → 台北 13:05
                    """,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        "max_tokens": 300,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    print(response.json()["choices"][0]["message"]["content"])
    return response.json()["choices"][0]["message"]["content"]


def image_recognition(image, api_key):
    base64_image = encode_image(image)
    os.environ["OPENAI_API_KEY"] = api_key

    while True:
        image_content = get_image_content(base64_image, api_key)
        qtype=image_content.split("\n")[0][3:5]
        qdate=image_content.split("\n")[1][3:]
        qtrain=image_content.split("\n")[2][3:]
        qtime=image_content.split("\n")[3][20:]
        if qtype == "台鐵" or qtype == "高鐵":
            break
    return qtype, qtrain, qdate, qtime


# important
with gr.Blocks() as demo:
    gr.Markdown("交通工具")
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
            qstation_qtime = gr.Textbox(label="出發站 出發時間 → 抵達站 抵達時間", value="")

    submit_button.click(
        image_recognition,
        inputs=[file_input, api_key_input],
        outputs=[qtype, qtrain, qdate, qstation_qtime],
    )
