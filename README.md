# labwc-menus-gtk

Menus e painéis no estilo do GNOME/Zorin OS para quem usa o **[labwc](https://labwc.github.io/)** (Wayland) com a barra **Waybar**: menu de aplicativos, tela de Configurações, calendário com central de notificações, e menus da barra superior para som, Wi-Fi, energia e pendrives.

Todos são pequenos programas em **Python + GTK3**, com o mesmo visual escuro e arredondado.

---

> ## 🤖 Feito por *vibecode*
>
> **Este projeto foi escrito inteiramente por uma IA (Claude, da Anthropic), conversando em português com o usuário**, no estilo conhecido como *vibe coding*: o usuário dizia o que queria ("um menu igual ao do GNOME", "o Wi-Fi tem que fechar sozinho", "mais estreito sem cortar texto"…), a IA escrevia o código, testava na tela do próprio usuário (com capturas de tela) e ajustava.
>
> Isso quer dizer que:
> - o código **não foi revisado linha a linha por um programador humano**;
> - foi testado em **uma única máquina** (notebook HP com Zorin OS 18 / Ubuntu 24.04, labwc 0.7.1, tela 1366×768);
> - pode ter bugs, partes específicas desse ambiente e decisões que um humano faria diferente.
>
> Use, estude e adapte à vontade, mas **por sua conta e risco**. Leia o código antes de rodar: ele é curto e todo comentado em português.

---

## O que tem aqui

| Programa | O que faz | Como abre (no exemplo) |
|---|---|---|
| `menu-iniciar` | Menu de aplicativos no layout "Standard" do Zorin Menu: categorias do sistema, todos os apps, favoritos, pastas, botões de sessão. A **busca** encontra apps, seções das Configurações, arquivos da pasta pessoal e faz **contas** (`2+2*3`, `15%*200`). | botão "Aplicativos" na barra, Super+A |
| `configuracoes` | Tela de **Configurações** em seções: Wi-Fi, Bluetooth, Som, Tela e brilho, Energia e bateria, Notificações, Mouse e touchpad, Teclado, Atalhos, Aparência, Impressoras, Sistema e Sobre. O que é do labwc (mouse, touchpad, teclado) é aplicado na hora. | Super+I |
| `menu-calendario` | Ao clicar na data: **calendário** à direita e **notificações** à esquerda, com "Não perturbe" e "Limpar" (como no GNOME). | clique na data, Super+V |
| `relogio-barra` | Texto da data na barra, com **ponto azul** quando há notificações novas e **sino cortado** no "não perturbe". | módulo da Waybar |
| `menu-volume` | Volume e microfone com controle deslizante e mudo, escolha da **saída de som** (alto-falantes, fones, HDMI, Bluetooth). | clique no volume |
| `menu-wifi` | Lista de redes com sinal e cadeado, **senha dentro do próprio menu**, liga/desliga o Wi-Fi. | clique na rede, Super+N |
| `menu-energia` | Bloquear, suspender, sair, reiniciar e desligar (os três últimos pedem confirmação). | botão ⏻, Super+Esc |
| `menu-dispositivos` | Ícone de **pendrive** que aparece na barra quando há um conectado, com "Abrir" e **"Ejetar"**. | clique no ícone USB |
| `bloquear` | Tela de bloqueio com o **papel de parede desfocado** e a data. | Super+L, inatividade |
| `lib/notificacoes.py` | Módulo usado pelo calendário e pelo relógio para ler o histórico do mako. | — |

Todos os menus **fecham sozinhos** ao clicar de novo no botão, ao clicar em outra janela ou com **Esc**.

## Requisitos

Testado no **Zorin OS 18** (Ubuntu 24.04). Pacotes usados:

```bash
sudo apt install labwc waybar python3-gi gir1.2-gtk-3.0 gir1.2-gmenu-3.0 \
  network-manager wireplumber pipewire-pulse pavucontrol mako-notifier \
  swaylock swayidle swaybg wlr-randr brightnessctl udisks2 libnotify-bin \
  python3-pil fonts-font-awesome
```

Algumas partes são específicas do Zorin/GNOME e degradam com elegância (o botão some ou abre outra coisa) se não existirem:
- **Aparência** usa os temas `Zorin<Cor>-Light/Dark` e a fonte Inter do Zorin OS;
- **Usuários, data e idioma** abrem o `gnome-control-center`;
- **Bluetooth**, **monitores** e **impressoras** usam `blueman`, `wdisplays` e `system-config-printer`, se estiverem instalados;
- o menu de aplicativos lê as categorias de `gnome-applications.menu` (pacote `gnome-menus`).

## Instalação

```bash
git clone https://github.com/natanramos252/labwc-menus-gtk.git
cd labwc-menus-gtk
./instalar.sh
```

O `instalar.sh` só copia arquivos para a sua pasta pessoal (`~/.local/bin` e `~/.local/share`), sem `sudo`. Depois:

1. **Barra:** junte `exemplos/waybar-config.jsonc` e `exemplos/waybar-style.css` à sua configuração do Waybar.
2. **Teclas e posições:** junte `exemplos/labwc-rc.xml` ao seu `~/.config/labwc/rc.xml` e rode `labwc --reconfigure`.

### ⚠ Ajuste as posições dos menus

O labwc 0.7 não sabe onde fica cada botão da Waybar. Por isso cada menu é posicionado por uma **regra de janela** com coordenadas fixas (`MoveTo x/y` em `exemplos/labwc-rc.xml`), calculadas para uma tela de **1366×768**. Em outra resolução, ou com outra ordem de módulos na barra, ajuste o `x` de cada regra.

## Como funciona (resumo)

- Cada menu é um `Gtk.Application` de **instância única**: rodar o comando de novo com o menu aberto o fecha. Assim, o mesmo clique abre e fecha.
- A janela não tem moldura e é posicionada pelo labwc (regras de janela). Ela fecha quando perde o foco. Um pequeno arquivo em `$XDG_RUNTIME_DIR` evita que o clique que tirou o foco reabra o menu na hora.
- As **Configurações** gravam as opções do labwc num bloco marcado do `rc.xml` (`<!-- configuracoes:inicio -->` … `<!-- configuracoes:fim -->`), a partir de `~/.config/labwc/configuracoes.json`, e rodam `labwc --reconfigure`.
- O **calendário/notificações** lê `makoctl list` e `makoctl history`. Para guardar mais que 5 notificações, use `max-history=50` no config do mako, que a tela de Configurações já gera.
- O **menu de aplicativos** finge ser GNOME (`XDG_CURRENT_DESKTOP=wlroots:GNOME`) só para listar os mesmos apps que o Zorin Menu, e abre os apps com o valor original.

## Limitações conhecidas

- Feito e testado para **labwc 0.7.1**. Versões mais novas podem ter recursos (ou mudanças) que este código não aproveita.
- Clicar na **área de trabalho vazia** ou na **própria barra** não fecha os menus, porque no labwc esses cliques não tiram o foco da janela.
- A tela de bloqueio mostra a **data**, não um relógio ao vivo: o `swaylock` do Ubuntu não desenha relógio.
- Textos da interface em **português do Brasil**, fixos no código.

## Licença

[MIT](LICENSE). Faça o que quiser com o código, sem garantias.
