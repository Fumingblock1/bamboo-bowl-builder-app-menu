from flask import Flask, request
import urllib.parse
import os

app = Flask(__name__)

menu_steps = [
    {"title": "Step 1 - Craft your Base", "name": "base", "items": {"Garlic fried rice": 17.90, "Steamed rice": 17.90, "Quinoa mix": 19.90, "Noodles": 17.90, "Udon": 30.90, "Forbidden rice": 20.90, "None": 0.00}, "multi": True},
    {"title": "Step 2 - Pick your Protein", "name": "protein", "items": {"Falafel": 12.90, "Venison": 23.90, "Pichana steak": 29.90, "Tofu": 17.90, "Salmon": 70.90, "Prawns": 40.90, "Pork belly": 30.90, "Tuna": 45.90, "Chicken": 17.90, "Duck": 40.90, "None": 0.00}, "multi": True},
    {"title": "Step 3 - Select your Greens", "name": "greens", "items": {"Seasonal veg": 17.90, "Greens": 18.90, "Baby veg": 18.90, "Exotic mushrooms": 21.90, "Stir fry veg": 17.90, "Red veg": 18.90, "None": 0.00}, "multi": True},
    {"title": "Step 4 - Drizzle your Delight", "name": "drizzle", "items": {"Sweet chiili": 12.90, "Chimichurri": 12.90, "Japanese mayo": 20.90, "Orange sauce": 12.90, "Lemon peri peri": 12.90, "Sweet and sour": 12.90, "Satay": 12.90, "Teriyaki": 12.90, "Thai green curry": 12.90, "Tonkatsu": 12.90, "None": 0.00}, "multi": True},
    {"title": "Step 5 - Muscle up your Bowl", "name": "muscle", "items": {"Chilli": 4.90, "Fried onion": 9.90, "Egg": 8.90, "Avocado": 11.90, "Mango": 10.90, "Pineapple": 10.90, "Chick peas": 11.90, "Cashew": 16.90, "Gochujang": 18.90, "None": 0.00}, "multi": True},
    {"title": "Step 6 - Quench your Thirst", "name": "drink", "items": {"Coke": 18.90, "Fanta": 18.90, "Coke zero": 19.90, "Coke light": 19.90, "Mountain falls": 24.90, "Steri stumpi": 25.90, "Fruticana": 19.90, "None": 0.00}, "multi": True},
    {"title": "Step 7 - Sweet Tooth", "name": "sweet", "items": {"Churros + Chocolate Sauce": 49.90, "Churros + Caramel Sauce": 49.90, "Churros + Milkybar Sauce": 49.90, "None": 0.00}, "multi": True}
]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('customer_name', 'Customer').strip() or "Customer"
        total = 0.0
        msg_parts = [f"🌿 New Bamboo Order: {name} 🌿\n"]
        has_items = False
        
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

        grand_total = f"R{total:.2f}"

        ik_pay_button = f"""
        <div style="width: 160px; margin: 30px auto; text-align: center;">
            <h6 style="margin: 10px 0; padding: 0; font-family: roboto-regular, sans-serif; font-size: 14px; color: #1d1d1b;">
                Bamboo Bowls
            </h6>
            <a href="https://pay.ikhokha.com/bamboo-bowls/buy/bamboobowls" style="text-decoration: none;">
                <div style="overflow: hidden; display: flex; justify-content: center; align-items: center; width: 100%; height: 48px; background: #0BB3BF; color: #FFFFFF; border: 1px solid #e5e5e5; box-shadow: 1px solid #e5e5e5; border-radius: 16px; font-family: roboto-medium, sans-serif; font-weight: 700;">
                    Pay Now {grand_total}
                </div>
            </a>
            <h6 style="margin: 5px 0; padding: 0; font-size: 8px; font-family: roboto-regular, sans-serif; text-align: center;">
                Powered by iKhokha
            </h6>
        </div>
        """

        encoded_message = urllib.parse.quote("\n".join(msg_parts))
        wa_url = f"https://wa.me/27678081176?text={encoded_message}"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Order Summary - Bamboo Bowls</title>
            <style>
                body {{ background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:50px 20px; }}
                .summary {{ background:#111; padding:25px; border-radius:15px; border:1px solid #333; margin:20px auto; max-width:500px; text-align:left; }}
                .btn {{ display:block; max-width:400px; margin:20px auto; padding:20px; background:#4caf50; color:#fff; text-decoration:none; border-radius:15px; font-weight:bold; font-size:22px; box-shadow:0 10px 20px rgba(0,0,0,0.5); }}
            </style>
        </head>
        <body>
            <h1 style="color:#4caf50;">Order Summary</h1>
            <div class="summary">
                <p>Customer: <strong>{name}</strong></p>
                <p>Total: <strong style="color:#4caf50; font-size:28px;">{grand_total}</strong></p>
                <hr style="border-color:#333;">
                <pre style="white-space: pre-wrap; color:#ccc;">{"\n".join(msg_parts)}</pre>
            </div>

            {ik_pay_button}

            <a href="{wa_url}" class="btn">CONFIRM & SEND ORDER VIA WHATSAPP ➔</a>

            <p style="margin-top:30px; color:#888;">
                <a href="/" style="color:#aaa; text-decoration:none;">← Change my order</a>
            </p>
        </body>
        </html>
        """

    # GET - form builder
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="color:#4caf50; text-align:center;">🌿 Bamboo Bowls</h1>
            <form method="post">
                <input type="text" name="customer_name" class="name-input" placeholder="Your Name" required>
                <div id="bowl-container">
                    <div class="bowl-section" id="bowl-0">
                        <h2 style="color:#4caf50; margin-top:0;">Bowl #1</h2>
                        {tpl.replace('[ID]', '')}
                    </div>
                </div>
                <button type="button" class="btn btn-add" onclick="addBowl()">+ Add Another Bowl</button>
                <button type="submit" class="btn btn-submit">Review & Pay ➔</button>
            </form>
        </div>
        <script>
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
                count++;
                window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
            }}
            function rm(id) {{ document.getElementById('bowl-' + id).remove(); }}
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting Bamboo menu...")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
