#!/bin/sh
# Instala os menus na pasta do usuário (não precisa de sudo).
#   ./instalar.sh
# Os scripts vão para ~/.local/bin e o módulo de notificações para
# ~/.local/share/labwc-menus. Depois, use os exemplos da pasta "exemplos"
# para ligar os menus à barra (Waybar) e às teclas (labwc).
set -e
cd "$(dirname "$0")"

mkdir -p "$HOME/.local/bin" "$HOME/.local/share/labwc-menus" "$HOME/.local/share/applications"
for f in bin/*; do
    install -m 755 "$f" "$HOME/.local/bin/"
    echo "instalado: ~/.local/bin/$(basename "$f")"
done
install -m 644 lib/notificacoes.py "$HOME/.local/share/labwc-menus/"
install -m 644 exemplos/org.labwc.Configuracoes.desktop "$HOME/.local/share/applications/"
echo
echo "Pronto. Próximos passos:"
echo "  1. Junte exemplos/waybar-config.jsonc e exemplos/waybar-style.css à sua configuração do Waybar."
echo "  2. Junte exemplos/labwc-rc.xml ao seu ~/.config/labwc/rc.xml e rode: labwc --reconfigure"
echo "  3. Confira se ~/.local/bin está no seu PATH."
