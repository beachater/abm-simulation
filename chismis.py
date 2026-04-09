"""
+======================================================+
|   CHISMIS SPREADER - A Barangay Agent-Based Model    |
|        Computational Modeling - Report 3             |
+======================================================+

A humorous SIR-style ABM set in a Philippine barangay.
Gossip (chismis) spreads from neighbor to neighbor,
just like a real epidemic, but with more drama.

HOW TO RUN:
    pip install streamlit numpy matplotlib
    streamlit run chismis.py
"""

import random
import time

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# PAGE CONFIG
st.set_page_config(
    page_title="Chismis Spreader",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CUSTOM CSS
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Courier+Prime&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

.main {
    background:
        radial-gradient(circle at top, rgba(255, 215, 0, 0.08), transparent 28%),
        linear-gradient(180deg, #0f1117 0%, #111827 100%);
}

.chismis-title {
    text-align: center;
    font-size: 2.8em;
    font-weight: 900;
    color: #FFD700;
    text-shadow: 2px 2px 0px #B8860B;
    margin-bottom: 0;
    letter-spacing: -1px;
}

.chismis-subtitle {
    text-align: center;
    font-size: 1.05em;
    color: #b9c0cc;
    margin-top: 4px;
    margin-bottom: 20px;
    font-style: italic;
}

.stat-card {
    border-radius: 16px;
    padding: 14px 18px;
    text-align: center;
    margin: 4px 0;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
}

.stat-wala {
    background: linear-gradient(135deg, rgba(46, 204, 113, 0.18), rgba(35, 98, 63, 0.55));
    border: 1.5px solid #2ECC71;
}

.stat-kabalo {
    background: linear-gradient(135deg, rgba(231, 76, 60, 0.2), rgba(122, 29, 35, 0.65));
    border: 1.5px solid #E74C3C;
}

.stat-kapoy {
    background: linear-gradient(135deg, rgba(127, 140, 141, 0.22), rgba(67, 76, 94, 0.6));
    border: 1.5px solid #7F8C8D;
}

.stat-number {
    font-size: 2.2em;
    font-weight: 900;
    line-height: 1;
}

.stat-label {
    font-size: 0.8em;
    color: #d5d9e0;
    margin-top: 4px;
}

.log-box {
    background: rgba(22, 27, 34, 0.92);
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 12px;
    font-family: 'Courier Prime', monospace;
    font-size: 0.8em;
    color: #c0c7d3;
    max-height: 220px;
    overflow-y: auto;
}

.info-box {
    background: rgba(22, 27, 34, 0.92);
    border-left: 4px solid #FFD700;
    border-radius: 0 12px 12px 0;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 0.9em;
    color: #d5d9e0;
}

.metric-highlight {
    font-size: 1.08em;
    font-weight: 800;
    color: #FFD700;
}

.viz-card {
    background: linear-gradient(160deg, rgba(23, 29, 39, 0.98), rgba(14, 19, 27, 0.98));
    border: 1px solid #30363d;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 10px;
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.18);
}

.viz-title {
    color: #FFD700;
    font-weight: 800;
    font-size: 0.98em;
    margin-bottom: 10px;
}

.viz-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 12px;
}

.mini-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 12px;
}

.mini-number {
    color: white;
    font-size: 1.6em;
    font-weight: 900;
    line-height: 1;
}

.mini-label {
    color: #a9b2bf;
    font-size: 0.78em;
    margin-top: 3px;
}

.bar-row {
    margin-bottom: 12px;
}

.bar-head {
    display: flex;
    justify-content: space-between;
    color: #dbe2ea;
    font-size: 0.82em;
    margin-bottom: 5px;
}

.bar-bg {
    width: 100%;
    height: 11px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 999px;
}

.timeline {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 4px;
}

.timeline-pill {
    min-width: 56px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 999px;
    padding: 8px 10px;
    text-align: center;
}

.timeline-day {
    color: #8c97a8;
    font-size: 0.72em;
}

.timeline-value {
    color: #fff;
    font-weight: 800;
    font-size: 0.96em;
}
</style>
""",
    unsafe_allow_html=True,
)

# CONSTANTS
WALA_PA_NAKABALO = 0
NAKABALO = 1
GIKAPOY = 2

COLORS = {
    WALA_PA_NAKABALO: "#2ECC71",
    NAKABALO: "#E74C3C",
    GIKAPOY: "#7F8C8D",
}

EMOJIS = {
    WALA_PA_NAKABALO: "🙂",
    NAKABALO: "🗣️",
    GIKAPOY: "😑",
}

PH_NAMES = [
    "Ate Rose", "Kuya Boboy", "Lola Caring", "Tito Nonong",
    "Ate Belen", "Mang Pedro", "Aling Nena", "Kuya Jun",
    "Ate Cora", "Dodong", "Inday", "Manong Bert",
    "Ate Chit", "Kuya Rex", "Lola Unding", "Tatay Isko",
    "Nanay Lita", "Bossing Tony", "Ate Girlie", "Diko Ben",
]

CHISMIS_CONTENT = [
    "naa na kunoy uyab si Ate Girlie!",
    "nakit-an kuno si Kuya Jun sa Jollibee uban sa lain!",
    "nasakit kuno si Aling Nena tungod sa aircon!",
    "sayop kuno ug pangalan ang gibutaran ni Mang Pedro!",
    "nidaug kuno sa lotto si Bossing Tony pero nagtago!",
    "naa kunoy bag-ong pet si Lola Caring nga sawa!",
    "ni-abroad kuno si Dodong nga walay pasalubong!",
    "naa pa kunoy utang si Tito Nonong sa tindahan!",
    "naaksidente kuno ang traysikel ni Manong Bert sa rotonda!",
    "nagbulag na kuno ang magtiayon sa eskina!",
]

SPREAD_PHRASES = [
    "Psst! Nakadungog naka?",
    "Ayaw lang isulti ha, pero...",
    "Tinuod kuno ni ha!",
    "Nakakita gyud kuno si Ate!",
    "Sus, juicy kaayo ni nga balita!",
    "Gikan ni sa kasaligan kunong source...",
    "Sulti sa among silingan nga...",
    "Naa koy nadunggan nga...",
]

TIRED_PHRASES = [
    "Sus, karaan na man na.",
    "Kapoy na kaayo, balik-balik naman na.",
    "Gikapoy nako ani.",
    "Hunong na mo uy.",
    "Move on na ta oy.",
]


def init_state():
    defaults = dict(
        grid=None,
        step=0,
        running=False,
        log=[],
        history_s=[],
        history_i=[],
        history_r=[],
        chismis_topic=random.choice(CHISMIS_CONTENT),
        initialized=False,
        completed_notified=False,
    )
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def safe_ratio(beta_value, gamma_value):
    if gamma_value == 0:
        return float("inf") if beta_value > 0 else 0.0
    return beta_value / gamma_value


def ratio_text(value):
    return "∞" if value == float("inf") else f"{value:.2f}"


def render_html_block(html):
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


def make_grid(size, initial_infected=1):
    grid = np.zeros((size, size), dtype=int)
    center = size // 2
    for _ in range(initial_infected):
        row = center + random.randint(-2, 2)
        col = center + random.randint(-2, 2)
        row = max(0, min(size - 1, row))
        col = max(0, min(size - 1, col))
        grid[row][col] = NAKABALO
    return grid


def step_grid(grid, beta, gamma, size):
    new_grid = grid.copy()
    log_entries = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for row in range(size):
        for col in range(size):
            if grid[row][col] == NAKABALO:
                if random.random() < gamma:
                    new_grid[row][col] = GIKAPOY
                    name = random.choice(PH_NAMES)
                    log_entries.append(f"😑 {name}: \"{random.choice(TIRED_PHRASES)}\"")
                else:
                    random.shuffle(directions)
                    for d_row, d_col in directions:
                        next_row, next_col = row + d_row, col + d_col
                        if 0 <= next_row < size and 0 <= next_col < size:
                            if grid[next_row][next_col] == WALA_PA_NAKABALO and random.random() < beta:
                                new_grid[next_row][next_col] = NAKABALO
                                spreader = random.choice(PH_NAMES)
                                receiver = random.choice(PH_NAMES)
                                phrase = random.choice(SPREAD_PHRASES)
                                log_entries.append(
                                    f"🗣️ {spreader} -> {receiver}: \"{phrase} {st.session_state.chismis_topic}\""
                                )

    return new_grid, log_entries


def count_states(grid):
    walay_nahibaw = int(np.sum(grid == WALA_PA_NAKABALO))
    nakabalo = int(np.sum(grid == NAKABALO))
    gikapoy = int(np.sum(grid == GIKAPOY))
    return walay_nahibaw, nakabalo, gikapoy


def reset_simulation(size, initial_infected):
    st.session_state.grid = make_grid(size, initial_infected)
    st.session_state.step = 0
    st.session_state.log = []
    st.session_state.history_s = []
    st.session_state.history_i = []
    st.session_state.history_r = []
    st.session_state.running = False
    st.session_state.initialized = True
    st.session_state.completed_notified = False

    susceptible, infected, recovered = count_states(st.session_state.grid)
    st.session_state.history_s.append(susceptible)
    st.session_state.history_i.append(infected)
    st.session_state.history_r.append(recovered)


def advance_simulation(beta, gamma, size):
    susceptible, infected, recovered = count_states(st.session_state.grid)
    if infected == 0:
        st.session_state.running = False
        return "finished", susceptible, infected, recovered

    new_grid, log_entries = step_grid(st.session_state.grid, beta, gamma, size)
    st.session_state.grid = new_grid
    st.session_state.step += 1
    st.session_state.log.extend(log_entries)

    susceptible, infected, recovered = count_states(new_grid)
    st.session_state.history_s.append(susceptible)
    st.session_state.history_i.append(infected)
    st.session_state.history_r.append(recovered)

    if infected == 0:
        st.session_state.running = False
        return "finished", susceptible, infected, recovered
    return "running", susceptible, infected, recovered


def render_grid(grid, size):
    fig, ax = plt.subplots(figsize=(6.1, 5.8))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#111827")

    xs, ys = [], []
    unaware_x, unaware_y = [], []
    infected_x, infected_y = [], []
    tired_x, tired_y = [], []

    for row in range(size):
        for col in range(size):
            state = int(grid[row][col])
            x_pos = col
            y_pos = size - 1 - row
            xs.append(x_pos)
            ys.append(y_pos)

            if state == WALA_PA_NAKABALO:
                unaware_x.append(x_pos)
                unaware_y.append(y_pos)
            elif state == NAKABALO:
                infected_x.append(x_pos)
                infected_y.append(y_pos)
            else:
                tired_x.append(x_pos)
                tired_y.append(y_pos)

    # Faint neighborhood lots so the barangay still feels structured.
    ax.scatter(xs, ys, s=410, c="#17212d", marker="s", alpha=0.18, linewidths=0)

    # Residents who still don't know.
    ax.scatter(unaware_x, unaware_y, s=250, c=COLORS[WALA_PA_NAKABALO], alpha=0.20, linewidths=0)
    ax.scatter(
        unaware_x,
        unaware_y,
        s=175,
        c=COLORS[WALA_PA_NAKABALO],
        edgecolors="#d8fee8",
        linewidths=0.7,
        alpha=0.92,
    )
    ax.scatter(unaware_x, unaware_y, s=22, c="#f4fff8", alpha=0.85, linewidths=0)

    # Residents currently spreading chismis get louder halos.
    ax.scatter(infected_x, infected_y, s=460, c=COLORS[NAKABALO], alpha=0.10, linewidths=0)
    ax.scatter(infected_x, infected_y, s=300, c=COLORS[NAKABALO], alpha=0.18, linewidths=0)
    ax.scatter(
        infected_x,
        infected_y,
        s=190,
        c=COLORS[NAKABALO],
        edgecolors="#ffe0dc",
        linewidths=0.8,
        alpha=0.96,
    )
    # Residents who got tired of the rumor.
    ax.scatter(tired_x, tired_y, s=250, c=COLORS[GIKAPOY], alpha=0.18, linewidths=0)
    ax.scatter(
        tired_x,
        tired_y,
        s=175,
        c=COLORS[GIKAPOY],
        edgecolors="#e5e7eb",
        linewidths=0.7,
        alpha=0.90,
    )
    def draw_people(x_positions, y_positions, state):
        if not x_positions:
            return

        if state == WALA_PA_NAKABALO:
            icon_color = "#f4fff8"
            arm_style = "open"
        elif state == NAKABALO:
            icon_color = "#fff5f4"
            arm_style = "raised"
        else:
            icon_color = "#f3f4f6"
            arm_style = "down"

        ax.scatter(
            x_positions,
            [y + 0.08 for y in y_positions],
            s=18,
            c=icon_color,
            linewidths=0,
            zorder=5,
        )

        for x_pos, y_pos in zip(x_positions, y_positions):
            ax.plot(
                [x_pos, x_pos],
                [y_pos - 0.12, y_pos + 0.02],
                color=icon_color,
                linewidth=1.25,
                solid_capstyle="round",
                zorder=5,
            )
            ax.plot(
                [x_pos, x_pos - 0.07],
                [y_pos - 0.12, y_pos - 0.22],
                color=icon_color,
                linewidth=1.05,
                solid_capstyle="round",
                zorder=5,
            )
            ax.plot(
                [x_pos, x_pos + 0.07],
                [y_pos - 0.12, y_pos - 0.22],
                color=icon_color,
                linewidth=1.05,
                solid_capstyle="round",
                zorder=5,
            )

            if arm_style == "raised":
                ax.plot(
                    [x_pos, x_pos - 0.11],
                    [y_pos - 0.01, y_pos + 0.12],
                    color=icon_color,
                    linewidth=1.05,
                    solid_capstyle="round",
                    zorder=5,
                )
                ax.plot(
                    [x_pos, x_pos + 0.11],
                    [y_pos - 0.01, y_pos + 0.12],
                    color=icon_color,
                    linewidth=1.05,
                    solid_capstyle="round",
                    zorder=5,
                )
                ax.scatter([x_pos + 0.16], [y_pos + 0.16], s=10, c=icon_color, linewidths=0, zorder=5)
            elif arm_style == "down":
                ax.plot(
                    [x_pos, x_pos - 0.1],
                    [y_pos - 0.01, y_pos - 0.08],
                    color=icon_color,
                    linewidth=1.0,
                    solid_capstyle="round",
                    zorder=5,
                )
                ax.plot(
                    [x_pos, x_pos + 0.1],
                    [y_pos - 0.01, y_pos - 0.08],
                    color=icon_color,
                    linewidth=1.0,
                    solid_capstyle="round",
                    zorder=5,
                )
            else:
                ax.plot(
                    [x_pos, x_pos - 0.1],
                    [y_pos - 0.01, y_pos + 0.03],
                    color=icon_color,
                    linewidth=1.0,
                    solid_capstyle="round",
                    zorder=5,
                )
                ax.plot(
                    [x_pos, x_pos + 0.1],
                    [y_pos - 0.01, y_pos + 0.03],
                    color=icon_color,
                    linewidth=1.0,
                    solid_capstyle="round",
                    zorder=5,
                )

    draw_people(unaware_x, unaware_y, WALA_PA_NAKABALO)
    draw_people(infected_x, infected_y, NAKABALO)
    draw_people(tired_x, tired_y, GIKAPOY)

    ax.set_xlim(-0.8, size - 0.2)
    ax.set_ylim(-0.8, size - 0.2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(color=(1, 1, 1, 0.05), linestyle=":", linewidth=0.6)

    ax.set_title(
        f"Barangay Visual - Adlaw {st.session_state.step}",
        color="#FFD700",
        fontsize=11,
        fontweight="bold",
        pad=10,
    )

    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
        spine.set_linewidth(1.4)

    patches = [
        mpatches.Patch(color=COLORS[WALA_PA_NAKABALO], label="Wa pa kabalo"),
        mpatches.Patch(color=COLORS[NAKABALO], label="Nakabalo"),
        mpatches.Patch(color=COLORS[GIKAPOY], label="Gikapoy na"),
    ]
    ax.legend(
        handles=patches,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.09),
        ncol=3,
        frameon=False,
        labelcolor="white",
        fontsize=8,
    )

    plt.tight_layout()
    return fig


def render_story_panel(grid, total_population):
    susceptible, infected, recovered = count_states(grid)
    heard = infected + recovered
    heard_pct = (heard / total_population * 100) if total_population else 0

    peak_infected = max(st.session_state.history_i) if st.session_state.history_i else 0
    peak_day = st.session_state.history_i.index(peak_infected) if st.session_state.history_i else 0

    recent_days = list(
        zip(
            range(max(0, len(st.session_state.history_i) - 8), len(st.session_state.history_i)),
            st.session_state.history_i[-8:],
        )
    )
    timeline_html = "".join(
        f"""
        <div class="timeline-pill">
            <div class="timeline-day">Adlaw {day}</div>
            <div class="timeline-value">{value}</div>
        </div>
        """
        for day, value in recent_days
    )

    def bar_row(label, value, color):
        pct = (value / total_population * 100) if total_population else 0
        return f"""
        <div class="bar-row">
            <div class="bar-head">
                <span>{label}</span>
                <span>{value} ({pct:.1f}%)</span>
            </div>
            <div class="bar-bg">
                <div class="bar-fill" style="width:{pct:.1f}%; background:{color};"></div>
            </div>
        </div>
        """

    status = "Init kaayo ang chismis" if infected > 0 else "Nahuman na ang chismis"
    card_html = f"""
    <div class="viz-card">
        <div class="viz-title">Visual nga Summary</div>
        <div class="viz-grid">
            <div class="mini-card">
                <div class="mini-number">{st.session_state.step}</div>
                <div class="mini-label">Karon nga adlaw</div>
            </div>
            <div class="mini-card">
                <div class="mini-number">{peak_infected}</div>
                <div class="mini-label">Pinakadaghan nga nakabalo</div>
            </div>
            <div class="mini-card">
                <div class="mini-number">{heard_pct:.1f}%</div>
                <div class="mini-label">Nakadungog na sa chismis</div>
            </div>
        </div>
        <div class="mini-card" style="margin-bottom:12px;">
            <div class="mini-label" style="margin-top:0; color:#FFD700;">Kahimtang karon</div>
            <div style="color:#fff; font-size:1.05em; font-weight:800; margin-top:4px;">{status}</div>
            <div style="color:#97a2b2; font-size:0.82em; margin-top:4px;">
                Peak sa adlaw {peak_day} - {heard} ka residente ang nakaabotan sa balita.
            </div>
        </div>
        {bar_row("Wa pa kabalo", susceptible, COLORS[WALA_PA_NAKABALO])}
        {bar_row("Nakabalo", infected, COLORS[NAKABALO])}
        {bar_row("Gikapoy na", recovered, COLORS[GIKAPOY])}
        <div class="viz-title" style="margin-top:14px;">Momentum sa ulahing mga adlaw</div>
        <div class="timeline">{timeline_html or '<div style="color:#8c97a8;">Wala pay dagan.</div>'}</div>
    </div>
    """
    render_html_block(card_html)


def render_stats(grid, beta, gamma):
    susceptible, infected, recovered = count_states(grid)
    r_zero = safe_ratio(beta, gamma)
    threshold_text = (
        "⚠️ R0 > 1 - paspas mokatag ang chismis!"
        if r_zero == float("inf") or r_zero > 1
        else "✅ R0 < 1 - dali ra kini mohunong."
    )
    st.markdown(
        f"""
    <div style="display:flex; gap:8px; margin-bottom:8px;">
        <div class="stat-card stat-wala" style="flex:1;">
            <div class="stat-number" style="color:{COLORS[WALA_PA_NAKABALO]};">{susceptible}</div>
            <div class="stat-label">🙂 Wa pa kabalo</div>
        </div>
        <div class="stat-card stat-kabalo" style="flex:1;">
            <div class="stat-number" style="color:{COLORS[NAKABALO]};">{infected}</div>
            <div class="stat-label">🗣️ Nakabalo</div>
        </div>
        <div class="stat-card stat-kapoy" style="flex:1;">
            <div class="stat-number" style="color:{COLORS[GIKAPOY]};">{recovered}</div>
            <div class="stat-label">😑 Gikapoy na</div>
        </div>
    </div>

    <div style="background:#161b22; border-radius:12px; padding:10px 14px;
                border:1px solid #30363d; margin-bottom:8px; font-size:0.85em; color:#d5d9e0;">
        <b style="color:#FFD700;">📈 R0 Estimate:</b>&nbsp;
        <span style="font-family:monospace;">{ratio_text(r_zero)}</span>
        &nbsp;&nbsp;
        <b style="color:#FFD700;">β:</b> {beta:.2f}
        &nbsp;|&nbsp;
        <b style="color:#FFD700;">γ:</b> {gamma:.2f}
        <br>
        <span style="color:#8c97a8; font-size:0.92em;">{threshold_text}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_log():
    recent = st.session_state.log[-18:][::-1]
    lines = "\n".join(f"[Adlaw {st.session_state.step}] {entry}" for entry in recent)
    st.markdown(
        f"""
    <div style="margin-top:8px;">
        <b style="color:#FFD700; font-size:0.92em;">📋 Chismis Log (pinakabag-o sa taas):</b>
        <div class="log-box">{lines if lines else "Wala pa'y chismis. Pislita ang 🏘️ Bag-ong Barangay aron magsugod."}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def show_completion_message(susceptible, recovered):
    if not st.session_state.completed_notified:
        st.balloons()
        st.session_state.completed_notified = True
    st.success(
        f"🎉 **Nahuman na ang chismis!** Adlaw {st.session_state.step} - "
        f"{recovered} ka residente ang nakadungog, {susceptible} ang wala maabti."
    )


def render_simulation_area(grid_size, beta, gamma):
    col_grid, col_right = st.columns([1.1, 1])
    total_population = grid_size * grid_size

    if not st.session_state.initialized:
        with col_grid:
            st.markdown(
                """
            <div style="background:#161b22; border-radius:16px; border:2px dashed #30363d;
                        height:430px; display:flex; align-items:center; justify-content:center;
                        flex-direction:column; gap:10px;">
                <div style="font-size:3em;">🏘️</div>
                <div style="color:#7f8a99; font-size:1em; text-align:center;">
                    Pislita ang <b style="color:#FFD700;">Bag-ong Barangay</b><br>aron sugdan ang chismis!
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with col_right:
            st.markdown(
                """
            <div style="background:#161b22; border-radius:16px; border:1px solid #30363d;
                        padding:20px; color:#c3cad4; font-size:0.9em;">
                <b style="color:#FFD700;">Giunsa ni paglihok?</b><br><br>
                Ang matag lingin sa visual usa ka <b style="color:#fff;">residente sa barangay</b>.<br><br>
                🟢 <b style="color:#2ECC71;">Wa pa kabalo</b> - Wala pa kadungog sa chismis<br>
                🔴 <b style="color:#E74C3C;">Nakabalo</b> - Nadunggan ug nagsugod na'g pasa-pasa<br>
                ⚫ <b style="color:#9b9b9b;">Gikapoy na</b> - Nakadungog pero di na interesado<br><br>
                Sa matag <b style="color:#fff;">adlaw</b>, ang nakabalo pwede:<br>
                • moambit sa chismis sa silingan (beta = spread rate)<br>
                • o kapuyon ug mohunong (gamma = kapoy rate)<br><br>
                <i style="color:#8c97a8;">"Sa barangay, lisod kaayo itago ang sekreto."</i>
            </div>
            """,
                unsafe_allow_html=True,
            )
        render_log()
        return

    with col_grid:
        fig_grid = render_grid(st.session_state.grid, grid_size)
        st.pyplot(fig_grid, use_container_width=True)
        plt.close(fig_grid)

    with col_right:
        render_stats(st.session_state.grid, beta, gamma)
        render_story_panel(st.session_state.grid, total_population)
        susceptible, infected, recovered = count_states(st.session_state.grid)
        if infected == 0:
            show_completion_message(susceptible, recovered)

    render_log()


init_state()

# SIDEBAR
with st.sidebar:
    st.markdown("## ⚙️ Mga Setting")
    st.markdown("---")

    grid_size = st.slider(
        "📐 Kadak-on sa Barangay",
        10,
        30,
        20,
        help="Mas dako nga barangay = mas daghan ug residente sa simulation.",
    )

    st.markdown("---")
    st.markdown("### 🧠 Mga Parameter sa Chismis")

    beta = st.slider(
        "🗣️ Beta - Kusog sa Pagkatag",
        0.0,
        1.0,
        0.30,
        0.01,
        help="Posibilidad nga maambit ang chismis sa silingan kada higayon.",
    )
    gamma = st.slider(
        "😑 Gamma - Kapoyon Rate",
        0.0,
        1.0,
        0.05,
        0.01,
        help="Posibilidad nga kapuyon ang usa ka tawo ug mohunong sa chismis.",
    )
    initial_infected = st.slider(
        "🔥 Unang Mga Tigpakatag",
        1,
        5,
        1,
        help="Pila kabuok ang unang nakabalo sa chismis.",
    )

    st.markdown("---")
    st.markdown("### 🎭 Pilia ang Chismis")
    chismis_choice = st.selectbox(
        "Unsa nga chismis ang nagkatag?",
        CHISMIS_CONTENT,
        index=CHISMIS_CONTENT.index(st.session_state.chismis_topic)
        if st.session_state.chismis_topic in CHISMIS_CONTENT
        else 0,
    )
    st.session_state.chismis_topic = chismis_choice

    st.markdown("---")
    speed = st.slider(
        "⚡ Kadasig sa Simulation",
        1,
        10,
        5,
        help="Mas taas = mas dali ang pag-uswag sa kada adlaw.",
    )

    st.markdown("---")
    st.markdown(
        """
    <div style="font-size:0.75em; color:#7f8a99; text-align:center;">
    <b>Computational Modeling</b><br>
    Agent-Based Models - Report 3<br><br>
    <i>"Sa barangay, walay sikreto nga molungtad."</i>
    </div>
    """,
        unsafe_allow_html=True,
    )

# MAIN LAYOUT
st.markdown(
    """
<div class="chismis-title">🗣️ CHISMIS SPREADER 🗣️</div>
<div class="chismis-subtitle">
    Barangay Agent-Based Model &nbsp;|&nbsp; Computational Modeling - Report 3
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="info-box">
    📢 <b>Chismis karon:</b> &nbsp;<span class="metric-highlight">"{st.session_state.chismis_topic}"</span><br>
    <span style="font-size:0.92em; color:#98a3b2;">
    Nagsugod kini sa tunga sa barangay ug mikatag samtang ang mga silingan magtinugyanay sa balita.
    </span>
</div>
""",
    unsafe_allow_html=True,
)

col_b1, col_b2, col_b3, col_b4 = st.columns([1, 1, 1, 2])

with col_b1:
    if st.button("🏘️ Bag-ong Barangay", use_container_width=True, type="secondary"):
        reset_simulation(grid_size, initial_infected)

with col_b2:
    if st.button(
        "▶️ Sugdi",
        use_container_width=True,
        type="primary",
        disabled=not st.session_state.initialized,
    ):
        st.session_state.running = True
        st.session_state.completed_notified = False

with col_b3:
    if st.button(
        "⏸️ Hunong",
        use_container_width=True,
        disabled=not st.session_state.running,
    ):
        st.session_state.running = False

with col_b4:
    if st.session_state.initialized:
        susceptible, infected, recovered = count_states(st.session_state.grid)
        total = grid_size * grid_size
        heard_pct = ((infected + recovered) / total * 100) if total > 0 else 0
        status_color = "#E74C3C" if infected > 0 else "#2ECC71"
        status_text = "🔥 NAGKATAG PA!" if infected > 0 else "✅ Nahuman na ang chismis!"
        st.markdown(
            f"""
        <div style="background:#161b22; border-radius:12px; padding:10px 14px; border:1px solid #30363d; height:100%;">
            <span style="color:{status_color}; font-weight:800;">{status_text}</span><br>
            <span style="font-size:0.85em; color:#aeb7c4;">
                {heard_pct:.1f}% sa barangay nakadungog na - Adlaw {st.session_state.step}
            </span>
        </div>
        """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

fragment_supported = hasattr(st, "fragment")
run_every = max(0.10, 1.05 - (speed * 0.09))

if fragment_supported:

    @st.fragment(run_every=run_every if st.session_state.running else None)
    def simulation_fragment():
        if st.session_state.running and st.session_state.initialized:
            advance_simulation(beta, gamma, grid_size)
        render_simulation_area(grid_size, beta, gamma)


    simulation_fragment()
else:
    render_simulation_area(grid_size, beta, gamma)

    if st.session_state.running and st.session_state.initialized:
        advance_simulation(beta, gamma, grid_size)
        render_simulation_area(grid_size, beta, gamma)
        time.sleep(run_every)
        st.rerun()

if st.session_state.initialized:
    r_zero = safe_ratio(beta, gamma)
    with st.expander("📚 Pasabot - Unsa ang ABM ug SIR Model?"):
        col_e1, col_e2 = st.columns(2)

        with col_e1:
            st.markdown(
                """
**Unsa ang Agent-Based Model (ABM)?**

Sa ABM, ang matag **residente** adunay kaugalingong estado ug mosunod sa **yanong lokal nga lagda**.
Walay sentrong tigdumala, apan ang pattern sa pagkatag sa chismis **mogawas gikan sa tagsa-tagsa nga lihok** sa mga tawo.

**Tulo ka Importanteng Bahin:**
- 🤖 **Agents** - mga residente sa barangay
- 🏘️ **Environment** - ang barangay grid ug mga silingan
- ✨ **Emergence** - ang natural nga pagdagsa sa chismis
            """
            )

        with col_e2:
            st.markdown(
                f"""
**Ang SIR Model sa Barangay:**

| Parameter | Bersyon sa Barangay | Bili |
|---|---|---|
| **β (beta)** | Kusog sa pagkatag sa chismis | {beta:.2f} |
| **γ (gamma)** | Gikusgon sa pagkakapoy | {gamma:.2f} |
| **R0 = β/γ** | Chismis reproduction number | {ratio_text(r_zero)} |

Kung **R0 > 1**, kasagaran mokusog ang pagkatag sa chismis.
Kung **R0 < 1**, dali ra kining mapalong.

**Koneksyon sa Monte Carlo (Report 2):**
Sa kada pagcontact, naay random draw kung mokatag ba ang chismis.
Kung daghanon nato ug dagan ang simulation, makita nato ang lain-laing posibleng resulta.
            """
            )

    st.markdown(
        """
    <div style="text-align:center; color:#5f6877; font-size:0.8em; margin-top:20px; padding:10px;">
        Computational Modeling - Report 3 - Agent-Based Models &nbsp;|&nbsp;
        <i>"Complexity comes from simple rules, labi na kung chismis na gani."</i>
    </div>
    """,
        unsafe_allow_html=True,
    )
