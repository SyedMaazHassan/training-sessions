function renderBookmarks(id, my_bookmark_list) {
  const $box = document.getElementById(id);
  let text = $box.innerHTML;
  for (let i = 0; i < my_bookmark_list.length; i++) {
    console.log();
    let bookmark = my_bookmark_list[i];
    let search = bookmark.content;
    console.log(bookmark);
    const regex = new RegExp(search, "gi");
    text = text.replace(/(<mark class="highlight">|<\/mark>)/gim, "");
    mycontent = `<p class="my-0 highlight-{bookmark.color}">${bookmark.content}</p>`;
    text = text.replace(
      regex,
      `<span title="${bookmark.title}" onclick="speak('${bookmark.content}')" data-bs-placement="top" data-bs-html="true"  data-bs-custom-class="popborder border-${bookmark.color}" data-bs-trigger="hover focus" data-bs-toggle="popover" data-bs-content="${bookmark.content}<br><br><b>Comment: </b><br>${bookmark.comment}" class="mk-pointer highlight-${bookmark.color}">$&</span>`
    );
  }
  $box.innerHTML = text;

  var popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]')
  );
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
}

function speak(text) {
  window.speechSynthesis.cancel();
  var msg = new SpeechSynthesisUtterance();
  msg.text = text;
  msg.lang = "en";
  window.speechSynthesis.speak(msg);
}

window.onbeforeunload = function () {
  window.speechSynthesis.cancel();
  console.log("Cancelling speach...");
  return;
};
