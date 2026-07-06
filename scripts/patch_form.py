#!/usr/bin/env python3
"""Rewrites the bundled template so the contact form's submit opens WhatsApp
with the user-entered values prefilled, instead of just flipping sent=true."""

import json
import re
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / "index.html"

OLD = "submit: () => this.setState({ sent: true }),"

NEW = """submit: () => {
        try {
          const tel = document.querySelector('input[type="tel"]');
          const box = tel && tel.parentElement;
          const inputs = box ? box.querySelectorAll('input') : [];
          const val = (i) => (inputs[i] && inputs[i].value.trim()) || '';
          const nombre = val(0), salon = val(1), telv = val(2), pobl = val(3);
          const num = (this.props && this.props.whatsappNumber) || '34628931419';
          const isCa = (this.state.lang || this.props.idiomaPorDefecto || 'ca') === 'ca';
          const msg = isCa
            ? 'Hola! Soc ' + (nombre || '[nom]') + ' del salo ' + (salon || '[salo]') + ' a ' + (pobl || '[poblacio]') + '. Vull provar Senyal. Telefon: ' + (telv || '[telefon]')
            : 'Hola! Soy ' + (nombre || '[nombre]') + ' del salon ' + (salon || '[salon]') + ' en ' + (pobl || '[poblacion]') + '. Quiero probar Senyal. Telefono: ' + (telv || '[telefono]');
          window.open('https://wa.me/' + num + '?text=' + encodeURIComponent(msg), '_blank', 'noopener');
        } catch (e) { console.error('wa submit', e); }
        this.setState({ sent: true });
      },"""


def main() -> int:
    html = HTML.read_text()
    m = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', html, re.S)
    if not m:
        print("template script not found", file=sys.stderr)
        return 1

    template = json.loads(m.group(2))
    if OLD not in template:
        print("submit line not found — bundle may have changed", file=sys.stderr)
        return 1
    if "wa.me/' + num" in template:
        print("already patched")
        return 0

    template = template.replace(OLD, NEW, 1)
    # Escape </script> so it can't close the outer <script> tag — JSON's \/ is
    # a legal escape for /. This mirrors the bootstrap code's own trick.
    serialized = json.dumps(template).replace("</script>", "<\\/script>")
    new_block = m.group(1) + serialized + m.group(3)
    HTML.write_text(html[: m.start()] + new_block + html[m.end() :])
    print("patched OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
