(function () {
  var dlg = document.querySelector('.player');
  var video = dlg.querySelector('video');
  var title = dlg.querySelector('h2');
  var note = dlg.querySelector('.caption p');

  function open(id) {
    var f = window.FILMS[id];
    if (!f) return;
    title.textContent = f.title;
    note.textContent = f.note;
    video.poster = f.poster;
    video.src = f.src;
    dlg.showModal();
    video.play().catch(function () {});   // a browser that refuses autoplay still shows the controls
  }

  document.querySelectorAll('[data-film]').forEach(function (el) {
    el.addEventListener('click', function (ev) {
      ev.preventDefault();
      open(el.getAttribute('data-film'));
    });
  });
  dlg.querySelector('.close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (ev) { if (ev.target === dlg) dlg.close(); });
  dlg.addEventListener('close', function () { video.pause(); video.removeAttribute('src'); video.load(); });

  var copy = document.querySelector('.copy');
  if (copy) copy.addEventListener('click', function () {
    var text = document.querySelector('.cmd code').textContent;
    var label = copy.textContent;
    navigator.clipboard.writeText(text).then(function () {
      copy.textContent = copy.getAttribute('data-done');
      setTimeout(function () { copy.textContent = label; }, 1600);
    }).catch(function () {});
  });
})();
