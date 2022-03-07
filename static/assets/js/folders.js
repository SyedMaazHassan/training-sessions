let redirect_url = null;

function confirmDelete() {
  window.location.href = redirect_url;
}

function askToDelete(element) {
  let link = $(element).attr("href");
  redirect_url = link;
  $("#confirmation").show();
  var myModal = new bootstrap.Modal(document.getElementById("confirmation"), {
    keyboard: false,
  });
  myModal.show();
  return false;
}
