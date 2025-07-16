import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# ------------------------
# 🎯 Simulation Parameters
# ------------------------
st.title("🚀 Startup Scenario Simulator with Wargame Mode")

st.sidebar.header("🔧 Paramètres du scénario")

# Input parameters
cash_start = st.sidebar.slider("💰 Cash de départ (€)", 1000, 100000, 20000, step=1000)
burn_rate = st.sidebar.slider("🔥 Burn rate mensuel (€)", 500, 30000, 5000, step=500)
growth_rate = st.sidebar.slider("📈 Taux de croissance client/mois (%)", -50, 300, 20)
retention = st.sidebar.slider("🔁 Taux de rétention client (%)", 0, 100, 80)
market_shock_prob = st.sidebar.slider("⚡ Probabilité d'un choc marché (%)", 0, 100, 10)

# Wargame Mode
st.sidebar.markdown("---")
st.sidebar.header("🎮 Mode Wargame (concurrent virtuel)")
wargame_mode = st.sidebar.checkbox("Activer le mode Wargame")
if wargame_mode:
    competitor_growth = st.sidebar.slider("📊 Croissance du concurrent (%)", -20, 300, 25)
    competitor_aggressiveness = st.sidebar.slider("🪓 Impact du concurrent sur ton acquisition (%)", 0, 100, 30)

# Global parameters
total_months = st.sidebar.slider("📆 Durée de la simulation (mois)", 6, 36, 12)
num_simulations = st.sidebar.slider("🔄 Nombre de simulations", 100, 5000, 1000, step=100)

# ------------------------
# 🧠 Simulation Logic
# ------------------------
def run_simulation():
    results = []
    for _ in range(num_simulations):
        cash = cash_start
        clients = 100
        competitor_clients = 100 if wargame_mode else 0
        history = []

        for month in range(total_months):
            shock = np.random.rand() < (market_shock_prob / 100)
            effective_growth = growth_rate / 100 * (0.5 if shock else 1.0)

            if wargame_mode:
                competitor_clients *= 1 + (competitor_growth / 100)
                market_share_loss = (competitor_aggressiveness / 100) * (competitor_clients / (clients + competitor_clients))
                effective_growth *= max(0.0, 1 - market_share_loss)

            new_clients = clients * effective_growth
            clients = clients * (retention / 100) + new_clients

            revenue = clients * 10  # basic revenue per client
            cash += revenue - burn_rate

            history.append({
                "mois": month + 1,
                "cash": cash,
                "clients": clients,
                "shock": shock,
                "competitor_clients": competitor_clients if wargame_mode else None
            })

            if cash < 0:
                break

        final_cash = cash
        success = final_cash > 0
        results.append({"succès": success, "cash_final": final_cash, "durée": len(history), "data": history})

    return results

# ------------------------
# 📊 Run and Display Results
# ------------------------
st.subheader("📊 Résultats de la simulation")
sim_data = run_simulation()

success_rate = np.mean([s["succès"] for s in sim_data]) * 100
average_lifetime = np.mean([s["durée"] for s in sim_data])

st.metric("✅ Taux de survie du modèle", f"{success_rate:.1f}%")
st.metric("🕒 Durée moyenne avant échec ou succès", f"{average_lifetime:.1f} mois")

# Plotting example trajectory
example_trajectory = pd.DataFrame(sim_data[0]["data"])
line_chart = alt.Chart(example_trajectory).mark_line().encode(
    x="mois",
    y="cash",
    color=alt.value("#007BFF")
).properties(title="💸 Évolution du cash (exemple 1)")

st.altair_chart(line_chart, use_container_width=True)

# Histogram of final cash values
hist_data = pd.DataFrame({"cash_final": [s["cash_final"] for s in sim_data]})
chart = alt.Chart(hist_data).mark_bar().encode(
    alt.X("cash_final", bin=alt.Bin(maxbins=50), title="Cash final (€)"),
    y='count()',
    tooltip=['count()']
).properties(title="Distribution du cash final sur toutes les simulations")

st.altair_chart(chart, use_container_width=True)

# Recommendations
st.subheader("🧠 Recommandation stratégique")
if success_rate > 70:
    st.success("Bonne probabilité de succès. Envisage une croissance plus agressive ou une levée de fonds.")
elif success_rate > 40:
    st.warning("Modèle fragile. Optimise le burn rate ou augmente la rétention.")
else:
    st.error("Modèle trop risqué. Revoit la stratégie de croissance ou les coûts fixes.")

# Optional: Show competitor trajectory
if wargame_mode:
    st.subheader("🤺 Évolution du concurrent (exemple)")
    competitor_chart = alt.Chart(example_trajectory).mark_line(color='red').encode(
        x="mois",
        y="competitor_clients"
    ).properties(title="📊 Clients du concurrent dans le temps")
    st.altair_chart(competitor_chart, use_container_width=True)
