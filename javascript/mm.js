
function handleModelManagerTabClick() {
  document
    .querySelector("#tabs .tab-nav")
    .addEventListener("click", function (event) {
      if (
        event.target.tagName === "BUTTON" &&
        event.target.textContent.trim() === "Model Manager"
      ) {
        console.log("Model Manager tab clicked");
        initializeDropdown();
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

// The dropdown. The bane of my existence. I hate it.
function initializeDropdown() {
  let js_btn = gradioApp().getElementById("js_init_dir_dropdown");

  if (!js_btn) {
    console.log("Dropdown button not found");
    return;
  }
  
  if (js_btn.textContent.trim() === "True") {
    console.log("Dropdown already initialized");
    return;
  }

  js_btn.click();
}

// Card Buttons
function addOnClickToButtons() {
  const tabs = ["img2img_extra_tabs", "txt2img_extra_tabs"].map((id) =>
    document.getElementById(id)
  );

  tabs.forEach((tab) => {
    if (tab) {
      const prefix = tab.id.split("_")[0] + "_";
      const buttons = tab.querySelectorAll("div > button:not(:first-child)");

      buttons.forEach((button) => {
        if (button.textContent.toLowerCase().includes("refresh")) {
          button.addEventListener("click", () => createCardButtons(tab)); // TODO: Actually add a refresh function - currently it has to be clicked twice
        } else {
          button.addEventListener("click", (event) => {
            console.log("Tab clicked: " + tab.id);
            const containerId =
              prefix +
              button.textContent.toLowerCase().trim().replace(" ", "_") +
              "_cards";
            console.log("Container ID: ", containerId);
            createCardButtons(tab, containerId);
          });
        }
      });
    }
  });
}

function createCardButtons(tab, containerId = null) {
  const observer = new MutationObserver((mutationsList, observer) => {
    const cardContainer = containerId
      ? tab.querySelector("#" + containerId)
      : tab;
    const cardDivs = cardContainer.querySelectorAll(".card");

    if (cardDivs.length > 0) {
      console.log("Card divs found: ", cardDivs.length);
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
  const svgIcon = createSVGIcon();
  newDiv.appendChild(svgIcon);

  newDiv.onclick = () => {
    const copyButton = cardDiv.querySelector(".copy-path-button");
    if (copyButton) {
      const dataAttribute = copyButton.getAttribute("data-clipboard-text");
      const jsonPath = dataAttribute.replace(/\.[^/.]+$/, `.json`);

      console.log("Model name: ", modelName);
      console.log("Model path: ", dataAttribute);
      console.log("GPT JSON path: ", jsonPath);

      openModelOnCivitai(jsonPath);
    }
  };

  return newDiv;
}

function createSVGIcon() {
  let iconSize = "1.8rem";
  const svgIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  setSVGAttributes(svgIcon, iconSize);
  addSVGPaths(svgIcon);

  return svgIcon;
}

function setSVGAttributes(svgElement, size) {
  svgElement.setAttribute("width", size);
  svgElement.setAttribute("height", size);
  svgElement.setAttribute("viewBox", "75 85 350 350");
  svgElement.setAttribute("fill", "white");
  svgElement.style.marginTop = size === "1.8rem" ? "-2px" : "0";
}

function addSVGPaths(svgElement) {
  const paths = [
    "M 352.79 218.85 L 319.617 162.309 L 203.704 162.479 L 146.28 259.066 L 203.434 355.786 L 319.373 355.729 L 352.773 299.386 L 411.969 299.471 L 348.861 404.911 L 174.065 404.978 L 87.368 259.217 L 174.013 113.246 L 349.147 113.19 L 411.852 218.782 L 352.79 218.85 Z",
    "M 304.771 334.364 L 213.9 334.429 L 169.607 259.146 L 214.095 183.864 L 305.132 183.907 L 330.489 227.825 L 311.786 259.115 L 330.315 290.655 Z M 278.045 290.682 L 259.294 259.18 L 278.106 227.488 L 240.603 227.366 L 221.983 259.128 L 240.451 291.026 Z",
  ];

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
        resolve(response);
      }
    });

    observer.observe(target, {
      attributes: true,
      childList: true,
      subtree: true,
      characterData: true,
    });

    setTimeout(() => {
      console.log(
        "Timeout for getting response from Gradio. Took: " + maxTimeout + "ms"
      );
      observer.disconnect();
      reject("Timeout");
    }, maxTimeout);
  });

function onPageLoad() {
  console.log("Page loaded");

  handleModelManagerTabClick();
  addOnClickToButtons();
}

onUiLoaded(onPageLoad);
