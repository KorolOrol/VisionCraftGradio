import gradio as gr
import requests
import json
import os
import datetime

api_url = "https://visioncraftapi--vladalek05.repl.co"

models = requests.get(api_url + "/models").json()
samplers = requests.get(api_url + "/samplers").json()
loras = requests.get(api_url + "/loras").json()

def saving_images(image_urls):
    if(not (os.path.exists("output") and os.path.isdir("output"))):
        os.mkdir("output")
    today = str(datetime.datetime.now().date())
    if(not (os.path.exists(f"output\\{today}") and os.path.isdir(f"output\\{today}"))):
        os.mkdir(f"output\\{today}")
    last_image = os.listdir(f"output\\{today}")
    last_image = [int(i[:-4]) for i in last_image]
    last_image.sort()
    if last_image:
        last_image = last_image[-1]
    else:
        last_image = 0
    output = []
    for i, image in enumerate(image_urls):
        with open(f"output\\{today}\\{str(last_image + i + 1)}.png", "xb") as f:
            f.write(requests.get(image).content)
            output.append(f"output\\{today}\\{str(last_image + i + 1)}.png")
    return output

def generate_image(api_key, prompt, negative, model, lora, sampler, cfg_scale, steps, image_count):
    lora = lora.to_dict()
    lora = {lora['Lora'][i]: int(lora['Weight'][i]) for i in range(len(lora['Lora'])) if int(lora["Weight"][i]) != 0}
    data = {
        "model": model,
        "sampler": sampler,
        "prompt": prompt,
        "negative_prompt": negative,
        "image_count": image_count,
        "token": api_key,
        "cfg_scale": cfg_scale,
        "steps": steps,
        "loras": lora,
    }
    with open("params.txt", 'w') as f:
        f.write(json.dumps(data))
    response = requests.post(api_url + "/generate", json=data).json()
    if "error" in response.keys():
        gr.Error(response["error"])
        return None
    else:
        return saving_images(response["images"])

with gr.Blocks() as webui:
    api_key_tb = gr.Textbox(lines=1, label="API Key", type="password")
    with gr.Row() as header:
        with gr.Column() as left_col:
            with gr.Row():
                prompt_tb = gr.Textbox(lines=5, label="Prompt")
                negative_tb = gr.Textbox(lines=5, label="Negative Prompt")
            with gr.Row():
                model_dd = gr.Dropdown(models, label="Model")
                sampler_dd = gr.Dropdown(samplers, label="Sampler")
            with gr.Row():
                cfg_scale_sl = gr.Slider(minimum=0, maximum=20, value=10, step=1, label="CFG Scale", scale=4)
                steps_sl = gr.Slider(minimum=0, maximum=50, value=30, step=1, label="Steps", scale=4)
                image_count_dd = gr.Dropdown(range(1, 5), label="Image Count", scale=1)
            with gr.Accordion("Loras", open=False):
                lora_df = gr.Dataframe([[l, 0] for l in loras], headers=["Lora", "Weight"], 
                                    interactive=True, row_count=(len(loras), "static"), col_count=(2, "static"))
        with gr.Column() as right_col:
            generate_button = gr.Button("Generate")
            image = gr.Gallery(label="Image")
    generate_button.click(generate_image, inputs=[api_key_tb, prompt_tb, negative_tb, 
                                                  model_dd, lora_df, sampler_dd, 
                                                  cfg_scale_sl, steps_sl, image_count_dd], 
                            outputs=[image])
    if os.path.exists("params.txt"):
        with open("params.txt", "r") as f:
            f = json.load(f)
            api_key_tb.value = f["token"]
            prompt_tb.value = f["prompt"]
            negative_tb.value = f["negative_prompt"]
            model_dd.value = f["model"]
            sampler_dd.value = f["sampler"]
            cfg_scale_sl.value = f["cfg_scale"]
            steps_sl.value = f["steps"]
            image_count_dd.value = f["image_count"]
            for l in lora_df.value['data']:
                if l[0] in f['loras'].keys():
                    l[1] = int(f['loras'][l[0]])
webui.launch()