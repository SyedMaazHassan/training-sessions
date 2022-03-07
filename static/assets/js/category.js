let cat_counter = 1;
let all_cats = {};
let cat_redirect_url = null;

function confirmDelete() {
  window.location.href = cat_redirect_url;
}

function askToDelete(element) {
  let link = $(element).attr("href");
  cat_redirect_url = link;
  $("#confirmation").show();
  var myModal = new bootstrap.Modal(document.getElementById("confirmation"), {
    keyboard: false,
  });
  myModal.show();
  return false;
}

function formSubmit() {
  let all_cats_values = Object.values(all_cats);
  if (all_cats_values.length > 0) {
    $("#all_cats_textarea").val(JSON.stringify(all_cats_values));
    $("#cat_form").submit();
  } else {
    $("#cat_error").text("Add at least 1 category before saving!");
  }
  return;
}

function deleteCat(id) {
  delete all_cats[id];
  $(`#cat_${id}`).remove();
  $("#cat_name").removeClass("is-valid");
}

function renderCat(id, name) {
  let element = `<span 
                            id="cat_${id}"
                            class="p-2 border px-3 m-1 mb-1 ml-0 radius-100 bg-light d-flex" style="margin-left: 0px !important; width: fit-content; float: left;">
                            ${name}
                            &nbsp;
                            <i onclick="deleteCat(${id})" class="material-icons my-0 mk-pointer" style="font-size:20px">close</i>
                        </span>`;
  $("#cat_container").prepend(element);
}

function addNewCat() {
  let new_category = $("#cat_name").val();
  if (new_category) {
    new_category = new_category.trim();
    if (Object.values(all_cats).includes(new_category)) {
      $("#cat_error").text("This category already added!");
    } else {
      $("#cat_error").text("");
      $("#cat_name").removeClass("is-invalid");
      $("#cat_name").addClass("is-valid");
      all_cats[cat_counter] = new_category;
      renderCat(cat_counter, new_category);
      $("#cat_name").val("");
      cat_counter++;
      return;
    }
  } else {
    $("#cat_error").text("Category name is required!");
  }
  $("#cat_name").removeClass("is-valid");
  $("#cat_name").addClass("is-invalid");
}
