# Model Manager

A very work in progress extension for AUTOMATIC1111's SD WebUI, with the aim of streamlining the management and download of the various types of models (Checkpoints, LoRAs, TIs etc.)

## Motivation & Goals

The motivation behind making this extension is rather simple. I've amassed quite a collection of models during my time of using Stable Diffusion and as I'm the person who like to keep my files structured I ended up spending a lot of time just sorting the different files. The excellent Civitai Helper extension did help to some extent, but a lot of time was still used on manually sorting and naming files. Hence, this extension, Model Manager

The goal of this extension is to alleviate the aforementioned waste of time by allowing the downloading/sorting/naming/metadata editing/etc. all from within the A1111 WebUI itself.

### Features

- Fetching and downloading models from Civitai
  - Types supported:
    - Checkpoints
    - LoRAs
    - Hypernetworks
    - Embeddings
    - LyCORIS
  - Allows for editing of various information before downloading:
    - Choose target directory
    - Choose filename
    - Choose preview image
  - Support for the new LoRA metadata functionality in A1111
    - When downloading a LoRA file, a .JSON file is saved in the same location. This contains various information, of note is activation words, allowing for easier use of downloaded LoRAs.


### Known issues:

- Some larger files (mostly checkpoints) sometimes doesn't download correctly.

### TODO:

- Indexing using SHA256 as to recognize already downloaded files
- A model editor page, for editing already installed models
- More streamlined download flow
- Settings page
