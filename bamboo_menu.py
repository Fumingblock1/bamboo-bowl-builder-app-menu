from flask import Flask, request, redirect, session
import urllib.parse
import os
import requests
import hashlib
import hmac
import uuid
import json

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "bamboo-bowls-secret-2024")

IKHOKHA_APP_ID = os.environ.get("IKHOKHA_APP_ID")
IKHOKHA_SECRET_KEY = os.environ.get("IKHOKHA_SECRET_KEY")
IKHOKHA_API_URL = "https://api.ikhokha.com/v1/paylink"

signature_bowls = [
    {"name": "Lemon Peri-Peri Calamari on Forbidden Rice", "price": 94.90},
    {"name": "Thai Green Veg Bowl on Quinoa", "price": 71.90},
    {"name": "Orange Duck & Red Veg on Noodles", "price": 99.90},
    {"name": "Sweet and Sour Pichana Steak on Udon", "price": 89.90},
    {"name": "Tonkatsu Tofu & Cashew Fried Rice", "price": 79.90},
    {"name": "Satay Pork on Garlic Fried Rice", "price": 89.90},
]

menu_steps = [
    {"title": "Step 1 - Craft your Base", "name": "base", "items": {"Garlic fried rice": 17.90, "Steamed rice": 17.90, "Quinoa mix": 19.90, "Noodles": 17.90, "Udon": 30.90, "Forbidden rice": 20.90, "None": 0.00}, "multi": True},
    {"title": "Step 2 - Pick your Protein", "name": "protein", "items": {"Falafel": 12.90, "Venison": 23.90, "Pichana steak": 29.90, "Tofu": 17.90, "Salmon": 70.90, "Prawns": 40.90, "Pork belly": 30.90, "Tuna": 45.90, "Chicken": 17.90, "Duck": 40.90, "None": 0.00}, "multi": True},
    {"title": "Step 3 - Select your Greens", "name": "greens", "items": {"Seasonal veg": 17.90, "Greens": 18.90, "Baby veg": 18.90, "Exotic mushrooms": 21.90, "Stir fry veg": 17.90, "Red veg": 18.90, "None": 0.00}, "multi": True},
    {"title": "Step 4 - Drizzle your Delight", "name": "drizzle", "items": {"Sweet chiili": 12.90, "Chimichurri": 12.90, "Japanese mayo": 20.90, "Orange sauce": 12.90, "Lemon peri peri": 12.90, "Sweet and sour": 12.90, "Satay": 12.90, "Teriyaki": 12.90, "Thai green curry": 12.90, "Tonkatsu": 12.90, "None": 0.00}, "multi": True},
    {"title": "Step 5 - Muscle up your Bowl", "name": "muscle", "items": {"Chilli": 4.90, "Fried onion": 9.90, "Egg": 8.90, "Avocado": 11.90, "Mango": 10.90, "Pineapple": 10.90, "Chick peas": 11.90, "Cashew": 16.90, "Gochujang": 18.90, "None": 0.00}, "multi": True},
    {"title": "Step 6 - Quench your Thirst", "name": "drink", "items": {"Coke": 18.90, "Fanta": 18.90, "Coke zero": 19.90, "Coke light": 19.90, "Mountain falls": 24.90, "Steri stumpi": 25.90, "Fruticana": 19.90, "None": 0.00}, "multi": True},
    {"title": "Step 7 - Sweet Tooth", "name": "sweet", "items": {"Churros + Chocolate Sauce": 49.90, "Churros + Caramel Sauce": 49.90, "Churros + Milkybar Sauce": 49.90, "None": 0.00}, "multi": True}
]

def create_ikhokha_payment(amount_rands, order_summary, transaction_id):
    amount_cents = int(round(amount_rands * 100))
    base_url = os.environ.get("BASE_URL", "https://bamboo-bowls.co.za")

    payload = {
        "entityID": IKHOKHA_APP_ID,
        "amount": amount_cents,
        "currency": "ZAR",
        "requesterUrl": base_url,
        "mode": "live",
        "externalTransactionID": transaction_id,
        "urls": {
            "successPageUrl": f"{base_url}/success?tid={transaction_id}",
            "failurePageUrl": f"{base_url}/failed",
            "cancelUrl": f"{base_url}/",
        }
    }

    payload_str = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(
        IKHOKHA_SECRET_KEY.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "ApplicationId": IKHOKHA_APP_ID,
        "Signature": signature
    }

    response = requests.post(IKHOKHA_API_URL, json=payload, headers=headers, timeout=10)
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('customer_name', 'Customer').strip() or "Customer"
        total = 0.0
        msg_parts = [f"🌿 New Bamboo Order: {name} 🌿\n"]
        has_items = False

        selected_sigs = request.form.getlist('signature[]')
        for sig_name in selected_sigs:
            sig = next((s for s in signature_bowls if s["name"] == sig_name), None)
            if sig:
                has_items = True
                msg_parts.append(f"--- SIGNATURE BOWL ---")
                msg_parts.append(f"• {sig['name']} (R{sig['price']:.2f})")
                msg_parts.append(f"Subtotal: R{sig['price']:.2f}\n")
                total += sig['price']

        for i in range(10):
            b_items, b_total = [], 0.0
            for step in menu_steps:
                field = f"{step['name']}[]" if i == 0 else f"{step['name']}[{i}][]"
                selected = request.form.getlist(field)
                for item in selected:
                    if item != "None" and item in step["items"]:
                        price = step["items"][item]
                        b_items.append(f"• {item} (R{price:.2f})")
                        b_total += price
            if b_items:
                has_items = True
                msg_parts.append(f"--- BOWL {i+1} ---")
                msg_parts.extend(b_items)
                msg_parts.append(f"Subtotal: R{b_total:.2f}\n")
                total += b_total

        if not has_items:
            return "<h2>No items selected.</h2><a href='/'>Go back</a>"

        msg_parts.append(f"TOTAL: R{total:.2f}")
        transaction_id = str(uuid.uuid4())
        session[transaction_id] = {
            "name": name,
            "msg": "\n".join(msg_parts),
            "total": f"R{total:.2f}"
        }

        try:
            result = create_ikhokha_payment(total, "\n".join(msg_parts), transaction_id)
            pay_url = result.get("paylinkUrl")
            if pay_url:
                return redirect(pay_url)
        except Exception as e:
            print(f"iKhokha API error: {e}")

        # Fallback if API fails
        encoded_message = urllib.parse.quote("\n".join(msg_parts))
        wa_url = f"https://wa.me/27678081176?text={encoded_message}"
        return redirect(f"/summary?wa={urllib.parse.quote(wa_url)}&tid={transaction_id}")

    # GET
    tpl = ""
    for s in menu_steps:
        itype = "checkbox" if s["multi"] else "radio"
        opts = ""
        for x, p in s["items"].items():
            if x != "None":
                img_tag = f'<img src="/static/images/{x}.jpg.png" alt="{x}" class="item-img" onerror="this.src=\'/static/images/{x}.jpg.jpg\';this.onerror=function(){{this.style.display=\'none\'}}">'
            else:
                img_tag = ''
            opts += f'<label class="item-label">{img_tag}<span class="item-text"><input type="{itype}" name="{s["name"]}[ID][]" value="{x}"> {x} (R{p:.2f})</span></label>'
        tpl += f'<div class="step"><h3>{s["title"]}</h3>{opts}</div>'

    sig_html = ""
    for sig in signature_bowls:
        img_tag = f'<img src="/static/images/{sig["name"]}.jpg.png" alt="{sig["name"]}" class="sig-img" onerror="this.src=\'/static/images/{sig["name"]}.jpg.jpg\';this.onerror=function(){{this.style.display=\'none\'}}">'
        sig_html += f'''
        <label class="sig-label">
            <input type="checkbox" name="signature[]" value="{sig["name"]}">
            {img_tag}
            <span class="sig-text">
                <strong>{sig["name"]}</strong><br>
                <span style="color:#4caf50;">R{sig["price"]:.2f}</span>
            </span>
        </label>'''

    sig_prices_js = ', '.join([f'"{s["name"]}": {s["price"]}' for s in signature_bowls])
    item_prices_js = ', '.join([f'"{x}": {p}' for s in menu_steps for x, p in s["items"].items()])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Bamboo Bowls</title>
        <style>
            body {{ background: #000; color: #fff; font-family: sans-serif; padding: 15px; margin: 0; }}
            .container {{ max-width: 500px; margin: auto; }}
            .bowl-section {{ background: #111; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #333; }}
            .sig-section {{ background: #111; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #4caf50; }}
            .sig-section h2 {{ color: #4caf50; margin-top: 0; text-align: center; font-size: 1.4rem; }}
            .sig-label {{ display: flex; align-items: center; padding: 10px 8px; color: #bbb; cursor: pointer; border-radius: 8px; transition: background 0.2s; border-bottom: 1px solid #222; }}
            .sig-label:hover {{ background: #1a1a1a; }}
            .sig-label:last-child {{ border-bottom: none; }}
            .sig-img {{ width: 80px; height: 80px; object-fit: cover; border-radius: 10px; margin: 0 14px 0 10px; border: 2px solid #4caf50; flex-shrink: 0; }}
            .sig-text {{ flex: 1; font-size: 0.95rem; line-height: 1.4; }}
            .sig-label input[type="checkbox"] {{ transform: scale(1.3); margin-right: 4px; flex-shrink: 0; }}
            .step {{ border-bottom: 1px solid #222; padding: 10px 0; }}
            h3 {{ color: #4caf50; margin: 0 0 10px 0; font-size: 1rem; }}
            .item-label {{ display: flex; align-items: center; padding: 8px; color: #bbb; cursor: pointer; transition: background 0.2s; border-radius: 8px; }}
            .item-label:hover {{ background: #1a1a1a; }}
            .item-img {{ width: 60px; height: 60px; object-fit: cover; border-radius: 8px; margin-right: 12px; border: 2px solid #333; flex-shrink: 0; }}
            .item-text {{ flex: 1; display: flex; align-items: center; }}
            input[type="checkbox"], input[type="radio"] {{ transform: scale(1.2); margin-right: 12px; }}
            .btn {{ width: 100%; padding: 16px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; }}
            .btn-add {{ background: #222; color: #4caf50; border: 1px solid #4caf50; margin-bottom: 10px; }}
            .btn-submit {{ background: #4caf50; color: #fff; font-size: 18px; }}
            .btn-remove {{ background: #ff4d4d; color: #fff; width: auto; padding: 5px 10px; float: right; font-size: 12px; border: none; border-radius: 6px; cursor: pointer; }}
            .name-input {{ width: 100%; padding: 16px; background: #111; border: 1px solid #333; color: #fff; border-radius: 10px; box-sizing: border-box; margin-bottom: 25px; font-size: 18px; }}
            .divider {{ text-align: center; color: #555; margin: 20px 0; font-size: 14px; letter-spacing: 2px; }}
            .total-bar {{ background: #1a1a1a; border: 1px solid #4caf50; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; font-size: 22px; color: #4caf50; font-weight: bold; display: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="color:#4caf50; text-align:center;">🌿 Bamboo Bowls</h1>
            <form method="post" id="orderForm">
                <input type="text" name="customer_name" class="name-input" placeholder="Your Name" required>

                <div class="sig-section">
                    <h2>⭐ Signature Bowls</h2>
                    {sig_html}
                </div>

                <div class="divider">── OR BUILD YOUR OWN ──</div>

                <div id="bowl-container">
                    <div class="bowl-section" id="bowl-0">
                        <h2 style="color:#4caf50; margin-top:0;">Bowl #1</h2>
                        {tpl.replace('[ID]', '')}
                    </div>
                </div>
                <button type="button" class="btn btn-add" onclick="addBowl()">+ Add Another Bowl</button>

                <div class="total-bar" id="totalBar">Total: R0.00</div>

                <button type="submit" class="btn btn-submit">💳 Pay Now ➔</button>
            </form>
        </div>
        <script>
            const sigPrices = {{{sig_prices_js}}};
            const itemPrices = {{{item_prices_js}}};

            function updateTotal() {{
                let total = 0;
                document.querySelectorAll('input[name="signature[]"]:checked').forEach(el => {{
                    total += sigPrices[el.value] || 0;
                }});
                document.querySelectorAll('input[type="checkbox"]:not([name="signature[]"]):checked, input[type="radio"]:checked').forEach(el => {{
                    if (el.value !== "None") total += itemPrices[el.value] || 0;
                }});
                const bar = document.getElementById('totalBar');
                if (total > 0) {{
                    bar.style.display = 'block';
                    bar.textContent = 'Total: R' + total.toFixed(2);
                }} else {{
                    bar.style.display = 'none';
                }}
            }}

            document.getElementById('orderForm').addEventListener('change', updateTotal);

            let count = 1;
            function addBowl() {{
                const container = document.getElementById('bowl-container');
                const div = document.createElement('div');
                div.className = 'bowl-section';
                div.id = 'bowl-' + count;
                let inner = `{tpl}`;
                div.innerHTML = `<button type="button" class="btn btn-remove" onclick="rm(${{count}})">Remove</button>` +
                                `<h2 style="color:#4caf50; margin-top:0;">Bowl #${{count + 1}}</h2>` +
                                inner.replace(/\\[ID\\]/g, '[' + count + ']');
                container.appendChild(div);
                div.addEventListener('change', updateTotal);
                count++;
                window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
            }}
            function rm(id) {{
                document.getElementById('bowl-' + id).remove();
                updateTotal();
            }}
        </script>
    </body>
    </html>
    """

@app.route('/success')
def success():
    tid = request.args.get('tid', '')
    order = session.get(tid, {})
    name = order.get('name', 'Customer')
    msg = order.get('msg', '')

    encoded_message = urllib.parse.quote(msg)
    wa_url = f"https://wa.me/27678081176?text={encoded_message}"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Payment Successful - Bamboo Bowls</title>
        <style>
            body {{ background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:40px 20px; }}
            .card {{ background:#111; padding:25px; border-radius:15px; border:1px solid #4caf50; margin:20px auto; max-width:500px; text-align:left; }}
            .btn {{ display:block; max-width:400px; margin:20px auto; padding:20px; background:#4caf50; color:#fff; text-decoration:none; border-radius:15px; font-weight:bold; font-size:20px; text-align:center; }}
        </style>
    </head>
    <body>
        <div style="font-size:60px;">✅</div>
        <h1 style="color:#4caf50;">Payment Successful!</h1>
        <p style="color:#aaa;">Thank you {name}! Now send us your order on WhatsApp and we'll get cooking! 🌿</p>
        <div class="card">
            <pre style="white-space: pre-wrap; color:#ccc; font-size:14px;">{msg}</pre>
        </div>
        <a href="{wa_url}" class="btn">SEND ORDER VIA WHATSAPP ➔</a>
        <p style="margin-top:20px;"><a href="/" style="color:#888;">← Back to menu</a></p>
    </body>
    </html>
    """

@app.route('/failed')
def failed():
    return """
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Payment Failed</title></head>
    <body style="background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:50px 20px;">
        <div style="font-size:60px;">❌</div>
        <h1 style="color:#ff4d4d;">Payment Failed</h1>
        <p style="color:#aaa;">Don't worry, your order was not placed. Please try again.</p>
        <a href="/" style="display:block; max-width:300px; margin:30px auto; padding:18px; background:#4caf50; color:#fff; text-decoration:none; border-radius:12px; font-weight:bold;">Try Again ➔</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting Bamboo menu...")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
