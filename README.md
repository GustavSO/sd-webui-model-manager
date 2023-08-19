# Model Manager

A **very work in progress** extension for [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui), with the aim of streamlining the management, downloading, organizing, and editing of the various types of models (Checkpoints, LoRAs, TIs etc.)

![Alt Text](resources/early%20preview.gif)

# Important Notice

Before installing this extension, please be aware of the following two things:

- This extension is being developed alongside version 1.6.0 of A1111's WebUI in which Gradio will see a version bump from 3.32.0 to 3.39.0. Some features made available in this version bump are used in this extension, however it still seems to work with version 1.5.1 of A1111's WebUI with some minor quirks and errors. \
For this reason, it is <mark>highly recommended</mark> that you install this extension on a build from the 'dev' branch of A1111's WebUI or wait for the official release of 1.6.0
- As mentioned, this extension is still very much WIP. While it is still in version 0.0.X please just consider it as "preview release". There will be bugs and errors.

I intend for this extension to be in a somewhat stable state when version 1.6.0 of the WebUI is released or shortly after

## Current Features

- Fetch and download various models types from [Civitai](https://civitai.com/)
  - Checkpoints
  - LoRAs
  - Hypernetworks
  - Embeddings
  - LyCORIS
  - ***More to come***
- Edit various properties before downloading
  - Target directory
    - Supports custom model paths passed to COMMAND_ARGS
  - Filename
  - Preview Image
  - ***More to come***
- Support the new built-in LoRA/LyCORIS metadata feature
  - When downloading a LoRA/LyCORIS model, a .JSON file is saved in the same location containing various information. Especially of note is activation words. These are added to the prompt automatically when selecting the LoRA/LyCORIS making them easier to immediately after downloading.


### Known Issues:

- In rare occasions, the connection stream to Civitai closes without raising errors. This results in some models being saved before all data has been written to the file, leaving them unusable.

### Planned Features/Improvements:

- Improvement to the fetch and download functionality
  - Display more information about a fetched model
  - Make it possible to select which version of the fetched model to display/download.
- Add various settings/options:
  - Allow/disallow NSFW images
  - Auto-paste clipboard
  - Provide filename suggestion based on a specific format (e.g. "filename [model version] (model creator)")
  - Change depth of subdirectories to list (Currently only lists immediate subdirectories)
  - And more
- Add a "Manage/Organizer" page:
  - Provide various ways to edit, organize and search in already installed models.
- General improvements:
  - Issue an overwriting warning if a file already exists with the same name
  - Indexing downloaded models using SHA256 as to recognize already downloaded models
  - Introduce some CSS styling

### Motivation & Goals

The motivation behind making this extension is rather simple. I've amassed quite a collection of different types of models (checkpoints, LoRAs, VAE, LyCORIS, you name it) during my time of using Stable Diffusion and as I'm generally the kind of person that like to keep my files neatly organized I ended up spending a lot of time manually managing, organizing and editing these models. The excellent Civitai Helper extension did help to some extent, but it didn't check all the boxes for my preference when I came to organizing. This meant that a lot of time was still being used on manually saving, sorting, re-naming the files. Hence, this extension, Model Manager

The goal of this extension is to alleviate the aforementioned waste of time by allowing the downloading, sorting, naming, editing, etc. all from within the A1111 WebUI itself.