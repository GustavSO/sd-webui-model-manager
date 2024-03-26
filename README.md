# Model Manager

A **work in progress** extension for [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui), with the aim of streamlining the management, downloading, organizing, and editing of the various types of models (Checkpoints, LoRAs, LyCORIS, TIs etc.)

![Alt Text](resources/early%20preview.gif)

# Important Notice

Before installing this extension, please be aware of the following:

- This extension is still very much work-in-progress. Currently, it handles the downloading of models rather well. Other features like re-naming, deletion and moving of already installed features will come at a later date.

## Current Features

- Fetch and download various models types from [Civitai](https://civitai.com/)
  - Checkpoints
  - LoRAs
  - LyCORIS
  - Hypernetworks
  - Embeddings
- Select which version of a model to download
- Edit various properties before downloading
  - Target directory
    - Supports custom model paths passed to COMMAND_ARGS
  - Filename
  - Preview Image
  - ***More to come***
- Support the new built-in LoRA/LyCORIS metadata feature
  - When downloading a LoRA/LyCORIS model, a .JSON file is saved in the same location containing various information. Especially of note is activation words. These are added to the prompt automatically when selecting the LoRA/LyCORIS making them easier to immediately after downloading.
- Settings
  - Allow/disallow NSFW images
  - Auto-paste clipboard when fetching a model
  - ***More to come***

### Advanced/WIP features:

#### Scrape models from your Civitai Notifications

While this feature does work it requires some technical know-how and a GitHub account as it needs a Fine-Grained Token.

### Planned Features/Improvements:

- Improvement to the fetch and download functionality
  - Display more information about a fetched model
- Add various settings/options:
  - Provide filename suggestion based on a specific format (e.g. "filename [model version] (model creator)")
  - Change depth of subdirectories to list (Currently only lists immediate subdirectories)
- Add a "Manage/Organizer" page:
  - Provide various ways to edit, organize and search in already installed models.
- General improvements:
  - Issue an overwriting warning if a file already exists with the same name. Currently it will not allow you to save a model with the same name as an existing one
  - Indexing downloaded models using SHA256 as to recognize already downloaded models
  - Introduce some CSS styling

### Motivation & Goals

The motivation behind making this extension is rather simple. I've amassed quite a collection of different types of models (checkpoints, LoRAs, VAE, LyCORIS, you name it) during my time of using Stable Diffusion and as I'm generally the kind of person that like to keep my files neatly organized I ended up spending a lot of time manually managing, organizing and editing these models. The excellent Civitai Helper extension did help to some extent, but it didn't check all the boxes for my preference when I came to organizing. This meant that a lot of time was still being used on manually saving, sorting, re-naming the files. Hence, this extension, Model Manager

The goal of this extension is to alleviate the aforementioned waste of time by allowing the downloading, sorting, naming, editing, etc. all from within the A1111 WebUI itself.