import streamlit as st
import json
import hashlib
from pathlib import Path

st.set_page_config(page_title="手残りシミュレーション", page_icon="💰", layout="wide")

# ──────────────────────────────
# デザインCSS（信頼性重視：白背景×ネイビー×控えめゴールド）
# ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');

/* 全体 */
.stApp {
    background-color: #f5f6f8;
    color: #2c3e50;
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

/* ヘッダー */
.gold-header {
    background: #1a2744;
    color: #ffffff;
    padding: 40px 30px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 30px;
    border-bottom: 4px solid #b8960b;
}
.gold-header h1 {
    font-size: 26px;
    font-weight: 900;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}
.gold-header p {
    font-size: 14px;
    opacity: 0.8;
    margin: 0;
}

/* セクションカード */
.section-card {
    background: #ffffff;
    border: 1px solid #e0e3e8;
    border-radius: 8px;
    padding: 28px;
    margin: 20px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.section-card h2 {
    color: #1a2744;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e8eaef;
}

/* メトリクスカード */
.metric-card {
    background: #f8f9fb;
    border: 1px solid #e0e3e8;
    border-radius: 8px;
    padding: 18px;
    text-align: center;
    margin: 8px 0;
}
.metric-card .label {
    color: #6b7b8d;
    font-size: 12px;
    margin-bottom: 4px;
}
.metric-card .value {
    color: #1a2744;
    font-size: 26px;
    font-weight: 900;
}
.metric-card .value-white {
    color: #1a2744;
    font-size: 26px;
    font-weight: 900;
}
.metric-card-highlight {
    background: #ffffff;
    border: 2px solid #1a2744;
    border-radius: 8px;
    padding: 18px;
    text-align: center;
    margin: 8px 0;
}
.metric-card-highlight .label {
    color: #6b7b8d;
    font-size: 12px;
    margin-bottom: 4px;
}
.metric-card-highlight .value {
    color: #b8960b;
    font-size: 26px;
    font-weight: 900;
}

/* ポイント吹き出し */
.point-box {
    background: #f0f4f8;
    border-left: 4px solid #1a2744;
    border-radius: 0 6px 6px 0;
    padding: 16px 20px;
    margin: 16px 0;
    color: #3a4a5c;
    font-size: 14px;
    line-height: 1.8;
}
.point-box strong { color: #1a2744; }

/* 利回りカード */
.rate-card {
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    margin: 8px 0;
}
.rate-card .rate-label {
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 6px;
}
.rate-card .rate-value {
    font-size: 42px;
    font-weight: 900;
    margin-bottom: 4px;
    letter-spacing: -1px;
}
.rate-card .rate-sub {
    font-size: 13px;
    opacity: 0.7;
    margin-top: 4px;
}
.rate-3 {
    background: #f0faf8;
    border: 1px solid #b8e0d8;
}
.rate-3 .rate-label { color: #2a8a7a; }
.rate-3 .rate-value { color: #2a8a7a; }

.rate-5 {
    background: #fffdf5;
    border: 2px solid #b8960b;
}
.rate-5 .rate-label { color: #8a7008; }
.rate-5 .rate-value { color: #8a7008; }

.rate-8 {
    background: #f5f0fa;
    border: 1px solid #c8b8e0;
}
.rate-8 .rate-label { color: #6a4fa0; }
.rate-8 .rate-value { color: #6a4fa0; }

/* まとめテーブル */
.summary-table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
}
.summary-table th {
    background: #f0f2f5;
    color: #6b7b8d;
    padding: 12px 16px;
    text-align: left;
    font-weight: 700;
    font-size: 13px;
    border-bottom: 2px solid #e0e3e8;
}
.summary-table td {
    padding: 14px 16px;
    border-bottom: 1px solid #eceef2;
    font-size: 15px;
    color: #2c3e50;
}
.summary-table .total-row td {
    border-top: 2px solid #1a2744;
    color: #b8960b;
    font-weight: 900;
    font-size: 18px;
    padding-top: 16px;
}

/* CTA */
.cta-box {
    background: #1a2744;
    color: #ffffff;
    padding: 35px 30px;
    border-radius: 8px;
    text-align: center;
    margin: 30px 0;
    border-bottom: 4px solid #b8960b;
}
.cta-box h2 {
    font-size: 20px;
    font-weight: 900;
    margin-bottom: 12px;
    color: #ffffff;
}
.cta-box p {
    font-size: 14px;
    color: #c0c8d8;
    line-height: 1.8;
    margin-bottom: 8px;
}

/* フッター */
.footer-note {
    color: #8899aa;
    font-size: 11px;
    line-height: 1.6;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e0e3e8;
}

/* Streamlitデフォルトの上書き */
.stMetric label { color: #6b7b8d !important; }
.stMetric [data-testid="stMetricValue"] { color: #1a2744 !important; }
div[data-testid="stForm"] {
    background: #ffffff;
    border: 1px solid #e0e3e8;
    border-radius: 8px;
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

    # ──── 将来資産（利回り別）── 一番上 ────
    st.markdown(f"""<div class="section-card"><h2 style="font-size:22px; margin-bottom:20px;">📈 将来の資産残高（運用利回り別）</h2><div style="background:#1a2744; border-radius:8px; padding:24px; margin-bottom:24px; text-align:center;"><p style="color:#c0a346; font-size:20px; font-weight:900; line-height:1.7; margin:0;">元本 ¥{r['total_principal']:,}（{r['until_age']}歳まで毎月¥{r['monthly']:,}を積み立て）で、<br>これだけの個人資産を作れる可能性が高いです！</p></div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="rate-card rate-8">
        <div class="rate-label">利回り 8%（積極運用）</div>
        <div class="rate-value">¥{r['fv_8']:,.0f}</div>
        <div class="rate-sub">運用益 ¥{r['gain_8']:,.0f}</div>
    </div>
    <div class="rate-card rate-5">
        <div class="rate-label">★ 利回り 5%（標準運用）</div>
        <div class="rate-value">¥{r['fv_5']:,.0f}</div>
        <div class="rate-sub">運用益 ¥{r['gain_5']:,.0f}</div>
    </div>
    <div class="rate-card rate-3">
        <div class="rate-label">利回り 3%（堅実運用）</div>
        <div class="rate-value">¥{r['fv_3']:,.0f}</div>
        <div class="rate-sub">運用益 ¥{r['gain_3']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

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

    # ──── 法人税の節税効果（目立つ版）────
    st.markdown(f"""<div class="section-card"><h2 style="font-size:22px;">🏢 法人税の節税効果</h2><div style="background:#1a2744; border-radius:8px; padding:24px; text-align:center;"><p style="color:#ffffff; font-size:17px; line-height:1.8; margin-bottom:12px;">会社の経費で年間 <span style="color:#c0a346; font-size:22px; font-weight:900;">¥{r['annual']:,}</span> を処理できるので</p><p style="color:#ffffff; font-size:17px; line-height:1.8; margin-bottom:8px;">法人税の節税効果として</p><p style="color:#c0a346; font-size:36px; font-weight:900; margin-bottom:8px;">年間 ¥{r['annual_tax_saving']:,.0f}</p><p style="color:#ffffff; font-size:18px; font-weight:700; margin:0;">{r['years']}年間で合計 <span style="color:#c0a346; font-size:28px; font-weight:900;">¥{r['total_tax_saving']:,.0f}</span> の節税</p></div></div>""", unsafe_allow_html=True)

    # ──── CTA：セミナー案内 ────
    seminar_lp_url = "https://contents.semeru-shigyo.com/401k-seminar/"
    st.markdown(f"""<a href="{seminar_lp_url}" target="_blank" style="text-decoration:none; color:inherit;"><div class="cta-box" style="cursor:pointer;"><p style="font-size:16px; color:#ffffff; margin-bottom:16px; line-height:1.8;">会社の経費で個人資産を作れて、社会保険料も安くなる<br>国の制度の使い方について詳しく学びませんか？</p><h2>社長の最終手残り設計セミナーのご案内</h2><p style="font-size:15px; color:#c0c8d8; margin-bottom:12px;">〜会社の経費で老後資金を作りながら、法人税も下げる方法〜</p><p style="font-size:20px; font-weight:900; margin-top:15px; color:#fbbf24;">▶ セミナー詳細を見る</p></div></a>""", unsafe_allow_html=True)

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
