# Stable Diffusion webui Model Manager 
### A **work in progress** extension for [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui), with the aim of streamlining the downloading, organizing, and editing of the various types of models
---

https://github.com/GustavSO/sd-webui-model-manager/assets/65391253/7bcac98f-1600-4b2c-be91-6eeda6192c19

# Features 💡
### Fetch and download various models from [Civitai](https://civitai.com/) ⬇️
- Supports multiple different model types:
  - Checkpoints
  - LoRA
  - LyCORIS
  - DoRA
  - Hypernetworks
  - Embeddings

### View and Edit Model Details 🔍
  - See and change many properties of the model before downloading it:
    - Customize the filename
    - Choose the target directory
    - Select preview image
    - Adjust trigger words

### Auto Naming 🏷️
- An extensive suite of settings for automatic filename modification upon model retrieval:
  - Dynamic naming structuring using model attributes like base model, version, creator, etc.
  - Filter out characters from specific alphabets
  - Exclude specific words or phrases
  - Automatically trim excess whitespaces
  - Eliminate illegal filename characters
  - **And much more**

 ### Auto Folder Selection 📂
 - Save time by setting default folders for each main tag on Civitai, eliminating the need for manual folder selection during downloads.
   - *Currently only works for LoRA, DoRA and LyCORIS*

### Quick Access to Source 🌐
- Easily open the original download page for any model, allowing you to quickly revisit and explore the source.-
  - *Currently only works on models downloaded using Model Manager.*
 
### Highly Customizable 🎛️
- Extensive settings provide numerous options for users to tailor features to their specific needs and preferences.

### Work-in-progress 🚧
- Scrape models from your Civitai notifications page
