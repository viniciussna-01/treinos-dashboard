import streamlit as st
from datetime import date, timedelta
from sheets_db import load_checks, save_check
import matplotlib.pyplot as plt

st.set_page_config(page_title="🏊 Triathlon Sprint", page_icon="🏆", layout="wide")

# ======================
# SIDEBAR
# ======================

menu = st.sidebar.radio(
    "📍 Navegação",
    ["Treinos", "Análise"]
)

# ======================
# CONFIGURAÇÕES
# ======================

PROVA  = date(2026, 5, 30)
INICIO = date(2026, 3, 2)
DIAS   = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]

def fase(s):
    return 1 if s<=4 else 2 if s<=8 else 3 if s<=12 else 4

def treinos_do_dia(semana, dia, d):
    f = fase(semana)
    key = d.strftime("%Y%m%d")
    t = []

    if d == PROVA:
        t.append((f"{key}_prova","🏆","DIA DA PROVA!\nNado 750m → Bike 20km → Corrida 5km 🎉","prova"))
        return t

    if dia in (0,2):
        t.append((f"{key}_nat","🔵","Natação","nat"))

    if dia in (1,3):
        t.append((f"{key}_bike","🟢","Bike","bike"))

    if dia in (2,5):
        t.append((f"{key}_run","🔴","Corrida","run"))

    if dia == 6:
        t.append((f"{key}_brick","🟠","Brick","brick"))

    return t

def get_checks():
    return load_checks()

# ======================
# ABA TREINOS
# ======================

if menu == "Treinos":

    checks = get_checks()
    hoje = date.today()

    st.title("🏊‍♂️ Triathlon Sprint — João Pessoa 30/05/2026")
    st.markdown("---")

    semana_num = 0
    current = INICIO
    
    def update_check(key):
        value = st.session_state[key]
        save_check(key, value)
        st.toast("Salvo ✅")

    while current <= PROVA:
        semana_num += 1
        lun = current
        fim_sem = lun + timedelta(days=6)

        with st.expander(f"Semana {semana_num} · {lun.strftime('%d/%m')} – {fim_sem.strftime('%d/%m')}"):
            cols = st.columns(7)

            for dia in range(7):
                d = lun + timedelta(days=dia)

                with cols[dia]:
                    st.markdown(f"**{DIAS[dia]} {d.strftime('%d/%m')}**")

                    treinos = treinos_do_dia(semana_num, dia, d)

                    if not treinos:
                        st.write("😴 Descanso")
                    else:
                        for (tid,emoji,desc,tipo) in treinos:
                            feito = checks.get(tid, False)
                            st.write(f"{emoji} {desc}")

                            st.checkbox(
                                "Feito",
                                value=feito,
                                key=tid,
                                on_change=update_check,
                                args=(tid,)
                            )

        current = lun + timedelta(weeks=1)

    st.markdown("---")
    st.caption("💪 Nado 750m · Bike 20km · Corrida 5km")

# ======================
# ABA ANÁLISE
# ======================

background_color = "#0E1A2B"
azul_claro = "#4FC3F7"
azul_medio = "#2196F3"
azul_escuro = "#1565C0"

if menu == "Análise":

    checks = get_checks()

    st.title("📊 Análise de Progresso")
    st.header("Simbora Vinícius - VAI DAR CERTO! FOCO!")
    st.markdown("---")

    total = len(checks)
    feitos = sum(1 for v in checks.values() if v)
    percentual = (feitos / total * 100) if total > 0 else 0

    st.metric("Progresso Geral", f"{percentual:.1f}%")

    # ======================
    # CONTAGEM MODALIDADES
    # ======================

    modalidades = {
        "Natação": 0,
        "Bike": 0,
        "Corrida": 0,
        "Brick": 0
    }

    for key, value in checks.items():
        if value:
            if "_nat" in key:
                modalidades["Natação"] += 1
            elif "_bike" in key:
                modalidades["Bike"] += 1
            elif "_run" in key:
                modalidades["Corrida"] += 1
            elif "_brick" in key:
                modalidades["Brick"] += 1

def total_treinos_planejados():
    total = 0
    semana_num = 0
    current = INICIO

    while current <= PROVA:
        semana_num += 1

        for dia in range(7):
            d = current + timedelta(days=dia)

            if d > PROVA:
                break

            treinos = treinos_do_dia(semana_num, dia, d)
            total += len(treinos)

        current += timedelta(weeks=1)

    return total

    # ======================
    # COLUNAS LADO A LADO
    # ======================

    col1, col2 = st.columns(2)

    # -------- COLUNA 1 - Percentual --------
    with col1:

    total = total_treinos_planejados()
    feitos = sum(1 for v in checks.values() if v)
    restantes = total - feitos
    percentual = (feitos / total * 100) if total > 0 else 0

    fig1, ax1 = plt.subplots()

    fig1.patch.set_facecolor(background_color)
    ax1.set_facecolor(background_color)

    cores = [azul_medio, "#1B2A41"]  # azul progresso + azul escuro restante

    ax1.pie(
        [feitos, restantes],
        labels=["Concluídos", "Restantes"],
        autopct="%1.1f%%",
        startangle=90,
        colors=cores,
        textprops={"color": "white"}
    )

    ax1.set_title("Progresso Total até a Prova", color="white")

    # Círculo no meio (efeito donut)
    centre_circle = plt.Circle((0, 0), 0.70, fc=background_color)
    fig1.gca().add_artist(centre_circle)

    st.pyplot(fig1)

    # -------- COLUNA 2 - Modalidades --------
    with col2:
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(111)

        fig2.patch.set_facecolor(background_color)
        ax2.set_facecolor(background_color)

        cores = [azul_claro, azul_medio, azul_escuro, "#1E88E5"]

        ax2.bar(modalidades.keys(), modalidades.values(), color=cores)

        ax2.set_title("Treinos por Modalidade", color="white")
        ax2.tick_params(colors="white")
        ax2.spines["bottom"].set_color("white")
        ax2.spines["left"].set_color("white")

        plt.xticks(rotation=45)


        st.pyplot(fig2)




