var redirect_url = null;

function applyFilter(type) {
  let current_url = window.location.href.split("?")[0];
  let my_list = ["all", "word", "phrase", "term"];
  if (type && my_list.includes(type)) {
    let new_url = `${current_url}?type=${type}`;
    window.location.href = new_url;
  }
}

$(document).ready(function () {
  $(".content").richText();
});

$("#term-form").submit(function () {
  let content = $($("#myText").val()).text();
  if (content) {
    $("#main-term-error").text("");
    return true;
  }
  $("#main-term-error").text(
    "Description of the term is required with formatting!"
  );
  return false;
});

function confirmDelete() {
  window.location.href = redirect_url;
}

function askToDelete(element) {
  let link = $(element).attr("href");
  redirect_url = link;
  let myModal = new bootstrap.Modal(document.getElementById("confirmation"), {
    keyboard: false,
  });
  myModal.show();
  return false;
}

$(".term-title-side").each(function () {
  let prev_string = $(this).text();
  $(this).text(prev_string.charAt(0).toUpperCase() + prev_string.slice(1));
});
