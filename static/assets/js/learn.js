$("#message-container").scrollTop($("#message-container")[0].scrollHeight);
console.log(titles_boomark);
var tooltipTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
);

var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

let rich_text_dict = {};

if (serialized_learning) {
  rich_text_dict = serialized_learning;
  if (to_open != "None") {
    launch_text(to_open);
  }
}

function get_current_time() {
  var date = new Date();
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var ampm = hours >= 12 ? "p.m." : "a.m.";
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? "0" + minutes : minutes;
  var strTime = hours + ":" + minutes + " " + ampm;
  return strTime;
}

function clip_text(string, max_length) {
  if (!string || string.length <= max_length) {
    return string;
  }
  return string.slice(0, max_length) + "...";
}

function binarySearch(arr, x) {
  x = x.toLowerCase();
  let l = 0,
    r = arr.length - 1;
  while (l <= r) {
    let m = l + Math.floor((r - l) / 2);

    let toCompareWith = arr[m][1].toLowerCase();

    let res = x.localeCompare(toCompareWith);

    // Check if x is present at mid
    if (res == 0) return m;

    // If x greater, ignore left half
    if (res > 0) l = m + 1;
    // If x is smaller, ignore right half
    else r = m - 1;
  }

  return -1;
}

function complete_render(content_to_render) {
  $("#message-container").append(content_to_render);
  $("#query").val("");
  $("#message-container").scrollTop($("#message-container")[0].scrollHeight);
}

function post_not_found(title, time = null) {
  time = get_current_time();
  let link = create_term_url + "?title=" + title;
  let content = `
            <div class="card p-2 px-3 radius-10 mb-2 message second-person">
                <div class="align-items-center mb-1 d-flex">
                    <h5 class="my-0 text-dark">${clip_text(title, 30)}</h5>
                    <div style="height: fit-content;">
                        <a href="${link}" 
                            data-bs-toggle="tooltip" data-bs-placement="right" title="Create this term"
                            class="btn text-success bg-white mx-1 p-0 my-0 border radius-100 mk-pointer" >
                            <i class="material-icons p-0 my-0">add</i>
                        </a >
                    </div >
                </div >
            
                <p class="mb-1">This term doesn't exist in record.</p>

                <div class="d-flex justify-content-end message-second-time">
                    ${time}
                </div>
            </div>
        `;
  complete_render(content);
}
let full_open = null;

$("#speak_icon").on("click", function () {
  if (full_open) {
    speak(full_open);
  }
});

function launch_text(url) {
  $("#no_render_container").hide();

  $.ajax({
    url: url,
    type: "GET",
    success: (response) => {
      if (!response.status) {
        alert("Something went wrong");
        return;
      }

      let link_a;
      let source_input;
      if (response.data.type == "bookmark") {
        link_a = `bookmarks/`;
        source_input = response.data.object.source;
      } else {
        source_input = response.data.object.id;
        link_a = `journal/terms/${response.data.object.id}/`;
      }
      console.log(response.data);
      $("#render_link").attr("href", link_a);
      $("#id_source_input").val(source_input);
      $("#render_title").text(response.data.object.title);
      $("#render_content").text(response.data.object.content);
      $("#render_category").text(response.data.object.category);
      $("#render_topics").children().remove();
      response.data.object.topics.forEach((topic) => {
        $("#render_topics").append(`
            <span class="p-1 border px-3 m-1 mb-1 ml-0 radius-100 bg-light d-flex"
                style="margin-left: 0px !important; width: fit-content; float: left;">
                ${topic}
            </span>                
        `);
      });
      full_open = response.data.object.content;
      if (response.data.type == "term") {
        renderBookmarks("render_content", response.data.object.bookmarks);
      }
      $("#my-spinner").show();
      $("#render_container").show();
    },
  });
  // if (term_id in rich_text_dict) {
  // $("#id_source_input").val(term_id);
  //   let term_object = rich_text_dict[term_id];
  //   let link_a = `journal/terms/${term_id}/`;
  //   $("#render_link").attr("href", link_a);
  //   $("#render_title").text(term_object.title);
  //   $("#render_content").html(term_object.content);
  //   $("#render_category").text(term_object.category);
  //   $("#render_topics").children().remove();
  //   term_object.topics.forEach((topic) => {
  //     $("#render_topics").append(`
  //                   <span class="p-1 border px-3 m-1 mb-1 ml-0 radius-100 bg-light d-flex"
  //                       style="margin-left: 0px !important; width: fit-content; float: left;">
  //                       ${topic}
  //                   </span>
  //               `);
  //   });
  //   $("#no_render_container").hide();
  //   $("#render_container").show();
  // } else {
  //   alert("Not found");
  // }
}

if (to_open != "None") {
  console.log(to_open);
  launch_text(`term/${to_open}`);
}

function post_message(message, time, status, type = "term", id = null) {
  let mycontent;

  if (status == "second" && id) {
    if (type == "bookmark") {
      link_a = `bookmark/${id}`;
    } else {
      link_a = `term/${id}`;
    }
    mycontent = message.content;
    content = `
                <div class="card p-2 px-3 radius-10 mb-2 message second-person">
                    <div class="align-items-center mb-1 d-flex">
                        <h5 class="my-0 text-dark">${clip_text(
                          message.title,
                          30
                        )}</h5>
                        <div style="height: fit-content;">
                            <div onclick="launch_text('${link_a}')" 
                                data-bs-toggle="tooltip" data-bs-placement="right" title="See formatted explanation"
                                class="text-success bg-white mx-2 p-0 my-0 radius-100 mk-pointer">
                                <i class="material-icons p-0 my-0"  style="font-size:18px">launch</i>
                            </div>
                        </div >
                    </div >
                
                    <p class="mb-1" title="${mycontent}">${clip_text(
      mycontent,
      526
    )}</p>

                    <div class="d-flex justify-content-end message-second-time">
                        ${time}
                    </div>
                </div>
            `;
  } else {
    mycontent = message;
    content = `
                <div class="card p-2 px-3 radius-10 mb-2 message ${status}-person">
                    <p class="mb-1">${mycontent}</p>
                    <div class="d-flex justify-content-end message-${status}-time">
                        ${time}
                    </div>
                </div>
            `;
  }

  // rendering only text
  complete_render(content);
}

function post_second_message(message, time, type = "term", id = null) {
  post_message(message, time, "second", type, id);
}

function post_first_message(message, time) {
  post_message(message, time, "first");
}

$("#query").keyup(function () {
  if (this.value) {
    $("#query-error").text("");
  }
});

function send_query_to_db(query, actual_query, type, not_found = false) {
  return $.ajax({
    url: query_to_send_url,
    type: "GET",
    data: `type=${type}&query=${query}&not_found=${not_found}&actual_query=${actual_query}`,
  });
}

function new_send_query_to_db(object) {
  return $.ajax({
    url: new_query_to_send_url,
    type: "GET",
    data: object,
  });
}

function toggle_typing(status) {
  if (status == "show") {
    $("#typing-gif").css("opacity", "1");
  } else if (status == "hide") {
    $("#typing-gif").css("opacity", "0");
  }
}

async function send_query() {
  let query = $("#query").val();
  if (!query) {
    $("#query-error").text("Write term to learn it!");
    return;
  }

  toggle_typing("show");
  await post_first_message(query, get_current_time());
  let query_index = binarySearch(titles_array, query);
  let bookmark_index = binarySearch(titles_boomark, query);
  console.log(bookmark_index);

  let request_object = { query: query };
  let response = await new_send_query_to_db(request_object);
  if (response.status) {
    setTimeout(() => {
      // rich_text_dict[term_id] = response.data;
      console.log(response);
      if (response.not_found) {
        post_not_found(query);
      } else {
        if (response.data.hasOwnProperty("term")) {
          post_second_message(
            response.data.term,
            "10:15 PM",
            "term",
            response.data.term.id
          );
        }
        if (response.data.hasOwnProperty("bookmark")) {
          post_second_message(
            response.data.bookmark,
            "10:15 PM",
            "bookmark",
            response.data.bookmark.id
          );
        }
      }
      toggle_typing("hide");
    }, 500);
  } else {
    alert("something went wrong");
  }

  // if (bookmark_index == -1) {
  //   let response = await send_query_to_db(null, query, "bookmark", true);
  //   if (response.status) {
  //     setTimeout(() => {
  //       post_not_found(query);
  //       toggle_typing("hide");
  //     }, 500);
  //   } else {
  //     alert("Something went wrong!");
  //   }
  // } else {
  //   let term_id = titles_array[query_index][0];
  //   let response = await send_query_to_db(term_id, query, "bookmark");
  //   if (response.status) {
  //     setTimeout(() => {
  //       rich_text_dict[term_id] = response.data;
  //       post_second_message(response.data, "10:15 PM", term_id);
  //       toggle_typing("hide");
  //     }, 500);
  //   } else {
  //     alert("Something went wrong!");
  //   }
  // }

  // if (query_index == -1) {
  //   let response = await send_query_to_db(null, query, "term", true);
  //   if (response.status) {
  //     setTimeout(() => {
  //       post_not_found(query);
  //       toggle_typing("hide");
  //     }, 500);
  //   } else {
  //     alert("Something went wrong!");
  //   }
  // } else {
  //   let term_id = titles_array[query_index][0];
  //   let response = await send_query_to_db(term_id, query, "term");
  //   if (response.status) {
  //     setTimeout(() => {
  //       rich_text_dict[term_id] = response.data;
  //       post_second_message(response.data, "10:15 PM", term_id);
  //       toggle_typing("hide");
  //     }, 500);
  //   } else {
  //     alert("Something went wrong!");
  //   }
  // }
}

$("#query").keypress(function (event) {
  var keycode = event.keyCode ? event.keyCode : event.which;
  if (keycode == "13") {
    send_query();
  }
});
