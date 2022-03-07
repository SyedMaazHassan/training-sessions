let topic_counter = 1;
let all_topics = {};
let topic_redirect_url = null;

function confirmDeleteTopic() {
  window.location.href = topic_redirect_url;
}

function askToDeleteTopic(element) {
  let link = $(element).attr("href");
  topic_redirect_url = link;
  var myModal = new bootstrap.Modal(
    document.getElementById("confirmation-topic"),
    {
      keyboard: false,
    }
  );
  myModal.show();
  return false;
}

function formSubmitTopic() {
  let all_topics_values = Object.values(all_topics);
  if (all_topics_values.length > 0) {
    $("#all_topics_textarea").val(JSON.stringify(all_topics_values));
    $("#topic_form").submit();
  } else {
    $("#topic_error").text("Add at least 1 topic before saving!");
  }
  return;
}

function deleteTopic(id) {
  delete all_cats[id];
  $(`#topic_${id}`).remove();
  $("#topic_name").removeClass("is-valid");
}

function renderTopic(id, name) {
  let element = `<span 
                        id="topic_${id}"
                        class="p-2 border px-3 m-1 mb-1 ml-0 radius-100 bg-light d-flex" style="margin-left: 0px !important; width: fit-content; float: left;">
                        ${name}
                        &nbsp;
                        <i onclick="deleteTopic(${id})" class="material-icons my-0 mk-pointer" style="font-size:20px">close</i>
                    </span>`;
  $("#topic_container").prepend(element);
}

function addNewTopic() {
  let new_topic = $("#topic_name").val();
  if (new_topic) {
    new_topic = new_topic.trim();
    if (Object.values(all_topics).includes(new_topic)) {
      $("#topic_error").text("This topic already added!");
    } else {
      $("#topic_error").text("");
      $("#topic_name").removeClass("is-invalid");
      $("#topic_name").addClass("is-valid");
      all_topics[topic_counter] = new_topic;
      renderTopic(topic_counter, new_topic);
      $("#topic_name").val("");
      topic_counter++;
      return;
    }
  } else {
    $("#topic_error").text("Topic name is required!");
  }
  $("#topic_name").removeClass("is-valid");
  $("#topic_name").addClass("is-invalid");
}
