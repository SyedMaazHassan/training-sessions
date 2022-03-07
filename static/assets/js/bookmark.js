if (window.history.replaceState) {
  window.history.replaceState(null, null, window.location.href);
}

var myword = null;
function getSelectionText() {
  var text = "";
  var activeEl = document.activeElement;
  var activeElTagName = activeEl ? activeEl.tagName.toLowerCase() : null;
  if (
    activeElTagName == "textarea" ||
    (activeElTagName == "input" &&
      /^(?:text|search|password|tel|url)$/i.test(activeEl.type) &&
      typeof activeEl.selectionStart == "number")
  ) {
    text = activeEl.value.slice(activeEl.selectionStart, activeEl.selectionEnd);
  } else if (window.getSelection) {
    text = window.getSelection().toString();
  }
  return text;
}

function isValidBookmart(text) {
  let text_list = text.trim().split(" ");
  if (text_list.length < 3) {
    return false;
  }
  return true;
}

document.getElementById("render_content").onmouseup = function () {
  selected_text = getSelectionText();
  // new_string = selected_text.replaceAll("\n", " - ");
  // new_string = new_string.replaceAll("\t", " - ");
  if (selected_text) {
    myword = selected_text;

    if (!isValidBookmart(myword)) {
      alert("Kindly select at least 3 words to add as a bookmark!");
      return;
    }

    $("#id_content").val(myword);
    let myModal = new bootstrap.Modal(
      document.getElementById("bookmarkmodal"),
      {
        keyboard: false,
      }
    );
    myModal.show();
    $("#id_title").focus();
  }
};

$("textarea").css("height", "150px");
$("#id_source").attr("disabled", "disabled");
