// prepares the progressbar element
function prepare_progressbar(element1, element2) {
  progressbar = document.getElementById("cardProgressBar");
  child = progressbar.children[0];

  var position = window.getComputedStyle(child).position;
  if (position === "absolute") {
    child.style.position = "relative";
  }

  return [element1, element2];
}
