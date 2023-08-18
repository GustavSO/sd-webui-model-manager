# Model Manager

A **very work in progress** extension for AUTOMATIC1111's SD WebUI, with the aim of streamlining the management, downloading, organizing, and editing of the various types of models (Checkpoints, LoRAs, TIs etc.)

![Alt Text](scripts/resources/early%20preview.gif)


# Important Notice

Before installing this extension, please be aware of the following two things:

- This extension is being developed alongside version 1.6.0 of A1111's WebUI in which Gradio will see a version bump from 3.32.0 to 3.39.0. Some features made available in this version bump are used in this extension, however it still seems to work with version 1.5.1 of A1111's WebUI with some quirks and errors. For the best possible experience, please install this extension on a build from the 'dev' branch of A1111's WebUI.
- As mentioned, this extension is still very much WIP. While it is still in version 0.0.X please just consider it as "preview release". There will be bugs and errors.

I intend for this extension to be released in a somewhat stable version, coinciding with the release of version 1.6.0 of A1111's WebUI. 


### Features

- Fetching and downloading models from Civitai
  - Support for:
    - Checkpoints
    - LoRAs
    - Hypernetworks
    - Embeddings
    - LyCORIS
    - **More to come**
- Edit various properties before downloading:
  - Target directory
  - Filename
  - Image
  - **More to come**
- Support the new built-in LoRA/LyCORIS metadata feature:
  - When downloading a LoRA/LyCORIS model, a .JSON file is saved in the same location containing various information. Especially of note is activation words. These are added to the prompt automatically when selecting the LoRA/LyCORIS making them easier to immediately  after downloading.


### Known issues:

- In rare occasions, the connection stream to Civitai closes without raising errors. This results in some models being saved before all data has been writing to the file, leaving them unusable.

### Planned Features:

- Indexing downloaded models using SHA256 as to recognize already downloaded models
- A model editor/organizer page, for editing and organizer already installed models
- More streamlined download flow
- Settings page

## Motivation & Goals

The motivation behind making this extension is rather simple. I've amassed quite a collection of models during my time of using Stable Diffusion and as I'm the person who like to keep my files structured I ended up spending a lot of time just sorting the different files. The excellent Civitai Helper extension did help to some extent, but a lot of time was still used on manually sorting and naming files. Hence, this extension, Model Manager

The goal of this extension is to alleviate the aforementioned waste of time by allowing the downloading/sorting/naming/metadata editing/etc. all from within the A1111 WebUI itself.