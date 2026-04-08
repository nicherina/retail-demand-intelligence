"""
Data Quality & Decision Intelligence Profiler
=============================================
Built by Nisrina Afnan Walyadin

A production-grade data quality assessment tool demonstrating
end-to-end analytical workflow — from raw data to actionable
business insights. Relevant to AI delivery, consulting, and
data product roles.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import re
from datetime import datetime

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Quality Profiler | Nisrina Walyadin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main { background-color: #f8f9fa; }

    .score-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .score-number {
        font-size: 3rem;
        font-weight: 700;
        font-family: 'IBM Plex Mono', monospace;
        line-height: 1;
    }
    .score-label {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.4rem;
    }
    .score-green  { color: #0a7c45; }
    .score-amber  { color: #d68910; }
    .score-red    { color: #c0392b; }

    .gate-pass   { background:#d4edda; color:#155724; border:1px solid #c3e6cb; border-radius:8px; padding:0.6rem 1.2rem; font-weight:600; font-size:0.9rem; display:inline-block; }
    .gate-warn   { background:#fff3cd; color:#856404; border:1px solid #ffeeba; border-radius:8px; padding:0.6rem 1.2rem; font-weight:600; font-size:0.9rem; display:inline-block; }
    .gate-block  { background:#f8d7da; color:#721c24; border:1px solid #f5c6cb; border-radius:8px; padding:0.6rem 1.2rem; font-weight:600; font-size:0.9rem; display:inline-block; }

    .issue-item {
        background: #fff8e1;
        border-left: 3px solid #f39c12;
        padding: 0.5rem 0.75rem;
        margin: 0.3rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.82rem;
    }
    .issue-critical { border-left-color: #e74c3c; background: #fdecea; }
    .issue-ok       { border-left-color: #27ae60; background: #eafaf1; }

    .section-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #1a73e8;
        margin-bottom: 0.5rem;
        margin-top: 1.5rem;
    }

    .chip {
        display: inline-block;
        background: #f0f4ff;
        border: 1px solid #d0dbff;
        border-radius: 20px;
        padding: 0.2rem 0.7rem;
        font-size: 0.72rem;
        color: #1a73e8;
        margin: 0.15rem;
        font-family: 'IBM Plex Mono', monospace;
    }

    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.72rem;
        padding: 2rem 0 1rem;
        font-family: 'IBM Plex Mono', monospace;
    }
    .stAlert { border-radius: 8px; }
    div[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace; }
</style>
""", unsafe_allow_html=True)


# ── HELPER FUNCTIONS ───────────────────────────────────────────────────────────

def detect_column_type(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "categorical"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    try:
        pd.to_datetime(series.dropna().head(50), infer_datetime_format=True)
        return "datetime"
    except Exception:
        pass
    if series.nunique() / max(len(series), 1) < 0.05 and series.nunique() <= 50:
        return "categorical"
    return "text"


def compute_completeness(df: pd.DataFrame) -> pd.Series:
    return 1 - df.isnull().mean()


def compute_validity(df: pd.DataFrame) -> dict:
    results = {}
    for col in df.columns:
        ct = detect_column_type(df[col])
        if ct == "numeric":
            q1, q99 = df[col].quantile(0.01), df[col].quantile(0.99)
            iqr = q99 - q1
            outliers = ((df[col] < q1 - 3 * iqr) | (df[col] > q99 + 3 * iqr)).sum()
            results[col] = {"type": ct, "outliers": int(outliers),
                            "outlier_rate": outliers / max(len(df[col].dropna()), 1)}
        elif ct == "categorical":
            results[col] = {"type": ct, "unique": df[col].nunique(),
                            "top_value": df[col].mode()[0] if not df[col].mode().empty else "N/A"}
        else:
            results[col] = {"type": ct}
    return results


def compute_duplicate_rate(df: pd.DataFrame) -> float:
    return df.duplicated().mean()


def compute_quality_score(completeness: pd.Series, dup_rate: float, validity: dict) -> float:
    comp_score = completeness.mean() * 40
    dup_score  = max(0, (1 - dup_rate * 10)) * 20
    outlier_rates = [v.get("outlier_rate", 0) for v in validity.values() if v.get("type") == "numeric"]
    avg_outlier = np.mean(outlier_rates) if outlier_rates else 0
    validity_score = max(0, (1 - avg_outlier * 5)) * 40
    return round(min(100, comp_score + dup_score + validity_score), 1)


def gate_decision(score: float) -> tuple:
    if score >= 85:
        return "✅ PIPELINE PASS", "pass", "#0a7c45"
    elif score >= 65:
        return "⚠️ REVIEW REQUIRED", "warn", "#d68910"
    else:
        return "🚫 PIPELINE BLOCKED", "block", "#c0392b"


def generate_recommendations(completeness: pd.Series, dup_rate: float,
                               validity: dict, df: pd.DataFrame) -> list:
    recs = []
    low_comp = completeness[completeness < 0.90]
    if not low_comp.empty:
        cols = ", ".join(low_comp.index[:3].tolist())
        recs.append(("🔴 Critical", f"Completeness below 90% in: **{cols}**. Investigate data source or apply imputation strategy."))
    med_comp = completeness[(completeness >= 0.90) & (completeness < 0.97)]
    if not med_comp.empty:
        cols = ", ".join(med_comp.index[:3].tolist())
        recs.append(("🟡 Warning", f"Moderate null rate in: **{cols}**. Consider forward-fill or median imputation."))
    if dup_rate > 0.02:
        n_dupes = int(dup_rate * len(df))
        recs.append(("🔴 Critical", f"**{n_dupes:,} duplicate rows** detected ({dup_rate*100:.1f}%). Deduplication required before downstream use."))
    for col, v in validity.items():
        if v.get("type") == "numeric" and v.get("outlier_rate", 0) > 0.05:
            recs.append(("🟡 Warning", f"Column **{col}** has high outlier rate ({v['outlier_rate']*100:.1f}%). Verify business rules and cap/null extreme values."))
    if not recs:
        recs.append(("🟢 Good", "No critical issues detected. Data quality is acceptable for downstream processing."))
    return recs


def generate_remediation_log(df: pd.DataFrame, completeness: pd.Series,
                              dup_rate: float) -> tuple:
    log = []
    clean = df.copy()
    original_rows = len(clean)

    dupes_removed = clean.duplicated().sum()
    clean = clean.drop_duplicates()
    if dupes_removed > 0:
        log.append(f"[DEDUP]      Removed {dupes_removed:,} duplicate rows")

    for col in clean.columns:
        if clean[col].isnull().mean() > 0:
            ct = detect_column_type(clean[col])
            if ct == "numeric":
                median_val = clean[col].median()
                n_filled = clean[col].isnull().sum()
                clean[col] = clean[col].fillna(median_val)
                log.append(f"[IMPUTE]     {col}: filled {n_filled:,} nulls with median ({median_val:.2f})")
            elif ct == "categorical":
                mode_val = clean[col].mode()[0] if not clean[col].mode().empty else "UNKNOWN"
                n_filled = clean[col].isnull().sum()
                clean[col] = clean[col].fillna(mode_val)
                log.append(f"[IMPUTE]     {col}: filled {n_filled:,} nulls with mode ('{mode_val}')")
            else:
                n_flagged = clean[col].isnull().sum()
                clean[col] = clean[col].fillna("MISSING")
                log.append(f"[FLAG]       {col}: flagged {n_flagged:,} missing text values → 'MISSING'")

    clean["_dq_remediated"] = True
    clean["_dq_timestamp"]  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.append(f"[AUDIT]      Added _dq_remediated and _dq_timestamp columns")
    log.append(f"[SUMMARY]    Rows: {original_rows:,} → {len(clean):,} | Columns: {df.shape[1]} → {clean.shape[1]}")
    return clean, log


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Data Quality Profiler")
    st.markdown("""
    <div style='font-size:0.8rem; color:#555; line-height:1.6;'>
    Upload any CSV/Excel file to get an instant<br/>
    data quality assessment, pipeline gate decision,<br/>
    automated remediation, and business recommendations.
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    uploaded = st.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx", "xls"],
        help="CSV or Excel file, max 200MB"
    )

    st.divider()
    st.markdown("**Settings**")
    pass_threshold = st.slider("Pass threshold (score ≥)", 70, 95, 85, 1)
    warn_threshold = st.slider("Warn threshold (score ≥)", 50, 84, 65, 1)
    sample_size    = st.selectbox("Analysis sample", ["Full dataset", "10,000 rows", "5,000 rows", "1,000 rows"])

    st.divider()
    st.markdown("""
    <div style='font-size:0.72rem; color:#aaa; font-family: monospace;'>
    Built by <b>Nisrina Walyadin</b><br/>
    MSc Mathematics, TU Munich<br/>
    <a href='https://www.linkedin.com/in/nisrina-walyadin-5b7345178/' target='_blank'>LinkedIn</a> ·
    <a href='https://nicherina.github.io/nisrinawalyadin.github.io/' target='_blank'>Portfolio</a>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    use_demo = st.button("🎲 Load demo dataset", use_container_width=True)


# ── DEMO DATA GENERATOR ────────────────────────────────────────────────────────
def make_demo_data() -> pd.DataFrame:
    np.random.seed(42)
    n = 2000
    markets = np.random.choice(["DE","AT","PL","CZ","SK"], n, p=[0.45,0.12,0.18,0.15,0.10])
    cats    = np.random.choice(["fashion","home","lingerie","hard_goods"], n)
    revenue = np.random.lognormal(6.5, 0.9, n).round(2)
    units   = np.random.lognormal(3.5, 0.8, n).astype(int)

    df = pd.DataFrame({
        "store_id":    [f"ST{str(i).zfill(4)}" for i in np.random.randint(1,1500,n)],
        "market":      markets,
        "category":    cats,
        "revenue_eur": revenue,
        "units_sold":  units,
        "week_start":  pd.date_range("2024-01-01", periods=n, freq="D").strftime("%Y-%m-%d"),
        "promo_flag":  np.random.choice([0,1], n, p=[0.78,0.22]),
        "data_source": np.random.choice(["ERP_v2","ERP_v1","MANUAL","API"], n, p=[0.65,0.15,0.12,0.08]),
    })
    mask1 = np.random.random(n) < 0.18
    df.loc[mask1, "category"] = np.nan
    mask2 = np.random.random(n) < 0.06
    df.loc[mask2, "revenue_eur"] = -df.loc[mask2, "revenue_eur"]
    mask3 = np.random.random(n) < 0.03
    df.loc[mask3, "units_sold"] = np.random.randint(100000, 999999, mask3.sum())
    mask4 = np.random.random(n) < 0.08
    df.loc[mask4, "market"] = np.nan
    dupes = df.sample(frac=0.04, random_state=99)
    df = pd.concat([df, dupes], ignore_index=True)
    return df.sample(frac=1, random_state=7).reset_index(drop=True)


# ── MAIN APP ───────────────────────────────────────────────────────────────────

st.title("Data Quality & Decision Intelligence Profiler")
st.markdown(
    "<span class='chip'>Completeness</span>"
    "<span class='chip'>Validity</span>"
    "<span class='chip'>Duplicates</span>"
    "<span class='chip'>Pipeline Gate</span>"
    "<span class='chip'>Auto-Remediation</span>"
    "<span class='chip'>Business Insights</span>",
    unsafe_allow_html=True
)

# Load data — use session_state to persist across reruns
if "df_raw" not in st.session_state:
    st.session_state.df_raw = None
    st.session_state.source_label = ""

if use_demo:
    st.session_state.df_raw = make_demo_data()
    st.session_state.source_label = "Demo Dataset — Retail Multi-Market (simulated)"
    st.success("✓ Demo dataset loaded — 2,000+ rows with injected quality issues")

elif uploaded:
    try:
        if uploaded.name.endswith(".csv"):
            st.session_state.df_raw = pd.read_csv(uploaded)
        else:
            st.session_state.df_raw = pd.read_excel(uploaded)
        st.session_state.source_label = uploaded.name
        st.success(f"✓ Loaded **{uploaded.name}** — {st.session_state.df_raw.shape[0]:,} rows × {st.session_state.df_raw.shape[1]} columns")
    except Exception as e:
        st.error(f"Error reading file: {e}")

df_raw = st.session_state.df_raw
source_label = st.session_state.source_label

if df_raw is None:
    # ── LANDING STATE ──────────────────────────────────────────────────────────
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 📤 Upload your data
        Drop any CSV or Excel file in the sidebar to get an instant quality report.
        """)
    with col2:
        st.markdown("""
        ### 🎲 Try the demo
        Click **Load demo dataset** in the sidebar to see the profiler in action with a retail dataset.
        """)
    with col3:
        st.markdown("""
        ### 📋 What you get
        Quality score · Pipeline gate · Column-level analysis · Auto-remediation · Clean export
        """)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; padding: 3rem 0; color: #aaa;'>
        <div style='font-size: 3rem;'>📊</div>
        <div style='font-size: 1rem; margin-top: 0.5rem;'>Waiting for data...</div>
        <div style='font-size: 0.8rem; margin-top: 0.25rem;'>Upload a file or load the demo to begin</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='footer'>
    Nisrina Afnan Walyadin · MSc Mathematics, TU Munich · nisrinawalyadin@gmail.com
    </div>
    """, unsafe_allow_html=True)

else:
    # ── ANALYSIS (only runs when data is loaded) ───────────────────────────────

    # Sample
    sample_map = {
        "Full dataset": len(df_raw),
        "10,000 rows": 10000,
        "5,000 rows": 5000,
        "1,000 rows": 1000,
    }
    n_sample = sample_map[sample_size]
    df = df_raw.head(n_sample).copy()

    # Compute metrics
    completeness = compute_completeness(df)
    dup_rate     = compute_duplicate_rate(df)
    validity     = compute_validity(df)
    score        = compute_quality_score(completeness, dup_rate, validity)

    if score >= pass_threshold:
        gate_label, gate_class, gate_color = "✅ PIPELINE PASS", "pass", "#0a7c45"
    elif score >= warn_threshold:
        gate_label, gate_class, gate_color = "⚠️ REVIEW REQUIRED", "warn", "#d68910"
    else:
        gate_label, gate_class, gate_color = "🚫 PIPELINE BLOCKED", "block", "#c0392b"

    score_color_class = "score-green" if score >= pass_threshold else ("score-amber" if score >= warn_threshold else "score-red")
    recommendations = generate_recommendations(completeness, dup_rate, validity, df)

    # ── OVERVIEW ROW ───────────────────────────────────────────────────────────
    st.markdown(f"<div class='section-header'>Dataset Overview · {source_label}</div>", unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f"""
        <div class='score-card'>
            <div class='score-number {score_color_class}'>{score}</div>
            <div class='score-label'>Quality Score / 100</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.metric("Rows", f"{len(df):,}")
    with c3:
        st.metric("Columns", df.shape[1])
    with c4:
        null_pct = df.isnull().mean().mean() * 100
        st.metric("Avg Null Rate", f"{null_pct:.1f}%", delta=f"{-null_pct:.1f}%" if null_pct > 0 else None, delta_color="inverse")
    with c5:
        st.metric("Duplicate Rows", f"{int(dup_rate*len(df)):,}", delta=f"{dup_rate*100:.1f}%" if dup_rate > 0 else "0%", delta_color="inverse")
    with c6:
        n_issues = sum(1 for r in recommendations if "Critical" in r[0] or "Warning" in r[0])
        st.metric("Issues Found", n_issues)

    st.markdown("<br/>", unsafe_allow_html=True)
    gate_css = {"pass": "gate-pass", "warn": "gate-warn", "block": "gate-block"}[gate_class]
    st.markdown(f"<div class='{gate_css}'>{gate_label} — Score: {score}/100</div>", unsafe_allow_html=True)

    st.divider()

    # ── TABS ───────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Column Profiling",
        "📈 Visual Analysis",
        "⚠️ Issues & Recommendations",
        "🔧 Auto-Remediation",
        "📄 Data Preview"
    ])

    # ── TAB 1: COLUMN PROFILING ────────────────────────────────────────────────
    with tab1:
        st.markdown("<div class='section-header'>Column-level Quality Assessment</div>", unsafe_allow_html=True)

        profile_rows = []
        for col in df.columns:
            ct    = detect_column_type(df[col])
            comp  = completeness[col]
            nulls = int(df[col].isnull().sum())
            uniq  = df[col].nunique()
            vinfo = validity.get(col, {})
            status = "🟢 OK" if comp >= 0.97 else ("🟡 Warn" if comp >= 0.90 else "🔴 Issue")
            profile_rows.append({
                "Column":        col,
                "Type":          ct,
                "Completeness":  f"{comp*100:.1f}%",
                "Null Count":    nulls,
                "Unique Values": uniq,
                "Outliers":      vinfo.get("outliers", "—"),
                "Status":        status,
            })

        st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, height=400)

        fig_comp = px.bar(
            x=completeness.index,
            y=completeness.values * 100,
            color=completeness.values * 100,
            color_continuous_scale=[[0,"#e74c3c"],[0.90,"#f39c12"],[1,"#27ae60"]],
            labels={"x":"Column","y":"Completeness (%)","color":""},
            title="Column Completeness (%)",
            height=320,
        )
        fig_comp.add_hline(y=97, line_dash="dot", line_color="#27ae60", annotation_text="97% threshold")
        fig_comp.add_hline(y=90, line_dash="dot", line_color="#f39c12", annotation_text="90% warning")
        fig_comp.update_layout(paper_bgcolor="white", plot_bgcolor="#fafafa",
                               coloraxis_showscale=False, margin=dict(t=40,b=20))
        st.plotly_chart(fig_comp, use_container_width=True)

    # ── TAB 2: VISUAL ANALYSIS ─────────────────────────────────────────────────
    with tab2:
        st.markdown("<div class='section-header'>Data Distribution & Pattern Analysis</div>", unsafe_allow_html=True)

        numeric_cols = [c for c in df.columns if detect_column_type(df[c]) == "numeric"]
        cat_cols     = [c for c in df.columns if detect_column_type(df[c]) == "categorical"]

        if numeric_cols:
            st.markdown("**Numeric Distributions**")
            n_num = len(numeric_cols)
            cols_per_row = min(3, n_num)
            rows_needed  = (n_num + cols_per_row - 1) // cols_per_row
            fig_num = make_subplots(rows=rows_needed, cols=cols_per_row,
                                    subplot_titles=numeric_cols)
            for idx, col in enumerate(numeric_cols):
                row     = idx // cols_per_row + 1
                col_pos = idx % cols_per_row + 1
                fig_num.add_trace(
                    go.Histogram(x=df[col].dropna(), name=col, showlegend=False,
                                 marker_color="#1a73e8", opacity=0.75, nbinsx=30),
                    row=row, col=col_pos
                )
            fig_num.update_layout(height=280 * rows_needed, paper_bgcolor="white",
                                  plot_bgcolor="#fafafa", margin=dict(t=40,b=20))
            st.plotly_chart(fig_num, use_container_width=True)

        if cat_cols:
            st.markdown("**Categorical Value Distributions**")
            sel_cat = st.selectbox("Select column", cat_cols)
            vc = df[sel_cat].value_counts().head(15).reset_index()
            vc.columns = ["value","count"]
            fig_cat = px.bar(vc, x="count", y="value", orientation="h",
                             color="count", color_continuous_scale="Blues",
                             title=f"Top values — {sel_cat}", height=350)
            fig_cat.update_layout(paper_bgcolor="white", plot_bgcolor="#fafafa",
                                  coloraxis_showscale=False, margin=dict(t=40,b=20),
                                  yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown("**Missing Data Heatmap** (sample of 200 rows)")
        fig_heat = px.imshow(
            df.isnull().head(200).astype(int).T,
            color_continuous_scale=[[0,"#eafaf1"],[1,"#e74c3c"]],
            aspect="auto",
            title="Missing values (red = null)",
            height=max(200, len(df.columns) * 22),
            labels=dict(color="Is Null"),
        )
        fig_heat.update_layout(paper_bgcolor="white", margin=dict(t=40,b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── TAB 3: ISSUES & RECOMMENDATIONS ───────────────────────────────────────
    with tab3:
        st.markdown("<div class='section-header'>Issues Found & Business Recommendations</div>", unsafe_allow_html=True)

        for severity, message in recommendations:
            if "Critical" in severity:
                st.markdown(f"<div class='issue-item issue-critical'><b>{severity}</b> — {message}</div>",
                            unsafe_allow_html=True)
            elif "Warning" in severity:
                st.markdown(f"<div class='issue-item'><b>{severity}</b> — {message}</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='issue-item issue-ok'><b>{severity}</b> — {message}</div>",
                            unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Quality Score Breakdown</div>", unsafe_allow_html=True)

        comp_score = completeness.mean() * 40
        dup_score  = max(0, (1 - dup_rate * 10)) * 20
        out_rates  = [v.get("outlier_rate", 0) for v in validity.values() if v.get("type") == "numeric"]
        val_score  = max(0, (1 - (np.mean(out_rates) if out_rates else 0) * 5)) * 40

        fig_score = go.Figure(go.Bar(
            x=["Completeness\n(40pts)", "Uniqueness\n(20pts)", "Validity\n(40pts)"],
            y=[round(comp_score,1), round(dup_score,1), round(val_score,1)],
            marker_color=["#1a73e8","#34a853","#fbbc04"],
            text=[f"{v:.1f}" for v in [comp_score, dup_score, val_score]],
            textposition="outside",
        ))
        fig_score.add_hline(y=score, line_dash="dot", line_color="#e74c3c",
                            annotation_text=f"Total: {score}/100")
        fig_score.update_layout(title="Score Components", yaxis_range=[0,45],
                                paper_bgcolor="white", plot_bgcolor="#fafafa",
                                height=300, margin=dict(t=40,b=20))
        st.plotly_chart(fig_score, use_container_width=True)

    # ── TAB 4: AUTO-REMEDIATION ────────────────────────────────────────────────
    with tab4:
        st.markdown("<div class='section-header'>Automated Remediation Pipeline</div>", unsafe_allow_html=True)
        st.markdown("""
        The remediation pipeline applies standard data cleaning rules with full audit logging.
        All actions are transparent and reversible — no silent data mutations.
        """)

        if st.button("▶ Run Remediation Pipeline", type="primary", use_container_width=True):
            with st.spinner("Running pipeline..."):
                df_clean, log = generate_remediation_log(df, completeness, dup_rate)
                comp2  = compute_completeness(df_clean.drop(columns=["_dq_remediated","_dq_timestamp"], errors="ignore"))
                score2 = compute_quality_score(comp2, 0.0, compute_validity(df_clean))

            st.success(f"Pipeline complete — quality score: {score} → **{score2}/100** (+{score2-score:.1f}pts)")

            st.markdown("**Remediation Log (full audit trail):**")
            for entry in log:
                st.code(entry, language=None)

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Before — Null Rate", f"{df.isnull().mean().mean()*100:.1f}%")
                st.metric("Before — Duplicates", f"{int(dup_rate*len(df)):,}")
                st.metric("Before — Score", f"{score}/100")
            with col_b:
                st.metric("After — Null Rate", "0.0%", delta=f"-{df.isnull().mean().mean()*100:.1f}pp", delta_color="inverse")
                st.metric("After — Duplicates", "0", delta=f"-{int(dup_rate*len(df)):,}", delta_color="inverse")
                st.metric("After — Score", f"{score2}/100", delta=f"+{score2-score:.1f}")

            csv_buffer = io.StringIO()
            df_clean.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇ Download clean dataset (CSV)",
                data=csv_buffer.getvalue(),
                file_name=f"clean_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("Click the button above to run the automated remediation pipeline on your dataset.")

    # ── TAB 5: DATA PREVIEW ────────────────────────────────────────────────────
    with tab5:
        st.markdown("<div class='section-header'>Raw Data Preview</div>", unsafe_allow_html=True)
        n_preview = st.slider("Rows to preview", 10, min(500, len(df)), 50, 10)
        st.dataframe(df.head(n_preview), use_container_width=True, height=450)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("⬇ Download sample (CSV)", df.to_csv(index=False),
                               file_name="sample_data.csv", mime="text/csv",
                               use_container_width=True)
        with col_dl2:
            profile_text  = f"Data Quality Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            profile_text += f"Source: {source_label}\n"
            profile_text += f"Rows: {len(df):,} | Columns: {df.shape[1]}\n"
            profile_text += f"Quality Score: {score}/100\n"
            profile_text += f"Gate: {gate_label}\n\nIssues:\n"
            for sev, msg in recommendations:
                profile_text += f"  [{sev}] {re.sub(r'\\*\\*(.+?)\\*\\*', r'\\1', msg)}\n"
            st.download_button("⬇ Download quality report (TXT)", profile_text,
                               file_name="quality_report.txt", mime="text/plain",
                               use_container_width=True)

    # ── FOOTER ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='footer'>
        Data Quality & Decision Intelligence Profiler · Built by Nisrina Afnan Walyadin<br/>
        MSc Mathematics, TU Munich · nisrinawalyadin@gmail.com ·
        <a href='https://www.linkedin.com/in/nisrina-walyadin-5b7345178/' target='_blank'>LinkedIn</a> ·
        <a href='https://github.com/nicherina' target='_blank'>Portfolio</a>

    </div>
    """, unsafe_allow_html=True)
