import gradio as gr
from functools import reduce
from .smallcard import Card as C1
from .card import Card as C2
from scripts.mm_libs.model import Model
from scripts.mm_libs import downloader
from scripts.mm_libs import selenium_dynamic as sd
from itertools import zip_longest
import webbrowser
from modules import shared

models: list[list[Model]] = []
cards: list[C2] = []
last_model_index = 0
is_token_set = False

def UI():
    is_token_set = shared.opts.mm_github_token != ""

    def create_session():
        try:
            sd.create_civitai_session()
        except Exception as e:
            print(f"Error: {e}")

    gr.Markdown("""## Fetch Models from your Civitai Notifications Page
                This is a very work in progress feature, that will allow you to fetch models from your Civitai notifications page.
                Can be a bit hard to get working right now as it requires a Github token, to download a FireFox driver.
                Will look into how to get it working without a token, and instead just use whatever driver is already installed on the system.
                For now, if you want to test it, you need to create a fine-grained token on GitHub and paste it into the Github Token Setting in 'Settings->Model Manager'.
                """)

    create_session_btn = gr.Button("Create Civitai Session", visible=is_token_set)
    get_session_page_source_btn = gr.Button("Get Session Page Source", visible=is_token_set)

    def scape_models():
        global models, last_model_index
        last_model_index = 0
        try:
            models = sd.get_page_source()
        except Exception as e:
            print(f"Error: {e}")
            return
        return update_cards(models)

    def get_pagination_states():
        last = last_model_index >= len(cards)
        next = last_model_index < len(models) - len(cards)
        return [
            gr.Button.update(visible=True, interactive=last),
            gr.Button.update(visible=True, interactive=next),
        ]

    def update_cards(models : list):
        global last_model_index

        if len(models) < len(cards):
            for card, model in zip_longest(cards, models):
                card.insert_models(model)
        else:
            for card, model in zip(cards, models):
                card.insert_models(model)

        print("Cards updated! Updating UI...")
        return (
            reduce(lambda acc, card: acc + card.get_updates(), cards, [])
            + get_pagination_states()
        )

    def next_page():
        global last_model_index
        last_model_index += len(cards)
        return update_cards(models[last_model_index:])

    def last_page():
        global last_model_index
        last_model_index -= len(cards)
        return update_cards(models[last_model_index:])

    # Card collection starts here
    with gr.Column(visible=is_token_set):
        with gr.Row():
            cards.append(C2())
            cards.append(C2())
        with gr.Row():
            cards.append(C2())
            cards.append(C2())
        with gr.Row():
            cards.append(C2())
            cards.append(C2())
        with gr.Row():
            cards.append(C2())
            cards.append(C2())
        with gr.Row():
            cards.append(C2())
            cards.append(C2())
        with gr.Row():
            last_btn = gr.Button("Previous", visible=False, interactive=False)
            next_btn = gr.Button("Next", visible=False, interactive=False)

    last_btn.click(
        last_page,
        None,
        outputs=reduce(lambda a, card: a + card.get_components(), cards, [])
        + [last_btn, next_btn],
    )
    next_btn.click(
        next_page,
        None,
        outputs=reduce(lambda a, card: a + card.get_components(), cards, [])
        + [last_btn, next_btn],
    )
    
    create_session_btn.click(create_session, None, None)

    get_session_page_source_btn.click(
        scape_models,
        None,
        outputs=reduce(lambda a, card: a + card.get_components(), cards, [])
        + [last_btn, next_btn],
    )

