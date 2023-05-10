import random
from flask import  make_response, render_template, request, redirect, session, url_for
from sqlalchemy import func
from database_handler import Product, Order, OrderItem, app, db
from flask.logging import default_handler
app.secret_key = "xC43)#Sqy1Yvzx8!m*bP{5gF&%hJLdK^W~VNf7j_@lI]O-tZu0o6Rp+9TAM<EQ2r|HGBk.D>U^&;[s}a\`/:qn"

def get_image_url(image_file):
    image = url_for("static", filename=f"images/{image_file}")
    if not image:
        return url_for("static", filename="images/generic_image.png")
    return url_for("static", filename=f"images/{image_file}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "change-address" in request.form:
            address = [
                request.form.get("address_street"),
                request.form.get("address_house"),
                request.form.get("address_zip"),
                request.form.get("address_state"),
                request.form.get("address_city"),
                request.form.get("address_country")
            ]
            session["address"] = address
            session["isAddress"] = True
            
        elif "add-to-basket" in request.form:
            item_id = request.form.get("add-to-basket")
            if "cart" in session:
                cart_items = session["cart"]
                cart_items.append(item_id)
                session["cart"] = cart_items
            else:
                session["cart"] = [item_id]


    item_info = Product.query.order_by(func.random()).limit(9).all()
    address = session.get("address")
    advert = adverts[random.randint(0, len(adverts)-1)]
    return render_template("index.html", no_items=len(item_info), item_info=item_info, address=address, 
                           isAddress= session.get("isAddress", False), advert_image = advert)

@app.route("/cart", methods=["POST", "GET"])
def cart():
    total_price = 0.0 
    if request.method == "POST":
        if "remove-from-basket" in request.form:
            item_id = request.form.get("remove-from-basket")
            all_items = session.get("cart")  
            if all_items and item_id in all_items:
                all_items.remove(item_id)  
                session["cart"] = all_items             
        elif "remove-all" in request.form:
            session["cart"] = []
            print(session["cart"])
        elif "update-quantity" in request.form:
            item_id = request.form.get("update-quantity")
            quantity = int(request.form.get("quantity"))
            all_items = session.get("cart")
            no_items_at = all_items.count(str(item_id))
            if quantity < no_items_at:
                while no_items_at > quantity:
                    all_items.remove(str(item_id))
                    no_items_at -= 1
            else:
                for _ in range(quantity - no_items_at):
                    all_items.append(str(item_id))
            session["cart"] = all_items

    all_cart_items = session.get("cart", [])
    actual_items = []
    numberof = {}
    no_internal_items = 0
    for item_id in all_cart_items:
        product = Product.query.filter_by(id=item_id[0]).first()
        if not (str(item_id) in numberof):
            numberof[str(item_id)] = 1
            actual_items.append(product)
        else:
            numberof[str(item_id)] += 1
        total_price += product.price
        no_internal_items += 1
    address = session.get("address")
    advert = adverts[random.randint(0, len(adverts)-1)]

    return render_template("cart.html", no_cart_items = no_internal_items,  no_items = len(numberof), 
                           cart_items = actual_items, total_price = round(total_price, 2), numberof = numberof,
                           address=address, isAddress= session.get("isAddress", False), advert_image = advert)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        if "search" in request.form:
            search_query = request.form["search"]
        elif "add-to-basket" in request.form:
            item_id = request.form.get("add-to-basket")
            if "cart" in session:
                cart_items = session["cart"]
                cart_items.append(item_id)
                session["cart"] = cart_items
            else:
                session["cart"] = [item_id]

    if session["order_by"] == "nameaz":
        order_by = Product.name.asc()
    elif session["order_by"] == "nameza":
        order_by = Product.name.desc()
    elif session["order_by"] == "pricelh":
        order_by = Product.price.asc()
    elif session["order_by"] == "pricehl":
        order_by = Product.price.desc()
    elif session["order_by"] == "envimplh":
        order_by = Product.environmental_impact.asc()
    elif session["order_by"] == "envimphl":
        order_by = Product.environmental_impact.desc()

    item_info = Product.query.filter(Product.name.ilike(f"%{search_query}%")).order_by(order_by).all()
    additional_items = []
    if len(item_info) < 10:
        subquery = db.session.query(Product.id).filter(Product.id.in_([p.id for p in item_info]))
        additional_items = Product.query.filter(~Product.id.in_(subquery)).order_by(order_by).limit(10-len(item_info)).all()        
        not_enough_items = [True, len(item_info)]
    else:
        not_enough_items = [False, 0]



    images = [get_image_url(item.name) for item in item_info]

    if len(item_info) != len(images):
        return "Error: number of items and images do not match"
    no_items = len(item_info) + len(additional_items)
    address = session.get("address")
    advert = adverts[random.randint(0, len(adverts)-1)]
    return render_template("search.html", item_info=item_info, no_additional_items = len(additional_items), additional_items=additional_items, 
                           no_items=no_items, images=images, address=address, not_enough_items=not_enough_items, 
                           isAddress= session.get("isAddress", False), advert_image = advert)

@app.route("/environmental_impact_info")
def environmental_impact_info():
    address = session.get("address")
    advert = adverts[random.randint(0, len(adverts)-1)]
    return render_template("envimp.html", address=address, isAddress=session.get("isAddress", False), advert_image = advert)

@app.route("/update_order_by", methods=["POST"])
def update_order_by():
    order_by = request.form["order_by"]
    session["order_by"] = order_by
    
    return "Order updated successfully"

@app.route("/checkout", methods=["POST", "GET"])
def checkout():
    if request.method == "POST":
        if "place-order" in request.form:
            cart_items = session.get("cart")
            total_price = request.form.get("total_price")
            if cart_items:
                # Create a new order
                order = Order(total_price=float(total_price))
                db.session.add(order)
                db.session.commit()

                # Add order items to the new order
                for item_id in cart_items:
                    order_item = OrderItem(product_id=item_id, order_id=order.id)
                    db.session.add(order_item)

                # Clear the cart
                session["cart"] = []
                return redirect(url_for("index"))
    cart_items = session.get("cart")

    if cart_items == []:
        return redirect(url_for("cart"))


    address = session.get("address", [])
    if address == []:
        return redirect(url_for("cart"))
    else:
        total_price = 0.0 
        for item_id in cart_items:
            total_price += Product.query.get(item_id).price 
            total_price += Product.query.get(item_id).delivery_fee 
        no_items = len(cart_items)
        address = session.get("address")

    actual_cart_items = []
    for pos in range(0, len(cart_items)):
        actual_cart_items.append(Product.query.get(cart_items[pos]))
    advert = adverts[random.randint(0, len(adverts)-1)]
    return render_template("checkout.html", cart_items=actual_cart_items, no_items=no_items, total_price=round(total_price,2), 
                           address=address, isAddress= session.get("isAddress", False), advert_image = advert)

@app.route("/product_view", methods=["POST", "GET"])
def product_view():
    if request.args.get('item_id') is not None:
        product = Product.query.filter_by(id=request.args.get("item_id")).first()
        address = session.get("address")
        advert = adverts[random.randint(0, len(adverts)-1)]
        return render_template("item.html", item_info = product, address=address, isAddress = session.get("isAddress", False), advert_image=advert)

if __name__ == "__main__":
    adverts = ["CCAdvertisement.jpg"]
    with app.app_context():
        app.run(debug=True)
