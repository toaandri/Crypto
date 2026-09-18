"""Regenerate README, GIFs, posters and scientific plots from executable examples.

Run from the repository root: python -m scripts.build_docs
Requires the optional [docs] dependencies. Never substitutes fake output.
"""

import json
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from examples.tour import SCENES, execute_scene

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
BG, PANEL, BORDER = "#0b1220", "#121e30", "#263950"
TEXT, MUTED, CYAN, GREEN = "#edf4fc", "#9eafc4", "#55d9ec", "#9fe6b3"


def _font(size, mono=False, bold=False):
    candidates = (["C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"] if mono else
                  ["C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def _wrapped(draw, value, x, y, font, width, fill, line_height):
    words, line = value.split(), ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textlength(candidate, font=font) > width and line:
            draw.text((x, y), line, font=font, fill=fill)
            line, y = word, y + line_height
        else:
            line = candidate
    draw.text((x, y), line, font=font, fill=fill)
    return y + line_height


def _frame(scene, step_index, output, reveal):
    image = Image.new("RGB", (1440, 840), BG)
    draw = ImageDraw.Draw(image)
    step = scene.steps[step_index]
    draw.text((48, 26), "CRYPTO / FROM SCRATCH", font=_font(16, bold=True), fill=CYAN)
    draw.text((48, 65), scene.title, font=_font(35, bold=True), fill=TEXT)
    draw.text((48, 116), scene.subtitle, font=_font(22), fill=MUTED)
    draw.rounded_rectangle((44, 175, 1396, 730), radius=20, fill=PANEL, outline=BORDER, width=2)
    draw.text((72, 199), f"{step_index + 1:02d}  {step.title}", font=_font(26, bold=True), fill=TEXT)
    _wrapped(draw, step.explanation, 72, 245, _font(21), 1260, MUTED, 28)
    draw.line((72, 318, 1368, 318), fill=BORDER, width=2)
    draw.text((76, 340), "PYTHON", font=_font(15, bold=True), fill=CYAN)
    draw.text((982, 340), "SORTIE EXÉCUTÉE", font=_font(15, bold=True), fill=GREEN)
    draw.line((951, 338, 951, 695), fill=BORDER, width=2)
    lines = textwrap.dedent(step.code).strip().splitlines()
    code_font = _font(18, mono=True)
    for index, line in enumerate(lines):
        y = 379 + index * 28
        if y > 699:
            raise ValueError(f"Too many code lines in {scene.slug}")
        draw.text((75, y), f"{index+1:02d}", font=code_font, fill="#526680")
        color = CYAN if line.lstrip().startswith(("from ", "import ")) else TEXT
        if line.lstrip().startswith("assert "):
            color = GREEN
        if draw.textlength(line, font=code_font) > 824:
            raise ValueError(f"Code too wide in {scene.slug}: {line}")
        draw.text((113, y), line, font=code_font, fill=color)
    if reveal:
        output_lines = []
        for line in output.splitlines():
            output_lines.extend(textwrap.wrap(line, width=32) or [""])
        if len(output_lines) > 12:
            raise ValueError(f"Output too tall in {scene.slug}")
        for index, line in enumerate(output_lines):
            draw.text((982, 379 + index * 26), line, font=_font(18, mono=True), fill=GREEN)
    else:
        draw.text((982, 379), "Exécution…", font=_font(20), fill=MUTED)
    draw.text((48, 760), "Bibliothèque éducative · Python · Exemples reproductibles", font=_font(18), fill=MUTED)
    for index in range(len(scene.steps)):
        x = 1250 + index * 35
        draw.rounded_rectangle((x, 767, x + 22, 773), radius=3,
                               fill=CYAN if index == step_index else BORDER)
    return image


def render_scene(scene, outputs):
    frames, durations = [], []
    for index, output in enumerate(outputs):
        frames.extend((_frame(scene, index, output, False), _frame(scene, index, output, True)))
        durations.extend((1300, 6000))
    # One shared palette avoids flashing between pages.
    palette = frames[1].quantize(colors=128)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(ASSETS / f"{scene.slug}.gif", save_all=True, append_images=indexed[1:],
                    duration=durations, loop=0, disposal=2, optimize=False)
    frames[-1].save(ASSETS / f"{scene.slug}.png")


def plots(data):
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": PANEL,
                         "axes.edgecolor": MUTED, "axes.labelcolor": TEXT,
                         "text.color": TEXT, "xtick.color": MUTED, "ytick.color": MUTED,
                         "font.size": 11, "grid.color": BORDER})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    rows = data["factorization"]
    axes[0, 0].plot([r["bits"] for r in rows], [r["median_seconds"] * 1000 for r in rows], "o-", color=CYAN)
    axes[0, 0].set(title="B · Factorisation par division", xlabel="Taille de n (bits)", ylabel="Médiane (ms)", yscale="log")
    for name, color in (("trial_division", CYAN), ("miller_rabin", GREEN)):
        rows = [r for r in data["primality"]["small_numbers"] if r["algorithm"] == name]
        axes[0, 1].plot([r["bits"] for r in rows], [r["median_seconds"] * 1000 for r in rows], "o-", color=color, label=name)
    axes[0, 1].set(title="F · Primalité sur les mêmes nombres", xlabel="Taille (bits)", ylabel="Médiane (ms)", yscale="log")
    axes[0, 1].legend(facecolor=PANEL, labelcolor=TEXT)
    for index, row in enumerate(data["avalanche"]):
        axes[1, 0].hist(row["samples"], bins=range(90, 171, 4), alpha=0.45, label=f"Message {index+1}")
    axes[1, 0].axvline(128, color=TEXT, linestyle="--")
    axes[1, 0].set(title="C · Avalanche SHA-256", xlabel="Bits modifiés sur 256", ylabel="Nombre d'essais")
    axes[1, 0].legend(facecolor=PANEL, labelcolor=TEXT)
    rows = data.get("benchmarks", {}).get("results", [])
    rows = [r for r in rows if r["operation"] == "rsa_keygen"]
    if rows:
        axes[1, 1].bar([str(r["key_bits_requested"]) for r in rows],
                        [r["median_seconds"] for r in rows], color=CYAN)
    axes[1, 1].set(title="A · Génération des clés RSA", xlabel="Taille demandée (bits)", ylabel="Médiane (s)")
    for ax in axes.flat:
        ax.grid(alpha=0.35)
    fig.suptitle("Mesures locales · Charges reproductibles, durées variables", fontsize=16)
    fig.savefig(ASSETS / "science.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), layout="constrained")
    modes = data["modes"]
    for ax, name, title in zip(axes, ("plaintext", "ecb", "cbc"), ("Clair · 2 blocs distincts", "ECB · motifs conservés", "CBC · motifs masqués")):
        lookup = {value: i for i, value in enumerate(sorted(set(modes[name])))}
        matrix = [[lookup[modes[name][y*16+x]] for x in range(16)] for y in range(16)]
        ax.imshow(matrix, cmap="viridis", interpolation="nearest")
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("D · Chaque cellule représente un bloc de 8 octets (padding exclu)")
    fig.savefig(ASSETS / "ecb-cbc.png", dpi=150)
    plt.close(fig)


def readme(outputs):
    parts = [(ROOT / "docs" / "readme_header.md").read_text(encoding="utf-8")]
    for scene in SCENES:
        parts.append(f"\n<a id=\"demo-{scene.slug}\"></a>\n\n### {scene.title}\n\n{scene.subtitle}.\n")
        parts.append(f"\n![{scene.title} : code Python et résultats étape par étape](docs/assets/{scene.slug}.gif)\n")
        parts.append(f"\n[Image fixe](docs/assets/{scene.slug}.png) · Exécuter : `python -m examples.tour {scene.slug}`\n")
        parts.append("\n<details>\n<summary>Lire le code et les résultats de cette démonstration</summary>\n")
        for step, output in zip(scene.steps, outputs[scene.slug]):
            parts.append(f"\n**{step.title}.** {step.explanation}\n\n```python\n{textwrap.dedent(step.code).strip()}\n```\n\n```text\n{output}\n```\n")
        parts.append("\n</details>\n")
    parts.append((ROOT / "docs" / "readme_footer.md").read_text(encoding="utf-8"))
    (ROOT / "README.md").write_text("".join(parts), encoding="utf-8")


def science_report(data):
    def table(headers, rows):
        return ("| " + " | ".join(headers) + " |\n|" + "---|" * len(headers) + "\n"
                + "".join("| " + " | ".join(str(value) for value in row) + " |\n" for row in rows))
    report = [f"""# Expériences A–F : protocole, observations et limites

Rapport généré depuis [science.json](results/science.json), sous Python
{data['python']} sur `{data['platform']}`, avec {data['repeats']} répétitions.
Les données et figures sont conservées ; les durées changeront à la réexécution.
Les clés jouets et les exposants fixes ne sont destinés qu'à l'étude.

Pour reproduire : `python -m experiments.science.run`, puis
`python -m scripts.build_docs`. Les calculs utilisent le code du dépôt.

![Mesures A, B, C et F](assets/science.png)

## A — Influence de la taille des clés RSA

**Hypothèse.** La génération devient plus coûteuse quand la taille augmente.

**Protocole et données.** Générer des clés de 512, 1024 et 2048 bits, une chauffe
puis plusieurs mesures. La recherche de nombres premiers reste aléatoire.
Le benchmark inclut aussi chiffrement/déchiffrement pour 16, 256 et 1024 octets.
Le pic d'allocations Python est obtenu dans une exécution séparée.

**Résultats.** Médianes de génération :

"""]
    rows = [r for r in data.get("benchmarks", {}).get("results", []) if r["operation"] == "rsa_keygen"]
    report.append(table(["Bits demandés", "Médiane (s)", "Pic Python (octets)"],
                        [(r["key_bits_requested"], f"{r['median_seconds']:.6f}", r["peak_python_bytes"]) for r in rows]))
    report.append("""
**Interprétation et conclusion.** Cette exécution montre un coût croissant.
Les petits échantillons et le nombre variable de candidats premiers interdisent
d'en déduire une loi exacte ou une recommandation de sécurité.

## B — Factorisation selon la taille de l'entier

**Hypothèse.** La division d'essai devient rapidement plus lente.

**Protocole et données.** Choisir deux premiers proches par une recherche
déterministe, multiplier, puis factoriser avec la même fonction à chaque taille.
Les paramètres exacts figurent dans le JSON ; aucune cible externe n'est utilisée.

**Résultats.**

""")
    report.append(table(["Bits réels", "n", "Facteurs", "Médiane (ms)"],
                        [(r["bits"], r["number"], " × ".join(map(str, r["factors"])),
                          f"{r['median_seconds']*1000:.4f}") for r in data["factorization"]]))
    report.append("""
**Interprétation et conclusion.** Les facteurs étant proches de la racine,
le nombre de divisions augmente fortement. Il s'agit uniquement de la division
d'essai, pas du crible général des corps de nombres ni d'une estimation du coût
des meilleures attaques RSA modernes.

## C — Effet avalanche de SHA-256

**Hypothèse.** Changer un bit d'entrée modifie environ la moitié du condensat.

**Protocole et données.** Messages : `Bonjour`, les octets 0 à 31 et
`Un seul bit change tout.`. Inverser chaque bit séparément et calculer la distance
de Hamming entre les condensats. Aucun tirage aléatoire n'est nécessaire.

**Résultats.** L'écart-type indiqué est celui de la population d'essais mesurée.

""")
    report.append(table(["Message", "Essais", "Moyenne / 256", "Écart-type", "Min–max"],
                        [(i+1, len(r["samples"]), f"{r['mean_bits']:.3f}", f"{r['stddev_bits']:.3f}",
                          f"{r['min_bits']}–{r['max_bits']}") for i, r in enumerate(data["avalanche"])]))
    report.append("""
**Interprétation et conclusion.** Les moyennes proches de 128 illustrent une
bonne diffusion. Cette observation ne prouve ni la résistance aux collisions
ni la résistance à la préimage. Les messages ont des nombres d'essais différents,
donc les hauteurs brutes des histogrammes ne sont pas directement comparables.

## D — Motifs répétés en ECB et CBC

**Hypothèse.** ECB conserve l'égalité des blocs ; CBC masque ce motif.

**Protocole et données.** Construire une matrice 16 × 16 de blocs de 8 octets,
alternant les valeurs `AAAAAAAA` et `BBBBBBBB`. Chiffrer avec Feistel et une clé
fixe. L'IV CBC nul est réservé à cette expérience reproductible. Exclure le
padding des comptages et attribuer une couleur à chaque valeur distincte.

![Matrice avant et après chiffrement](assets/ecb-cbc.png)

**Résultats.** 2 blocs distincts en clair, 2 en ECB, 256 en CBC pour ces entrées.

**Interprétation et conclusion.** La matrice révèle les motifs laissés par ECB.
L'absence de répétitions en CBC n'authentifie rien et ne valide pas le Feistel.
Un IV fixe ne doit pas être reproduit pour des messages réels.

## E — Interception d'un Diffie–Hellman non authentifié

**Hypothèse.** Un échange DH seul n'assure pas l'identité du pair.

**Protocole et données.** Dans le groupe jouet p=23, g=5, Alice et Bob utilisent
les exposants 6 et 15. Mallory remplace leurs valeurs publiques par celles de
ses exposants 3 et 7. Comparer les secrets de chaque extrémité.

**Résultats.** Alice partage 6 avec Mallory, Bob partage 15 avec Mallory.
Les deux utilisateurs n'ont pas le même secret, mais Mallory connaît les deux.

**Interprétation et conclusion.** Le calcul mathématique est correct et
l'identité est absente. Le canal V12 ajoute des preuves HMAC du transcript et
rejette une substitution sans connaissance de la clé prépartagée ; ses tests
vérifient le transcript modifié et une mauvaise clé d'authentification.

## F — Paramètres, coût et garanties

**Hypothèse.** Augmenter tailles et nombre de témoins a un coût observable ;
choisir un algorithme adapté change également les performances.

**Protocole et données.** Comparer les deux tests sur les mêmes premiers de
12 à 32 bits. Mesurer ensuite Miller–Rabin sur le premier `2**127-1` avec
1, 4, 8, 16 et 40 témoins. Mesurer aussi des échanges DH de 16 à 128 bits et
AES-GCM avec trois tailles de clé et trois tailles de message.

**Résultats de primalité.**

""")
    report.append(table(["Bits", "Algorithme", "Médiane (ms)"],
                        [(r["bits"], r["algorithm"], f"{r['median_seconds']*1000:.4f}")
                         for r in data["primality"]["small_numbers"]]))
    report.append("\n**Nombre de témoins sur 127 bits.**\n\n")
    report.append(table(["Témoins", "Borne théorique pour un composé fixé", "Médiane (ms)"],
                        [(r["rounds"], f"{r['composite_false_positive_bound']:.3e}", f"{r['median_seconds']*1000:.4f}")
                         for r in data["primality"]["probabilistic_rounds"]]))
    report.append("\n**Échanges DH.** Les durées incluent la validation des paramètres et les deux participants.\n\n")
    report.append(table(["Bits", "Médiane (ms)"],
                        [(r["bits"], f"{r['median_seconds']*1000:.4f}") for r in data["dh"]]))
    report.append("\n**AES-GCM.** Les nonces sont fixes uniquement pour ces données de benchmark publiques.\n\n")
    report.append(table(["Clé (bits)", "Message (octets)", "Opération", "Médiane (ms)", "Pic Python (octets)"],
                        [(r["key_bits"], r["message_bytes"], r["operation"], f"{r['median_seconds']*1000:.4f}", r["peak_python_bytes"])
                         for r in data.get("aes_gcm_benchmarks", [])]))
    report.append("""
**Interprétation.** Sur les très petits nombres, le coût fixe de Miller–Rabin
peut dépasser la division ; il devient avantageux quand la taille augmente.
La borne théorique n'est pas mesurée sur un premier : un premier passe toujours.
Sous 2**64, le paramètre rounds ne remplace pas les sept bases fixes. Les temps
DH avec validation ne mesurent pas seulement une exponentiation modulaire.

**Conclusion.** Les paramètres doivent être étudiés avec leurs hypothèses, pas
seulement leur vitesse. Les expériences ne recommandent aucun paramètre réel et
ne prouvent aucune résistance cryptographique. AES-GCM apporte une authentification
que les modes Feistel seuls ne donnent pas, mais le code Python reste éducatif.

## Reproductibilité et portée

Les valeurs d'entrée, nombres de répétitions et distributions sont conservés
dans le JSON. Les temps dépendent du système, de Python et de la recherche de
premiers. Trois répétitions donnent une illustration, pas un intervalle de
confiance robuste. Les graphiques sont produits à partir des mesures enregistrées,
sans inventer de données ni interpoler des performances non observées.
""")
    (ROOT / "docs/experiments.md").write_text("".join(report), encoding="utf-8")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    data = json.loads((ROOT / "docs/results/science.json").read_text(encoding="utf-8"))
    outputs = {}
    for scene in SCENES:
        outputs[scene.slug] = execute_scene(scene)
        render_scene(scene, outputs[scene.slug])
        print(f"Rendered {scene.slug}.gif")
    plots(data)
    science_report(data)
    readme(outputs)
    (ROOT / "docs/results/demo_outputs.json").write_text(
        json.dumps(outputs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("README, 10 GIFs, 10 static alternatives and 2 scientific figures generated.")


if __name__ == "__main__":
    main()
