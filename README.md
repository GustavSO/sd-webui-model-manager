# Stable Diffusion webui Model Manager

A **work in progress** extension for [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui), with the aim of streamlining the downloading, organizing, and editing of the various types of models (Checkpoints, LoRAs, LyCORIS, TIs etc.)

![Alt Text](resources/early%20preview.gif)

## Development Strategy

Development will focus on one feature at a time. The current priority is optimizing the download functionality. The core features are: downloading, organizing, and editing. These features will be implemented in the mentioned order.

Each large feature improvement will be marked with a 0.X.0 version increase.

## Current Features
### Downloading
Fetch and download various models from [Civitai](https://civitai.com/)
- Supported model types:
  - Checkpoints
  - LoRA
  - LyCORIS
  - DoRA
  - Hypernetworks
  - Embeddings
- See and edit various properties before downloading
  - Target directory
  - Filename
  - Preview Image
  - Trigger Words
- Select which version of the model to download

### Auto Naming
An extensive suite of settings for automatic Filename modification upon fetching a model:
- Dynamic naming structuring using model attributes like base model, version, creator, etc.
- Filter characters from specific alphabets
- Exclude specific words or phrases
- Automatically trim whitespaces
- Remove illegal filename characters
- **Many more**

