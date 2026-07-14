import streamlit as st
import json
import hashlib
from pathlib import Path

st.set_page_config(page_title="手残りシミュレーション", page_icon="💰", layout="wide")

# ──────────────────────────────
# デザインCSS（信頼性重視：白背景×ネイビー×ゴールド）
# ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');

:root{
    --ink:#111d33;
    --navy:#1a2744;
    --navy2:#243559;
    --gold:#c8a951;
    --gold-bright:#e0c574;
    --gold-deep:#a8842f;
    --paper:#eef0f4;
    --card:#ffffff;
    --line:#e3e6ec;
    --muted:#7c8797;
    --text:#2c3e50;
    --teal:#2a8a7a;
    --violet:#6a4fa0;
}

/* 全体 */
.stApp{
    background:var(--paper);
    color:var(--text);
    font-family:'Noto Sans JP',sans-serif;
}
header[data-testid="stHeader"]{display:none;}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}

.block-container{
    max-width:820px;
    padding:1.4rem 1.1rem 3rem;
}

/* 数字は等幅で桁を揃える */
.num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum" 1;letter-spacing:-.5px;}

/* ───────── コンパクトヘッダー ───────── */
.top-band{
    display:flex;align-items:center;gap:12px;
    padding:14px 20px;margin-bottom:22px;
    background:var(--navy);border-radius:12px;
    border-bottom:3px solid var(--gold);
}
.top-band .tb-mark{
    font-size:22px;line-height:1;
}
.top-band .tb-txt{color:#fff;}
.top-band .tb-txt b{display:block;font-size:15px;font-weight:900;letter-spacing:.3px;}
.top-band .tb-txt span{font-size:11.5px;opacity:.75;}

/* ───────── ヒーロー（診断結果の主役） ───────── */
.hero{
    position:relative;overflow:hidden;
    background:radial-gradient(120% 140% at 50% -20%, #26365c 0%, var(--navy) 45%, var(--ink) 100%);
    border-radius:18px;
    padding:34px 26px 30px;
    text-align:center;
    border:1px solid rgba(200,169,81,.35);
    box-shadow:0 12px 34px rgba(17,29,51,.28);
    margin-bottom:14px;
}
.hero::after{
    content:"";position:absolute;inset:0;pointer-events:none;
    background:radial-gradient(60% 50% at 50% 120%, rgba(200,169,81,.18), transparent 70%);
}
.hero-eyebrow{
    display:inline-block;
    color:var(--gold-bright);
    font-size:12px;font-weight:700;letter-spacing:2px;
    border:1px solid rgba(200,169,81,.5);
    border-radius:999px;padding:5px 16px;margin-bottom:14px;
}
.hero-lead{color:#cdd6e6;font-size:14px;margin:0 0 4px;font-weight:500;}
.hero-number{
    color:#fff;
    font-weight:900;
    font-size:clamp(2.5rem,11vw,4.6rem);
    line-height:1.02;
    margin:2px 0 4px;
    background:linear-gradient(180deg,#ffffff 30%,var(--gold-bright) 130%);
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
    animation:rise .8s cubic-bezier(.2,.75,.2,1) both;
}
.hero-unit{color:#aeb9cc;font-size:13px;margin-bottom:20px;font-weight:500;}
.hero-stats{
    display:flex;align-items:stretch;justify-content:center;gap:0;
    background:rgba(255,255,255,.05);
    border:1px solid rgba(255,255,255,.09);
    border-radius:12px;overflow:hidden;
    animation:rise .8s .12s cubic-bezier(.2,.75,.2,1) both;
}
.hero-stats .hs{flex:1;padding:14px 8px;text-align:center;}
.hero-stats .hs-l{color:#9fabbf;font-size:11px;margin-bottom:5px;font-weight:500;}
.hero-stats .hs-v{color:#fff;font-size:clamp(15px,4.4vw,20px);font-weight:900;}
.hero-stats .hs-v.gold{color:var(--gold-bright);}
.hero-stats .hs-div{width:1px;background:rgba(255,255,255,.12);}

/* ───────── 汎用カード ───────── */
.card{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px;
    padding:26px 24px;
    margin:16px 0;
    box-shadow:0 2px 10px rgba(17,29,51,.05);
}
.card-eyebrow{
    color:var(--gold-deep);font-size:11px;font-weight:700;
    letter-spacing:2px;margin-bottom:6px;
}
.card h2{
    color:var(--navy);font-size:20px;font-weight:900;
    margin:0 0 18px;line-height:1.4;
}
.card h2 em{color:var(--gold-deep);font-style:normal;}

/* ───────── 成長グラフ ───────── */
.chart-wrap{width:100%;}
.chart-wrap svg{width:100%;height:auto;display:block;}
.chart-legend{
    display:flex;flex-wrap:wrap;gap:16px;justify-content:center;
    margin-top:14px;font-size:12.5px;color:var(--text);
}
.chart-legend span{display:inline-flex;align-items:center;gap:7px;}
.chart-legend i{width:14px;height:14px;border-radius:4px;display:inline-block;}
.chart-legend i.navy{background:var(--navy);}
.chart-legend i.gold{background:linear-gradient(135deg,var(--gold-bright),var(--gold-deep));}

/* ───────── 利回り別カード（横並び） ───────── */
.rate-grid{display:flex;gap:12px;}
.rate-grid .rate-card{
    flex:1;border-radius:14px;padding:18px 12px;text-align:center;position:relative;
}
.rate-card .rate-label{font-size:12px;font-weight:700;margin-bottom:8px;}
.rate-card .rate-value{font-size:clamp(20px,5.2vw,27px);font-weight:900;line-height:1.1;}
.rate-card .rate-sub{font-size:11px;opacity:.8;margin-top:6px;}
.rate-card .rate-badge{
    position:absolute;top:-10px;left:50%;transform:translateX(-50%);
    background:var(--gold);color:#3a2c00;font-size:10px;font-weight:900;
    padding:3px 12px;border-radius:999px;white-space:nowrap;letter-spacing:.5px;
    box-shadow:0 3px 8px rgba(168,132,47,.4);
}
.rate-3{background:#f0faf8;border:1px solid #b8e0d8;}
.rate-3 .rate-label,.rate-3 .rate-value{color:#238274;}
.rate-5{background:linear-gradient(180deg,#fffdf4,#fff8e6);border:2px solid var(--gold);box-shadow:0 8px 22px rgba(168,132,47,.18);transform:translateY(-4px);}
.rate-5 .rate-label,.rate-5 .rate-value{color:var(--gold-deep);}
.rate-8{background:#f6f2fb;border:1px solid #cabbe6;}
.rate-8 .rate-label,.rate-8 .rate-value{color:#63499b;}

/* ───────── 節税効果 ───────── */
.tax-panel{
    background:radial-gradient(120% 120% at 50% 0%, var(--navy2), var(--navy) 60%, var(--ink));
    border-radius:16px;padding:28px 24px;text-align:center;
    border:1px solid rgba(200,169,81,.3);
    box-shadow:0 8px 24px rgba(17,29,51,.2);
}
.tax-panel .tx-lead{color:#cdd6e6;font-size:15px;line-height:1.85;margin:0 0 6px;}
.tax-panel .tx-inline{color:var(--gold-bright);font-weight:900;font-size:19px;}
.tax-panel .tx-big{
    color:#fff;font-size:clamp(2rem,9vw,3.2rem);font-weight:900;margin:10px 0 2px;
    background:linear-gradient(180deg,#fff,var(--gold-bright));
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
}
.tax-panel .tx-per{color:#9fabbf;font-size:12px;margin-bottom:16px;}
.tax-panel .tx-total{
    display:inline-block;background:rgba(200,169,81,.12);
    border:1px solid rgba(200,169,81,.4);border-radius:10px;
    padding:12px 20px;color:#fff;font-size:15px;font-weight:700;
}
.tax-panel .tx-total b{color:var(--gold-bright);font-size:22px;font-weight:900;margin:0 4px;}

/* ───────── セミナー案内（CTAブリッジ） ───────── */
.cta-bridge{
    position:relative;margin-top:30px;
    background:linear-gradient(135deg,var(--gold-bright) 0%, var(--gold) 45%, var(--gold-deep) 100%);
    border-radius:18px;padding:32px 26px 30px;text-align:center;
    box-shadow:0 14px 34px rgba(168,132,47,.32);
}
.cta-bridge .cb-eyebrow{
    display:inline-block;color:#4a3708;font-size:11px;font-weight:900;letter-spacing:2.5px;
    background:rgba(255,255,255,.35);border-radius:999px;padding:5px 16px;margin-bottom:14px;
}
.cta-bridge h2{color:#231903;font-size:clamp(19px,4.8vw,25px);font-weight:900;margin:0 0 12px;line-height:1.55;}
.cta-bridge p{color:#3c2d07;font-size:14px;line-height:1.9;margin:0 auto;max-width:32em;}
.cta-bridge .cb-points{
    display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:18px 0 4px;
}
.cta-bridge .cb-points span{
    background:rgba(35,25,3,.9);color:var(--gold-bright);font-size:12.5px;font-weight:700;
    padding:7px 14px;border-radius:999px;
}
.cta-bridge .cb-chev{
    display:block;margin:20px auto 0;width:20px;height:20px;
    border-right:3px solid #231903;border-bottom:3px solid #231903;
    transform:rotate(45deg);animation:bob 1.5s ease-in-out infinite;
}
@keyframes bob{0%,100%{transform:rotate(45deg) translate(0,0)}50%{transform:rotate(45deg) translate(3px,3px)}}

/* ───────── 条件ストリップ（脇役） ───────── */
.cond-strip{
    display:flex;gap:10px;flex-wrap:wrap;
    background:var(--card);border:1px solid var(--line);
    border-radius:14px;padding:16px 14px;margin:16px 0;
    box-shadow:0 2px 10px rgba(17,29,51,.05);
}
.cond-strip .cs-title{
    width:100%;color:var(--muted);font-size:11px;font-weight:700;
    letter-spacing:1.5px;margin-bottom:4px;
}
.cond-strip .cs-item{
    flex:1;min-width:90px;text-align:center;padding:6px 4px;
}
.cond-strip .cs-l{color:var(--muted);font-size:11px;margin-bottom:3px;}
.cond-strip .cs-v{color:var(--navy);font-size:19px;font-weight:900;}

.footer-note{
    color:#98a3b2;font-size:11px;line-height:1.7;
    margin-top:26px;padding-top:18px;border-top:1px solid var(--line);
}

/* Streamlitフォーム */
div[data-testid="stForm"]{
    background:var(--card);border:1px solid var(--line);
    border-radius:16px;padding:24px;box-shadow:0 2px 10px rgba(17,29,51,.05);
}
.stMetric label{color:var(--muted)!important;}

@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

@media (max-width:640px){
    .rate-grid{flex-direction:column;}
    .rate-5{transform:none;}
    .hero-stats .hs-v{font-size:15px;}
}
@media (prefers-reduced-motion:reduce){
    *{animation:none!important;}
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
# 表示ヘルパー
# ──────────────────────────────
def yen(v):
    return f"¥{v:,.0f}"


def manyen(v):
    return f"{v/10000:,.0f}万円"


def build_growth_chart_svg(r):
    """元本（ネイビー）の上に運用益（ゴールド）が積み上がって伸びる面グラフ。"""
    yearly = r.get("yearly_data")
    if not yearly:
        return ""

    W, H = 720, 340
    pad_l, pad_r, pad_t, pad_b = 18, 18, 30, 48
    plot_w = W - pad_l - pad_r
    plot_h = H - pad_t - pad_b
    base_y = pad_t + plot_h
    total_years = r["years"]
    max_y = r["fv_5"] if r["fv_5"] > 0 else 1

    xs = [0] + [d["年目"] for d in yearly]
    prin = [0] + [d["元本"] for d in yearly]
    fv5 = [0] + [d["利回り5%"] for d in yearly]

    def X(year):
        return pad_l + plot_w * (year / total_years)

    def Y(val):
        return pad_t + plot_h * (1 - val / max_y)

    prin_pts = [(X(xs[i]), Y(prin[i])) for i in range(len(xs))]
    fv5_pts = [(X(xs[i]), Y(fv5[i])) for i in range(len(xs))]

    def poly(pts):
        return " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))

    prin_area = poly(prin_pts) + f" L {prin_pts[-1][0]:.1f} {base_y:.1f} L {prin_pts[0][0]:.1f} {base_y:.1f} Z"
    gain_area = poly(fv5_pts) + " " + " ".join(f"L {x:.1f} {y:.1f}" for x, y in reversed(prin_pts)) + " Z"
    fv5_line = poly(fv5_pts)
    prin_line = poly(prin_pts)

    # 目盛り（年齢）
    mid_year = total_years // 2
    ticks = [(0, f"{r['age']}歳"), (mid_year, f"{r['age']+mid_year}歳"), (total_years, f"{r['until_age']}歳")]
    tick_svg = ""
    for yr, lbl in ticks:
        tx = X(yr)
        anchor = "start" if yr == 0 else ("end" if yr == total_years else "middle")
        tick_svg += f'<text x="{tx:.1f}" y="{base_y+22:.1f}" fill="#8a94a4" font-size="12" text-anchor="{anchor}">{lbl}</text>'

    # 補助線
    grid = ""
    for f in (1/3, 2/3):
        gy = pad_t + plot_h * f
        grid += f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{W-pad_r}" y2="{gy:.1f}" stroke="#eef0f4" stroke-width="1"/>'

    # 終点ラベル
    ex = fv5_pts[-1][0]
    ey_fv = fv5_pts[-1][1]
    ey_pr = prin_pts[-1][1]

    # 運用益ラベル位置（グラフ内 65% 付近の帯の中央）
    idx = max(1, int(len(xs) * 0.62))
    gx = (prin_pts[idx][0] + fv5_pts[idx][0]) / 2
    gy_mid = (prin_pts[idx][1] + fv5_pts[idx][1]) / 2

    gain_val = r["fv_5"] - r["total_principal"]

    svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="資産成長グラフ">
  <defs>
    <linearGradient id="goldFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e6cd82"/>
      <stop offset="100%" stop-color="#c8a951"/>
    </linearGradient>
    <linearGradient id="navyFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2b3d63"/>
      <stop offset="100%" stop-color="#1a2744"/>
    </linearGradient>
  </defs>
  {grid}
  <line x1="{pad_l}" y1="{base_y}" x2="{W-pad_r}" y2="{base_y}" stroke="#d7dbe3" stroke-width="1.5"/>
  <path d="{gain_area}" fill="url(#goldFill)" opacity="0.92"/>
  <path d="{prin_area}" fill="url(#navyFill)"/>
  <path d="{prin_line}" fill="none" stroke="#0f1a30" stroke-width="2"/>
  <path d="{fv5_line}" fill="none" stroke="#a8842f" stroke-width="3" stroke-linejoin="round"/>
  {tick_svg}
  <text x="{gx:.1f}" y="{gy_mid+4:.1f}" fill="#5a4614" font-size="13" font-weight="700" text-anchor="middle">運用益 +{manyen(gain_val)}</text>
  <circle cx="{ex:.1f}" cy="{ey_fv:.1f}" r="5" fill="#a8842f" stroke="#fff" stroke-width="2"/>
  <circle cx="{ex:.1f}" cy="{ey_pr:.1f}" r="5" fill="#1a2744" stroke="#fff" stroke-width="2"/>
  <text x="{ex-10:.1f}" y="{ey_fv-10:.1f}" fill="#8a6a1e" font-size="14" font-weight="900" text-anchor="end">{manyen(r['fv_5'])}</text>
  <text x="{ex-10:.1f}" y="{ey_pr+18:.1f}" fill="#1a2744" font-size="12" font-weight="700" text-anchor="end">元本 {manyen(r['total_principal'])}</text>
</svg>'''
    return svg


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
    # 保存済みパラメータから再計算して yearly_data（グラフ用）も復元
    r = calc_simulation(data["age"], data["until_age"], data["monthly_contribution"])
    if r is None:
        st.error("レポートデータに問題があります。")
        st.stop()
else:
    r = None


# ══════════════════════════════
# レポート表示
# ══════════════════════════════
if r:
    multiple = r["fv_5"] / r["total_principal"] if r["total_principal"] else 0
    gain_5 = r["fv_5"] - r["total_principal"]

    # ── コンパクトヘッダー ──
    st.markdown("""
    <div class="top-band">
        <div class="tb-mark">💰</div>
        <div class="tb-txt">
            <b>あなたの「手残り」シミュレーション結果</b>
            <span>企業型確定拠出年金（選択制DC）を導入した場合の試算レポート</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ヒーロー（主役の数字） ──
    st.markdown(f"""
    <div class="hero">
        <div class="hero-eyebrow">利回り5％で運用した場合</div>
        <p class="hero-lead">{r['until_age']}歳までの積み立てで、社長個人の資産は</p>
        <div class="hero-number num">{yen(r['fv_5'])}</div>
        <div class="hero-unit">まで育つ可能性があります</div>
        <div class="hero-stats">
            <div class="hs">
                <div class="hs-l">投じた元本</div>
                <div class="hs-v num">{yen(r['total_principal'])}</div>
            </div>
            <div class="hs-div"></div>
            <div class="hs">
                <div class="hs-l">ふえた運用益</div>
                <div class="hs-v gold num">+{yen(gain_5)}</div>
            </div>
            <div class="hs-div"></div>
            <div class="hs">
                <div class="hs-l">資産倍率</div>
                <div class="hs-v gold num">約{multiple:.1f}倍</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 成長グラフ ──
    st.markdown(f"""
    <div class="card">
        <div class="card-eyebrow">ASSET GROWTH</div>
        <h2>積み立てた元本は、<em>運用益</em>でこれだけ大きく育ちます</h2>
        <div class="chart-wrap">{build_growth_chart_svg(r)}</div>
        <div class="chart-legend">
            <span><i class="navy"></i>元本（積み立てたお金）</span>
            <span><i class="gold"></i>運用益（ふえた分・利回り5％）</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 利回り別カード ──
    st.markdown(f"""
    <div class="card">
        <div class="card-eyebrow">SCENARIO</div>
        <h2>運用利回り別・将来の資産残高</h2>
        <div class="rate-grid">
            <div class="rate-card rate-3">
                <div class="rate-label">堅実 3％</div>
                <div class="rate-value num">{yen(r['fv_3'])}</div>
                <div class="rate-sub num">運用益 +{yen(r['gain_3'])}</div>
            </div>
            <div class="rate-card rate-5">
                <div class="rate-badge">標準シナリオ</div>
                <div class="rate-label">標準 5％</div>
                <div class="rate-value num">{yen(r['fv_5'])}</div>
                <div class="rate-sub num">運用益 +{yen(r['gain_5'])}</div>
            </div>
            <div class="rate-card rate-8">
                <div class="rate-label">積極 8％</div>
                <div class="rate-value num">{yen(r['fv_8'])}</div>
                <div class="rate-sub num">運用益 +{yen(r['gain_8'])}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 法人税の節税効果 ──
    st.markdown(f"""
    <div class="card" style="padding:0;border:none;box-shadow:none;background:transparent;">
        <div class="tax-panel">
            <p class="tx-lead">さらに、会社の経費で年間 <span class="tx-inline num">{yen(r['annual'])}</span> を拠出できるので<br>法人税の節税効果は</p>
            <div class="tx-big num">年間 {yen(r['annual_tax_saving'])}</div>
            <div class="tx-per">（法人税率30％で試算）</div>
            <div class="tx-total">{r['years']}年間の累計で <b class="num">{yen(r['total_tax_saving'])}</b> の節税</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 条件（脇役・下部） ──
    st.markdown(f"""
    <div class="cond-strip">
        <div class="cs-title">シミュレーション条件</div>
        <div class="cs-item"><div class="cs-l">現在の年齢</div><div class="cs-v num">{r['age']}歳</div></div>
        <div class="cs-item"><div class="cs-l">積立終了</div><div class="cs-v num">{r['until_age']}歳</div></div>
        <div class="cs-item"><div class="cs-l">積立期間</div><div class="cs-v num">{r['years']}年</div></div>
        <div class="cs-item"><div class="cs-l">毎月の掛金</div><div class="cs-v num">{yen(r['monthly'])}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── セミナー案内（CTAブリッジ）──
    st.markdown("""
    <div class="cta-bridge">
        <div class="cb-eyebrow">NEXT STEP</div>
        <h2>この「手残り」を実現する具体的な方法を、<br>無料セミナーで解説します</h2>
        <p>選択制DC（企業型確定拠出年金）の導入手順・掛金の決め方・注意点まで。この試算を"絵に描いた餅"で終わらせないための実務を、まるごとお伝えします。</p>
        <div class="cb-points">
            <span>導入コスト</span>
            <span>手続きの流れ</span>
            <span>失敗しない設計</span>
        </div>
        <span class="cb-chev"></span>
    </div>
    """, unsafe_allow_html=True)

    # ── セミナーLP埋め込み ──
    st.markdown("""
    <div style="margin-top:20px;">
        <iframe src="https://contents.semeru-shigyo.com/401k-seminar/"
                style="width:100%; border:none; min-height:8000px;"
                scrolling="no"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation"></iframe>
    </div>
    """, unsafe_allow_html=True)

    # ── フッター ──
    st.markdown("""
    <div class="footer-note">
        ※ このシミュレーションは概算であり、実際の金額を保証するものではありません。
        運用利回りは想定であり、実際の運用成果は市場環境により変動します。
        法人税率は約30％として概算しています。実際の税率は会社の利益額により異なります。
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════
# 入力フォーム（テスト用 / LP代わり）
# ══════════════════════════════
if not r:
    st.markdown("""
    <div class="hero" style="margin-bottom:24px;">
        <div class="hero-eyebrow">無料・60秒でわかる</div>
        <p class="hero-lead" style="font-size:16px;">社長の「手残り」シミュレーション</p>
        <div class="hero-unit" style="margin-top:8px;">会社の経費で、社長の老後資金をいくら積み立てられるか試算します</div>
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
