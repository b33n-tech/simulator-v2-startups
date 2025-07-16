import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# ------------------------
# 🎯 Simulation Parameters
# ------------------------
st.title("🚀 Startup Scenario Simulator: Multi-Actors & Wargame Mode")

st.sidebar.header("🔧 Paramètres du scénario")

# Input parameters
cash_start = st.sidebar.slider("💰 Cash de départ (€)", 1000, 100000, 20000, step=1000)
burn_rate = st.sidebar.slider("🔥 Burn rate mensuel (€)", 500, 30000, 5000, step=500)
growth_rate_input = st.sidebar.slider("📈 Taux de croissance client/mois (%)", -50, 300, 20)
retention_input = st.sidebar.slider("🔁 Taux de rétention client (%)", 0, 100, 80)
market_shock_prob = st.sidebar.slider("⚡ Probabilité d'un choc marché (%)", 0, 100, 10)
event_chance = st.sidebar.slider("🎲 Probabilité d'un événement stratégique/mois (%)", 0, 100, 20)

# Wargame Mode
st.sidebar.markdown("---")
st.sidebar.header("🎮 Mode Wargame Avancé")
wargame_mode = st.sidebar.checkbox("Activer le mode Wargame (multi-acteurs)")
num_competitors = st.sidebar.slider("Nombre de concurrents", 0, 3, 2) if wargame_mode else 0
competitors = []

for i in range(num_competitors):
    growth = st.sidebar.slider(f"📊 Croissance du concurrent {i+1} (%)", -20, 300, 25, key=f"c_growth_{i}")
    aggressiveness = st.sidebar.slider(f"🪓 Agressivité concurrent {i+1} (%)", 0, 100, 30, key=f"c_aggr_{i}")
    competitors.append({"growth": growth, "aggressiveness": aggressiveness})

# Global parameters
total_months = st.sidebar.slider("📆 Durée de la simulation (mois)", 6, 36, 12)
num_simulations = st.sidebar.slider("🔄 Nombre de simulations", 100, 5000, 1000, step=100)

# ------------------------
# 🧠 Simulation Logic
# ------------------------
def run_simulation(growth_rate_init, retention_init):
    results = []
    for _ in range(num_simulations):
        cash = cash_start
        clients = 100
        growth_rate = growth_rate_init
        retention = retention_init
        comp_clients = [100 for _ in competitors]
        history = []

        for month in range(total_months):
            shock = np.random.rand() < (market_shock_prob / 100)
            event_triggered = np.random.rand() < (event_chance / 100)

            effective_growth = growth_rate / 100 * (0.5 if shock else 1.0)

            if wargame_mode:
                for i, comp in enumerate(competitors):
                    comp_clients[i] *= 1 + (comp["growth"] / 100)
                    market_share_loss = (comp["aggressiveness"] / 100) * (comp_clients[i] / (clients + sum(comp_clients)))
                    effective_growth *= max(0.0, 1 - market_share_loss)

            if event_triggered:
                event_type = np.random.choice(["Levée de fonds", "Partenariat stratégique", "Bug critique", "Crise réputationnelle"])
                if event_type == "Levée de fonds":
                    cash += 20000
                elif event_type == "Partenariat stratégique":
                    growth_rate *= 1.2
                elif event_type == "Bug critique":
                    retention *= 0.9
                elif event_type == "Crise réputationnelle":
                    growth_rate *= 0.7
            else:
                event_type = None

            new_clients = clients * effective_growth
            clients = clients * (retention / 100) + new_clients

            revenue = clients * 10  # basic revenue per client
            cash += revenue - burn_rate

            history.append({
                "mois": month + 1,
                "cash": cash,
                "clients": clients,
                "shock": shock,
                "event": event_type,
                **{f"competitor_{i+1}_clients": cc for i, cc in enumerate(comp_clients)}
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
sim_data = run_simulation(growth_rate_input, retention_input)

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

# Optional: Show competitors
if wargame_mode:
    for i in range(num_competitors):
        st.subheader(f"🤺 Concurrents - Évolution du concurrent {i+1} (exemple)")
        comp_chart = alt.Chart(example_trajectory).mark_line().encode(
            x="mois",
            y=f"competitor_{i+1}_clients",
            color=alt.value(["#FF4136", "#FF851B", "#B10DC9"][i % 3])
        ).properties(title=f"📊 Clients du concurrent {i+1}")
        st.altair_chart(comp_chart, use_container_width=True)

# Optional: Show events
event_list = example_trajectory.dropna(subset=["event"])[["mois", "event"]]
if not event_list.empty:
    st.subheader("📌 Événements stratégiques sur la trajectoire exemple")
    st.dataframe(event_list)
