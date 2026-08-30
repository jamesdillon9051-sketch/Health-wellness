/* ==========================================================================
   HEALTH WELLNESS — forms.js
   Submits the contact and signup forms to Formspree over fetch, so the reader
   stays on the page instead of being bounced to a third-party thank-you screen.

   Progressive enhancement: with JS off, the contact form still posts normally
   to its `action`. Set the IDs in config.js — until you do, both forms say so
   plainly rather than swallowing what someone typed.
   ========================================================================== */
(function () {
  'use strict';

  var cfg = window.SITE_CONFIG || {};

  var ID_FOR = {
    contact: cfg.formspreeContactId,
    signup:  cfg.formspreeSignupId
  };

  var MSG = {
    sending:   'Sending…',
    okContact: 'Thanks — that has arrived. I reply to everything, usually within a few days.',
    okSignup:  'You are on the list. Check your inbox for a confirmation.',
    fail:      'That did not send. Try again, or email me directly.',
    offline:   'You appear to be offline — the message was not sent.',
    unwired:   'This form is not connected yet. Add your Formspree ID to assets/js/config.js.'
  };

  function status(form, text, state) {
    var el = form.querySelector('.form-status');
    if (!el) return;
    el.textContent = text;
    el.hidden = !text;
    el.className = 'form-status' + (state ? ' is-' + state : '');
  }

  Array.prototype.forEach.call(
    document.querySelectorAll('form[data-form]'),
    function (form) {
      var kind = form.getAttribute('data-form');
      var id = ID_FOR[kind];
      var button = form.querySelector('button[type="submit"], button:not([type])');

      if (id) form.setAttribute('action', 'https://formspree.io/f/' + id);

      form.addEventListener('submit', function (e) {
        if (!id) {                       // not configured — say so, lose nothing
          e.preventDefault();
          status(form, MSG.unwired, 'error');
          return;
        }
        if (!window.fetch) return;       // let the browser post it the old way

        e.preventDefault();
        if (form.dataset.busy === '1') return;
        form.dataset.busy = '1';

        var label = button ? button.textContent : '';
        if (button) { button.disabled = true; button.textContent = MSG.sending; }
        status(form, MSG.sending, 'busy');

        fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: { Accept: 'application/json' }
        })
          .then(function (res) {
            if (!res.ok) throw new Error(res.status);
            form.reset();
            status(form, kind === 'signup' ? MSG.okSignup : MSG.okContact, 'ok');
          })
          .catch(function () {
            status(form, navigator.onLine === false ? MSG.offline : MSG.fail, 'error');
          })
          .then(function () {
            form.dataset.busy = '';
            if (button) { button.disabled = false; button.textContent = label; }
          });
      });
    }
  );
})();
