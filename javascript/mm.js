// Global variables
let currentTab;

// Add event listener to Model Manager tab
// The event doesn't do anything yet
function handleModelManagerTabClick() {
  document
    .querySelector("#tabs .tab-nav")
    .addEventListener("click", function (event) {
      if (
        event.target.tagName === "BUTTON" &&
        event.target.textContent.trim() === "Model Manager"
      ) {
        console.log("Model Manager tab clicked");
      }
    });
}

function addTagRefreshButton() {
  const controls = [
    "txt2img_textual_inversion_controls",
    "txt2img_hypernetworks_controls",
    "txt2img_checkpoints_controls",
    "txt2img_lora_controls",
    "img2img_textual_inversion_controls",
    "img2img_hypernetworks_controls",
    "img2img_checkpoints_controls",
    "img2img_lora_controls",
  ].map((id) => document.getElementById(id));

  controls.forEach((control) => {
    if (control) {
      const tagDiv = document.createElement("div");
      tagDiv.id = control.id + "_extra_tag";
      tagDiv.className = "extra-network-control--tag";
      tagDiv.title = "Refresh Model Manager card buttons";
      tagDiv.onclick = () => {
        refreshAllCardButtons();
      };
      tagDiv.appendChild(tagSvgIcon());

      control.appendChild(tagDiv);
    }
  });
}

// Progress Bar
function initializeProgressbar(element1, element2) {
  progressbar = document.getElementById("cardProgressBar");
  child = progressbar.children[0];
  console.log(child);

  var position = window.getComputedStyle(child).position;
  if (position === "absolute") {
    child.style.position = "relative";
  }

  return [element1, element2];
}

// Card Buttons
function attachButtonClickEvents() {
  const tabs = ["img2img_extra_tabs", "txt2img_extra_tabs"].map((id) =>
    document.getElementById(id)
  );

  const button_text = [
    "Textual Inversion",
    "Hypernetworks",
    "Checkpoints",
    "Lora",
  ];

  // Find all the buttons in the tabs with the text from button_text
  tabs.forEach((tab) => {
    if (tab) {
      currentTab = tab;
      const prefix = tab.id.split("_")[0] + "_";
      tab.addEventListener("click", function (event) {
        if (
          event.target.tagName === "BUTTON" &&
          button_text.includes(event.target.textContent.trim())
        ) {
          const containerId =
            prefix +
            event.target.textContent.toLowerCase().trim().replace(" ", "_") +
            "_cards";
          createCardButtons(tab, containerId);
        }
      });
    }
  });
}

function refreshAllCardButtons() {
  const cardDivs = currentTab.querySelectorAll(".card");
  processCardDivs(cardDivs);
}

function createCardButtons(tab, containerId = null) {
  const observer = new MutationObserver((mutationsList, observer) => {
    const cardContainer = containerId
      ? tab.querySelector("#" + containerId)
      : tab;
    const cardDivs = cardContainer.querySelectorAll(".card");

    if (cardDivs.length > 0) {
      observer.disconnect();
      clearTimeout(timeoutId);
      processCardDivs(cardDivs);
    }
  });

  observer.observe(tab, { childList: true, subtree: true });

  const timeoutId = setTimeout(() => {
    console.log("Timeout for checking card divs. Took: " + 5000 + "ms");
    observer.disconnect();
  }, 5000);
}

function processCardDivs(cardDivs) {
  cardDivs.forEach((cardDiv) => {
    // If it already has a button, skip
    if (cardDiv.querySelector(".mm-open-civit.card-button")) return;

    const buttonRow = cardDiv.querySelector(".button-row");
    if (!buttonRow) return;

    buttonRow.addEventListener("click", (event) => {
      event.stopPropagation();
    });

    if (!buttonRow.querySelector(".mm-open-civit.card-button")) {
      const modelName = cardDiv
        .querySelector(".actions .name")
        ?.textContent.trim();
      if (!modelName) return;

      const cardButtonDiv = createNewButton(modelName, cardDiv);
      buttonRow.insertBefore(cardButtonDiv, buttonRow.firstChild);
    }
  });
}

function createNewButton(modelName, cardDiv) {
  const newDiv = document.createElement("div");
  newDiv.className = "mm-open-civit card-button";

  const svgIcon = cardSvgIcon();
  newDiv.appendChild(svgIcon);

  newDiv.onclick = () => {
    const copyButton = cardDiv.querySelector(".copy-path-button");
    if (copyButton) {
      const dataAttribute = copyButton.getAttribute("data-clipboard-text"); // Kinda sketchy will break if the attribute changes
      const jsonPath = dataAttribute.replace(/\.[^/.]+$/, `.json`);

      openModelOnCivitai(jsonPath);
    }
  };

  return newDiv;
}

function addSVGPaths(svgElement, paths) {
  paths.forEach((d) => {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", d);
    svgElement.appendChild(path);
  });
}

async function openModelOnCivitai(jsonFile) {
  sendMessageToGradio(jsonFile);

  let jsOpenCivitBtn = gradioApp().getElementById("js_open_model_btn");
  jsOpenCivitBtn.click();

  let response = "";
  try {
    response = await getResponseFromGradio();
  } catch (error) {
    console.error("Error getting response from Gradio: ", error);
  }

  console.log("Response from Gradio: ", response);
  if (response !== "None") {
    window.open(response, "_blank");
  }
}

function cardSvgIcon() {
  const svgIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  const paths = [
    "M 352.79 218.85 L 319.617 162.309 L 203.704 162.479 L 146.28 259.066 L 203.434 355.786 L 319.373 355.729 L 352.773 299.386 L 411.969 299.471 L 348.861 404.911 L 174.065 404.978 L 87.368 259.217 L 174.013 113.246 L 349.147 113.19 L 411.852 218.782 L 352.79 218.85 Z",
    "M 304.771 334.364 L 213.9 334.429 L 169.607 259.146 L 214.095 183.864 L 305.132 183.907 L 330.489 227.825 L 311.786 259.115 L 330.315 290.655 Z M 278.045 290.682 L 259.294 259.18 L 278.106 227.488 L 240.603 227.366 L 221.983 259.128 L 240.451 291.026 Z",
  ];

  svgIcon.setAttribute("width", "1.8rem");
  svgIcon.setAttribute("height", "1.8rem");
  svgIcon.setAttribute("viewBox", "75 85 350 350");
  svgIcon.setAttribute("fill", "white");
  // svgElement.style.marginTop = size === "1.8rem" ? "-2px" : "0";
  addSVGPaths(svgIcon, paths);

  return svgIcon;
}

function tagSvgIcon() {
  const svgIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  const svgPaths = [
    "M 486.82 21.213 L 465.607 0 l -42.768 42.768 H 238.991 L 0 281.759 L 205.061 486.82 l 238.992 -238.991 V 63.98 L 486.82 21.213 Z M 414.053 235.403 L 205.061 444.394 L 42.427 281.759 L 251.418 72.768 h 141.421 l -40.097 40.097 c -14.56 -6.167 -32.029 -3.326 -43.898 8.543 c -15.621 15.621 -15.621 40.948 0 56.569 c 15.621 15.621 40.948 15.621 56.568 0 c 11.869 -11.869 14.71 -29.338 8.543 -43.898 l 40.097 -40.097 V 235.403 Z",
  ];

  svgIcon.setAttribute("width", "1.5rem");
  svgIcon.setAttribute("height", "1.5rem");
  svgIcon.setAttribute("viewBox", "0 0 486.82 486.82");
  svgIcon.setAttribute("fill", "var(--input-placeholder-color)");
  addSVGPaths(svgIcon, svgPaths);

  return svgIcon;
}

//----------------------
//-Gradio Communication-
//----------------------
function sendMessageToGradio(message) {
  let target = gradioApp().querySelector("#from_js textarea");

  if (target && message) {
    target.value = message;
    target.dispatchEvent(new Event("input"));
  }
}

const getResponseFromGradio = (maxTimeout = 5000) =>
  new Promise((resolve, reject) => {
    const target = gradioApp().querySelector("#to_js textarea");

    if (!target) {
      return reject("Textarea not found");
    }

    const observer = new MutationObserver(() => {
      if (target.value) {
        let response = target.value;

        // Clear the textarea
        target.value = "";
        target.dispatchEvent(new Event("input"));

        observer.disconnect();
        clearTimeout(timeoutId);
        resolve(response);
      }
    });

    observer.observe(target, {
      attributes: true,
      childList: true,
      subtree: true,
      characterData: true,
    });

    const timeoutId = setTimeout(() => {
      console.log(
        "Timeout for getting response from Gradio. Took: " + maxTimeout + "ms"
      );
      observer.disconnect();
      reject("Timeout");
    }, maxTimeout);
  });

function onPageLoad() {
  console.log("MM.js loaded");

  // handleModelManagerTabClick(); // Not used yet
  attachButtonClickEvents(); // Stupid name, I know
  addTagRefreshButton();
}

onUiLoaded(onPageLoad);
