import streamlit as st
import json
import hashlib
from pathlib import Path

st.set_page_config(page_title="手残りシミュレーション", page_icon="💰", layout="wide")

# ──────────────────────────────
# デザインCSS（ゴールド × ダークネイビー）
# ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');

/* 全体 */
.stApp {
    background-color: #0a1628;
    color: #e8e8e8;
    font-family: 'Noto Sans JP', sans-serif;
}

/* ヘッダー非表示 */
header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* メインコンテナ */
.block-container {
    max-width: 800px;
    padding: 2rem 1.5rem;
}

/* ゴールドヘッダー */
.gold-header {
    background: linear-gradient(135deg, #b8860b 0%, #daa520 50%, #b8860b 100%);
    color: #0a1628;
    padding: 40px 30px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 4px 20px rgba(218, 165, 32, 0.3);
}
.gold-header h1 {
    font-size: 28px;
    font-weight: 900;
    margin-bottom: 8px;
    letter-spacing: 1px;
}
.gold-header p {
    font-size: 14px;
    opacity: 0.85;
    margin: 0;
}

/* セクションカード */
.section-card {
    background: linear-gradient(145deg, #111d35, #162040);
    border: 1px solid #253560;
    border-radius: 12px;
    padding: 28px;
    margin: 20px 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.section-card h2 {
    color: #daa520;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #253560;
}

/* ゴールドのメトリクスカード */
.metric-card {
    background: linear-gradient(145deg, #162040, #1a2850);
    border: 1px solid #253560;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    margin: 8px 0;
}
.metric-card .label {
    color: #8899bb;
    font-size: 13px;
    margin-bottom: 6px;
}
.metric-card .value {
    color: #daa520;
    font-size: 28px;
    font-weight: 900;
}
.metric-card .value-white {
    color: #ffffff;
    font-size: 28px;
    font-weight: 900;
}
.metric-card-highlight {
    background: linear-gradient(145deg, #1a2040, #1e2850);
    border: 2px solid #daa520;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    margin: 8px 0;
    box-shadow: 0 0 15px rgba(218, 165, 32, 0.15);
}

/* ポイント吹き出し */
.point-box {
    background: linear-gradient(145deg, #1a2545, #1e2d55);
    border-left: 4px solid #daa520;
    border-radius: 0 10px 10px 0;
    padding: 18px 22px;
    margin: 16px 0;
    color: #c8d0e0;
    font-size: 15px;
    line-height: 1.7;
}
.point-box strong { color: #daa520; }

/* 利回りカード */
.rate-card {
    border-radius: 10px;
    padding: 22px;
    text-align: center;
    margin: 8px 0;
}
.rate-card .rate-label {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 8px;
}
.rate-card .rate-value {
    font-size: 30px;
    font-weight: 900;
    margin-bottom: 4px;
}
.rate-card .rate-sub {
    font-size: 12px;
    opacity: 0.7;
}
.rate-3 {
    background: linear-gradient(145deg, #1a3030, #1e3838);
    border: 1px solid #2d6b5a;
}
.rate-3 .rate-label { color: #4ecdc4; }
.rate-3 .rate-value { color: #4ecdc4; }

.rate-5 {
    background: linear-gradient(145deg, #1a2545, #1e2d55);
    border: 2px solid #daa520;
    box-shadow: 0 0 15px rgba(218, 165, 32, 0.15);
}
.rate-5 .rate-label { color: #daa520; }
.rate-5 .rate-value { color: #daa520; }

.rate-8 {
    background: linear-gradient(145deg, #2a1a35, #351e45);
    border: 1px solid #6b3fa0;
}
.rate-8 .rate-label { color: #a88beb; }
.rate-8 .rate-value { color: #a88beb; }

/* まとめテーブル */
.summary-table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
}
.summary-table th {
    background: #1a2545;
    color: #8899bb;
    padding: 12px 16px;
    text-align: left;
    font-weight: 700;
    font-size: 14px;
    border-bottom: 2px solid #253560;
}
.summary-table td {
    padding: 14px 16px;
    border-bottom: 1px solid #1e2d50;
    font-size: 15px;
    color: #c8d0e0;
}
.summary-table .total-row td {
    border-top: 2px solid #daa520;
    color: #daa520;
    font-weight: 900;
    font-size: 18px;
    padding-top: 16px;
}

/* CTA */
.cta-box {
    background: linear-gradient(135deg, #b8860b 0%, #daa520 50%, #b8860b 100%);
    color: #0a1628;
    padding: 35px 30px;
    border-radius: 12px;
    text-align: center;
    margin: 30px 0;
    box-shadow: 0 4px 20px rgba(218, 165, 32, 0.3);
}
.cta-box h2 {
    font-size: 22px;
    font-weight: 900;
    margin-bottom: 12px;
    color: #0a1628;
}
.cta-box p {
    font-size: 15px;
    color: #1a2545;
    line-height: 1.8;
    margin-bottom: 8px;
}
.cta-box .cta-button {
    display: inline-block;
    background: #0a1628;
    color: #daa520;
    padding: 14px 40px;
    font-size: 18px;
    font-weight: 700;
    text-decoration: none;
    border-radius: 8px;
    margin-top: 15px;
    border: 2px solid #0a1628;
}

/* フッター */
.footer-note {
    color: #556080;
    font-size: 11px;
    line-height: 1.6;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #1e2d50;
}

/* Streamlitデフォルトの上書き */
.stMetric label { color: #8899bb !important; }
.stMetric [data-testid="stMetricValue"] { color: #daa520 !important; }
div[data-testid="stForm"] {
    background: #111d35;
    border: 1px solid #253560;
    border-radius: 12px;
    padding: 24px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────
# データ保存先
# ──────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ──────────────────────────────
# シミュレーション計算
# ──────────────────────────────
def calc_simulation(age, until_age, monthly_contribution):
    years = until_age - age
    if years <= 0:
        return None

    monthly = monthly_contribution
    annual = monthly * 12
    total_principal = annual * years

    def future_value(rate, months):
        if rate == 0:
            return monthly * months
        r = rate / 12
        return monthly * (((1 + r) ** months - 1) / r)

    months = years * 12
    fv_3 = future_value(0.03, months)
    fv_5 = future_value(0.05, months)
    fv_8 = future_value(0.08, months)

    # 年ごとの資産推移（グラフ用）
    yearly_data = []
    for y in range(1, years + 1):
        m = y * 12
        yearly_data.append({
            "年目": y,
            "元本": annual * y,
            "利回り3%": future_value(0.03, m),
            "利回り5%": future_value(0.05, m),
            "利回り8%": future_value(0.08, m),
        })

    tax_rate = 0.30
    annual_tax_saving = annual * tax_rate
    total_tax_saving = annual_tax_saving * years

    return {
        "age": age,
        "until_age": until_age,
        "years": years,
        "monthly": monthly,
        "annual": annual,
        "total_principal": total_principal,
        "fv_3": fv_3,
        "fv_5": fv_5,
        "fv_8": fv_8,
        "gain_3": fv_3 - total_principal,
        "gain_5": fv_5 - total_principal,
        "gain_8": fv_8 - total_principal,
        "annual_tax_saving": annual_tax_saving,
        "total_tax_saving": total_tax_saving,
        "tax_rate": tax_rate,
        "yearly_data": yearly_data,
    }


def save_data(email, age, until_age, monthly_contribution, result):
    record = {
        "email": email,
        "age": age,
        "until_age": until_age,
        "monthly_contribution": monthly_contribution,
        "result": {k: v for k, v in result.items() if k != "yearly_data"},
    }
    filename = hashlib.md5(email.encode()).hexdigest() + ".json"
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return filename


def load_data_by_email(email):
    filename = hashlib.md5(email.encode()).hexdigest() + ".json"
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# ──────────────────────────────
# URLパラメータ判定
# ──────────────────────────────
params = st.query_params
email_param = params.get("email", None)
age_param = params.get("age", None)
until_param = params.get("until", None)
contribution_param = params.get("contribution", None)

if email_param and age_param and until_param and contribution_param:
    try:
        age_val = int(age_param)
        until_val = int(until_param)
        contribution_val = int(contribution_param)
        r = calc_simulation(age_val, until_val, contribution_val)
        if r is None:
            st.error("入力データにエラーがあります。年齢と積立終了年齢を確認してください。")
            st.stop()
    except (ValueError, TypeError):
        st.error("URLのパラメータが正しくありません。")
        st.stop()
elif email_param:
    data = load_data_by_email(email_param)
    if data is None:
        st.error("レポートが見つかりません。URLをご確認ください。")
        st.stop()
    r = data["result"]
    r["yearly_data"] = None
else:
    r = None


# ══════════════════════════════
# レポート表示
# ══════════════════════════════
if r:
    # ──── ゴールドヘッダー ────
    st.markdown(f"""
    <div class="gold-header">
        <h1>あなたの「手残り」シミュレーション結果</h1>
        <p>企業型確定拠出年金（選択制DC）を導入した場合の試算レポート</p>
    </div>
    """, unsafe_allow_html=True)

    # ──── シミュレーション条件 ────
    st.markdown("""<div class="section-card"><h2>📋 シミュレーション条件</h2>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="label">現在の年齢</div><div class="value-white">{r["age"]}歳</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="label">積立終了年齢</div><div class="value-white">{r["until_age"]}歳</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="label">積立期間</div><div class="value-white">{r["years"]}年間</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="label">毎月の掛金</div><div class="value">¥{r["monthly"]:,}</div></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ──── 掛金は全額経費 ────
    st.markdown("""<div class="section-card"><h2>💼 掛金は全額「会社の経費」になります</h2>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="label">年間の掛金</div><div class="value">¥{r["annual"]:,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card-highlight"><div class="label">{r["years"]}年間の掛金合計（元本）</div><div class="value">¥{r["total_principal"]:,}</div></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="point-box">
        <strong>ポイント：</strong>毎月 <strong>¥{r['monthly']:,}</strong> の掛金は、社長個人のお金ではなく
        <strong>会社の経費</strong>として処理されます。<br>
        つまり、<strong>社長の老後資金を会社のお金で積み立てている</strong>ことになります。
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ──── 将来資産（利回り別）────
    st.markdown("""<div class="section-card"><h2>📈 将来の資産残高（運用利回り別）</h2>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="rate-card rate-3">
            <div class="rate-label">利回り 3%（堅実運用）</div>
            <div class="rate-value">¥{r['fv_3']:,.0f}</div>
            <div class="rate-sub">運用益 ¥{r['gain_3']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="rate-card rate-5">
            <div class="rate-label">★ 利回り 5%（標準運用）</div>
            <div class="rate-value">¥{r['fv_5']:,.0f}</div>
            <div class="rate-sub">運用益 ¥{r['gain_5']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="rate-card rate-8">
            <div class="rate-label">利回り 8%（積極運用）</div>
            <div class="rate-value">¥{r['fv_8']:,.0f}</div>
            <div class="rate-sub">運用益 ¥{r['gain_8']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="point-box">
        元本 <strong>¥{r['total_principal']:,}</strong> に対して、利回り5%なら <strong>¥{r['fv_5']:,.0f}</strong> に。<br>
        運用益 <strong>¥{r['gain_5']:,.0f}</strong> には税金がかかりません（<strong>運用益非課税</strong>）。
    </div>
    """, unsafe_allow_html=True)

    # グラフ
    if r.get("yearly_data"):
        import pandas as pd
        df_chart = pd.DataFrame(r["yearly_data"])
        df_chart = df_chart.set_index("年目")
        st.line_chart(df_chart, color=["#556080", "#4ecdc4", "#daa520", "#a88beb"])

    st.markdown("</div>", unsafe_allow_html=True)

    # ──── 法人税の節税効果 ────
    st.markdown("""<div class="section-card"><h2>🏢 法人税の節税効果</h2>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="label">年間の節税額（概算）</div><div class="value">¥{r["annual_tax_saving"]:,.0f}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card-highlight"><div class="label">{r["years"]}年間の節税合計</div><div class="value">¥{r["total_tax_saving"]:,.0f}</div></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="point-box">
        掛金は<strong>全額損金算入</strong>されるため、法人税が下がります。<br>
        法人税率を約{int(r['tax_rate']*100)}%として計算すると、年間 <strong>¥{r['annual']:,}</strong> の掛金に対して
        <strong>年間 ¥{r['annual_tax_saving']:,.0f} の節税</strong>に。<br>
        {r['years']}年間で合計 <strong>¥{r['total_tax_saving']:,.0f}</strong> の節税効果です。
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ──── まとめ ────
    st.markdown("""<div class="section-card"><h2>✅ まとめ：この制度で得られるもの</h2>""", unsafe_allow_html=True)

    total_merit = r['fv_5'] + r['total_tax_saving']

    st.markdown(f"""
    <table class="summary-table">
        <tr><th>項目</th><th style="text-align:right;">金額</th></tr>
        <tr><td>毎月の掛金</td><td style="text-align:right;">¥{r['monthly']:,}（全額会社の経費）</td></tr>
        <tr><td>{r['years']}年間の元本合計</td><td style="text-align:right;">¥{r['total_principal']:,}</td></tr>
        <tr><td>将来の資産残高（利回り5%）</td><td style="text-align:right; color:#daa520; font-weight:700;">¥{r['fv_5']:,.0f}</td></tr>
        <tr><td>うち運用益（非課税）</td><td style="text-align:right;">¥{r['gain_5']:,.0f}</td></tr>
        <tr><td>法人税の節税合計</td><td style="text-align:right; color:#daa520; font-weight:700;">¥{r['total_tax_saving']:,.0f}</td></tr>
        <tr class="total-row"><td>実質的な総メリット</td><td style="text-align:right;">¥{total_merit:,.0f}</td></tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ──── CTA：セミナー案内 ────
    st.markdown(f"""
    <div class="cta-box">
        <h2>「手残り設計」勉強会のご案内</h2>
        <p>
            このシミュレーションは概算です。<br>
            実際の導入にあたっては、社長の報酬額・会社の利益状況に応じた詳細な設計が必要です。
        </p>
        <p>
            ✔ 社長の報酬の「手残り」を年間60万円以上増やす方法<br>
            ✔ 退職金ゼロの会社でも使える仕組みの全体像<br>
            ✔ 導入企業の具体的な事例
        </p>
        <p style="font-size:20px; font-weight:900; margin-top:15px;">参加費：無料（通常8,000円）</p>
    </div>
    """, unsafe_allow_html=True)

    # ──── フッター ────
    st.markdown("""
    <div class="footer-note">
        ※ このシミュレーションは概算であり、実際の金額を保証するものではありません。
        運用利回りは想定であり、実際の運用成果は市場環境により変動します。
        法人税率は約30%として概算しています。実際の税率は会社の利益額により異なります。
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════
# 入力フォーム（テスト用 / LP代わり）
# ══════════════════════════════
if not r:
    st.markdown("""
    <div class="gold-header">
        <h1>社長の「手残り」無料シミュレーション</h1>
        <p>会社の経費で社長の老後資金をいくら積み立てられるか、すぐにわかります</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("simulation_form"):
        email = st.text_input("メールアドレス *", placeholder="example@company.co.jp")
        age = st.number_input("現在の年齢 *", min_value=20, max_value=70, value=45)
        until_age = st.number_input("何歳まで積み立てるか *", min_value=30, max_value=75, value=65)

        st.markdown("**毎月の掛金（会社の経費として拠出）**")
        contribution = st.select_slider(
            "掛金を選択",
            options=[i * 1000 for i in range(3, 63)],
            value=55000,
            format_func=lambda x: f"¥{x:,}",
        )

        submitted = st.form_submit_button("シミュレーション結果を見る", type="primary", use_container_width=True)

    if submitted:
        if not email:
            st.error("メールアドレスを入力してください")
        elif age >= until_age:
            st.error("積立終了年齢は現在の年齢より大きくしてください")
        else:
            result = calc_simulation(age, until_age, contribution)
            if result:
                save_data(email, age, until_age, contribution, result)
                report_url_full = f"?email={email}&age={age}&until={until_age}&contribution={contribution}"
                st.success("シミュレーション完了！")
                st.markdown(f"**[あなたのレポートを見る]({report_url_full})**")
