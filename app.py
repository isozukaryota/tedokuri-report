import streamlit as st
import json
import hashlib
from pathlib import Path

st.set_page_config(page_title="手残りシミュレーション結果", page_icon="💰", layout="wide")

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

    # 将来資産残高（毎月積立の複利計算）
    def future_value(rate, months):
        if rate == 0:
            return monthly * months
        r = rate / 12
        return monthly * (((1 + r) ** months - 1) / r)

    months = years * 12
    fv_3 = future_value(0.03, months)
    fv_5 = future_value(0.05, months)
    fv_8 = future_value(0.08, months)

    # 法人税節税効果（概算：法人税率を約30%として）
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
    }


def save_data(email, age, until_age, monthly_contribution, result):
    record = {
        "email": email,
        "age": age,
        "until_age": until_age,
        "monthly_contribution": monthly_contribution,
        "result": result,
    }
    # メアドをファイル名に使う（ハッシュ化）
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
# URLパラメータでレポート表示 or 入力フォーム
# ──────────────────────────────
# 2つのモードで動作する：
#
# モード1：URLパラメータにage/until/contributionが全部ある
#   → データベース不要。URLだけで計算・表示（UTAGE連携用）
#   例：?email=xxx&age=45&until=65&contribution=55000
#
# モード2：URLパラメータにemailだけある
#   → ローカルデータベースから読む（フォーム入力後の即時表示用）
#
# モード3：URLパラメータなし
#   → 入力フォームを表示（テスト用 / LP代わり）

params = st.query_params
email_param = params.get("email", None)
age_param = params.get("age", None)
until_param = params.get("until", None)
contribution_param = params.get("contribution", None)

# モード1：URLパラメータで全データが来ている（UTAGE連携）
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

# モード2：emailだけある（フォーム入力後の即時表示）
elif email_param:
    data = load_data_by_email(email_param)
    if data is None:
        st.error("レポートが見つかりません。URLをご確認ください。")
        st.stop()
    r = data["result"]

else:
    r = None

if r:

    # ──── ヘッダー ────
    st.markdown("---")
    st.markdown("## 💰 あなたの「手残り」シミュレーション結果")
    st.markdown("##### 企業型確定拠出年金（選択制DC）を導入した場合の試算です")
    st.markdown("---")

    # ──── 入力条件 ────
    st.markdown("### 📋 シミュレーション条件")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("現在の年齢", f"{r['age']}歳")
    c2.metric("積立終了年齢", f"{r['until_age']}歳")
    c3.metric("積立期間", f"{r['years']}年間")
    c4.metric("毎月の掛金", f"¥{r['monthly']:,}")

    st.markdown("---")

    # ──── 元本と経費 ────
    st.markdown("### 💼 掛金は全額「会社の経費」になります")

    c1, c2, c3 = st.columns(3)
    c1.metric("年間の掛金", f"¥{r['annual']:,}")
    c2.metric(f"{r['years']}年間の掛金合計（元本）", f"¥{r['total_principal']:,}")
    c3.metric("掛金の会社負担", "全額経費（損金算入）")

    st.info(f"""
    **ポイント：** 毎月 ¥{r['monthly']:,} の掛金は、社長個人のお金ではなく **会社の経費** として処理されます。
    つまり、**社長の老後資金を会社のお金で積み立てている** ことになります。
    """)

    st.markdown("---")

    # ──── 将来資産 ────
    st.markdown("### 📈 将来の資産残高（運用利回り別）")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### 🟢 利回り 3%")
        st.metric("資産残高", f"¥{r['fv_3']:,.0f}")
        st.caption(f"運用益: ¥{r['gain_3']:,.0f}")

    with c2:
        st.markdown("#### 🔵 利回り 5%")
        st.metric("資産残高", f"¥{r['fv_5']:,.0f}")
        st.caption(f"運用益: ¥{r['gain_5']:,.0f}")

    with c3:
        st.markdown("#### 🟣 利回り 8%")
        st.metric("資産残高", f"¥{r['fv_8']:,.0f}")
        st.caption(f"運用益: ¥{r['gain_8']:,.0f}")

    st.success(f"""
    **元本 ¥{r['total_principal']:,} に対して、利回り5%なら ¥{r['fv_5']:,.0f} になります。**
    運用益 ¥{r['gain_5']:,.0f} には税金がかかりません（運用益非課税）。
    """)

    st.markdown("---")

    # ──── 法人税の節税効果 ────
    st.markdown("### 🏢 法人税の節税効果")

    c1, c2 = st.columns(2)
    c1.metric("年間の節税額（概算）", f"¥{r['annual_tax_saving']:,.0f}")
    c2.metric(f"{r['years']}年間の節税合計", f"¥{r['total_tax_saving']:,.0f}")

    st.info(f"""
    **掛金は全額損金算入されるため、法人税が下がります。**
    法人税率を約{int(r['tax_rate']*100)}%として計算すると、
    年間 ¥{r['annual']:,} の掛金に対して **年間 ¥{r['annual_tax_saving']:,.0f} の節税** になります。
    {r['years']}年間で合計 **¥{r['total_tax_saving']:,.0f}** の節税効果です。
    """)

    st.markdown("---")

    # ──── まとめ ────
    st.markdown("### ✅ まとめ：この制度で得られるもの")

    st.markdown(f"""
    | 項目 | 金額 |
    |------|------|
    | 毎月の掛金 | ¥{r['monthly']:,}（全額会社の経費） |
    | {r['years']}年間の元本合計 | ¥{r['total_principal']:,} |
    | 将来の資産残高（利回り5%） | **¥{r['fv_5']:,.0f}** |
    | うち運用益（非課税） | ¥{r['gain_5']:,.0f} |
    | 法人税の節税合計 | **¥{r['total_tax_saving']:,.0f}** |
    | **実質的な総メリット** | **¥{r['fv_5'] + r['total_tax_saving']:,.0f}** |
    """)

    st.markdown("---")

    # ──── セミナー案内 ────
    st.markdown("### 🎓 さらに詳しく知りたい方へ")

    st.warning("""
    **「手残り設計」勉強会のご案内**

    このシミュレーションは概算です。実際の導入にあたっては、
    社長の報酬額・会社の利益状況に応じた詳細な設計が必要です。

    勉強会では、以下の内容をお伝えします：
    - 社長の報酬の「手残り」を年間60万円以上増やす方法
    - 退職金ゼロの会社でも使える仕組みの全体像
    - 導入企業の具体的な事例

    **参加費：無料（通常8,000円）**
    """)

    st.markdown("""
    **お問い合わせ・勉強会のお申し込み：**
    社労士事務所〇〇　セミナー事務局
    TEL：〇〇-〇〇〇〇-〇〇〇〇
    """)

    st.markdown("---")
    st.caption("※ このシミュレーションは概算であり、実際の金額を保証するものではありません。"
               "運用利回りは想定であり、実際の運用成果は市場環境により変動します。"
               "法人税率は約30%として概算しています。実際の税率は会社の利益額により異なります。")

if not r:
    # ========== 入力フォームモード（LP用 or テスト用）==========
    st.title("💰 社長の「手残り」無料シミュレーション")
    st.markdown("##### 会社の経費で社長の老後資金をいくら積み立てられるか、すぐにわかります")
    st.markdown("---")

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
                # 2種類のURLを表示
                report_url_simple = f"?email={email}"
                report_url_full = f"?email={email}&age={age}&until={until_age}&contribution={contribution}"
                st.success("シミュレーション完了！")
                st.markdown(f"**[あなたのレポートを見る]({report_url_full})**")
                st.markdown("---")
                st.markdown("#### UTAGEステップメール用のURL（コピペ用）")
                st.code(f"https://サーバーURL/?email={{メールアドレス}}&age={{年齢}}&until={{何歳まで}}&contribution={{掛金}}", language=None)
                st.caption("UTAGEの差し込みタグを使って、上記の{メールアドレス}等を実際のタグに置き換えてください")
