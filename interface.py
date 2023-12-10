import gradio as gr
import requests

api_url = "https://visioncraftapi--vladalek05.repl.co"

models = requests.get(api_url + "/models").json()
samplers = requests.get(api_url + "/samplers").json()
loras = requests.get(api_url + "/loras").json()

api_key = "d2882741-7085-416e-ac38-eb1ccbcd09be"

def generate_image(prompt, negative, model, lora, sampler, cfg_scale, steps):
    lora = lora.to_dict()
    lora = {lora['Lora'][i]: int(lora['Weight'][i]) for i in range(len(lora['Lora'])) if lora['Weight'][i] != 0}
    data = {
        "model": model,
        "sampler": sampler,
        "prompt": prompt,
        "negative_prompt": negative,
        "image_count": 1,
        "token": api_key,
        "cfg_scale": cfg_scale,
        "steps": steps,
        "loras": lora
    }
    print(data)
    response = requests.post(api_url + "/generate", json=data)
    print(response.json())
    try:
        image_urls = response.json()["err"]
        gr.Error(image_urls)
        return None
    except:
        image_urls = response.json()["images"]
    return image_urls

with gr.Blocks() as webui:
    with gr.Row() as header:
        with gr.Column() as left_col:
            with gr.Row():
                prompt = gr.Textbox(lines=5, label="Prompt")
                negative = gr.Textbox(lines=5, label="Negative Prompt")
            with gr.Row():
                model = gr.Dropdown(models, label="Model")
                sampler = gr.Dropdown(samplers, label="Sampler")
            with gr.Row():
                cfg_scale = gr.Slider(minimum=0, maximum=20, value=10, step=1, label="CFG Scale")
                steps = gr.Slider(minimum=0, maximum=30, value=30, step=1, label="Steps")
            with gr.Accordion("Loras", open=False):
                lora = gr.Dataframe([[lora, 0] for lora in loras], headers=["Lora", "Weight"], 
                                    interactive=True, row_count=(len(loras), "static"), col_count=(2, "static"))
        with gr.Column() as right_col:
            generate_button = gr.Button("Generate")
            image = gr.Gallery(label="Image")
    generate_button.click(generate_image, inputs=[prompt, negative, model, lora, sampler, cfg_scale, steps], outputs=[image])
webui.launch()