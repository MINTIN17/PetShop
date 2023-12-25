from datetime import datetime

from flask import render_template, request, jsonify, session, redirect, url_for
import utils

from PetShop import app, mysql

import cloudinary.uploader
import io
import base64

@app.route('/')
def home():
    soluong = utils.view_cart()
    latest_products = utils.latest_products()

    hot_products = utils.hot_products()
    return render_template('index.html', soluong = soluong, latest_products = latest_products, hot_products = hot_products)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_account', methods=['get', 'post'])
def login_account():
    username = request.form.get('username')
    password = request.form.get('password')
    acc = None
    acc = utils.checklogin(username, password)
    if acc == None:
        return render_template('login.html', result="Sai tai khoan hoac mat khau")
    if acc['isAdmin'] == b'\x01':
        tongsanpham = utils.Tongsanpham()
        tonguser = utils.Tonguser()
        tongdh = utils.TongDonHang()
        doanhthungay = utils.Doanhthungay()
        doanhthuthang = utils.Doanhthuthang()
        return render_template('./admin/index.html', tongsanpham = tongsanpham, tonguser = tonguser, tongdh = tongdh, doanhthungay =doanhthungay, doanhthuthang = doanhthuthang)

    session['username'] = acc['username']
    session['uID'] = acc['uID']

    return redirect(url_for('home'))

# @app.route('/login_account', methods=['POST'])
# def login_account():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     acc = None
#     acc = utils.checklogin(username, password)
#     if acc is None or 'username' not in acc:
#         return render_template('login.html', result="Sai tài khoản hoặc mật khẩu")
#
#     session['username'] = acc['username']
#     session['uID'] = acc['uID']
#
#
#     return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('uID', 0)
    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Nhận thông tin từ form đăng ký
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']

        # Xử lý lưu thông tin vào cơ sở dữ liệu (ví dụ: MySQL)
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO account (username, password, name, email, address) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (username, password, name, email, address))
        mysql.connection.commit()
        cursor.close()

        return render_template('login.html')
    return render_template('signup.html')



@app.route('/tintuc')
def tintuc():
    soluong = utils.view_cart()
    return render_template('tintuc.html',soluong=soluong)

@app.route('/shop')
def shop():
    cates = utils.load_catefory()
    products = utils.load_products()

    products = utils.load_category_products()
    soluong = utils.view_cart()
    return render_template('shop.html',categories=cates, products=products,soluong=soluong)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = utils.product_detail(product_id)
    soluong = utils.view_cart()
    return render_template('product_detail.html', product=product, soluong=soluong)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    try:
        cur = mysql.connection.cursor()
        accountID = session.get('uID')
        if accountID == None:
            return redirect(url_for('login'))

        check_query = "SELECT * FROM cart WHERE accountID = %s AND productID = %s"
        cur.execute(check_query, (accountID, product_id))
        existing_item = cur.fetchone()

        if existing_item:
            # Nếu sản phẩm đã có trong giỏ hàng, cập nhật số lượng
            update_query = "UPDATE cart SET amount = amount + 1 WHERE accountID = %s AND productID = %s"
            cur.execute(update_query, (accountID, product_id))
            mysql.connection.commit()
        else:
            # Nếu sản phẩm chưa có trong giỏ hàng, thêm mới
            add_query = "INSERT INTO cart (accountID, productID, amount) VALUES (%s, %s, %s)"
            cur.execute(add_query, (accountID, product_id, 1))
            mysql.connection.commit()

        soluong = utils.view_cart()
        product = utils.product_detail(product_id)
        return render_template('product_detail.html',product=product, soluong=soluong)

    finally:
        cur.close()

@app.route('/cart')
def cart():
    cursor = mysql.connection.cursor()
    accountID = session.get('uID')
    if accountID == None:
        return redirect(url_for('login'))
    # Lấy thông tin các sản phẩm trong giỏ hàng từ cơ sở dữ liệu
    query = "SELECT  cart.maCart,product.title, product.image, product.price, cart.amount FROM cart JOIN product ON cart.productID = product.id WHERE cart.accountID = %s"
    cursor.execute(query, (accountID,))
    cart_items = cursor.fetchall()
    print(cart_items)

    cursor.close()
    soluong = utils.view_cart()

    total_price = sum(item['price'] * item['amount'] for item in cart_items)
    shipping_fee = 30000
    total_payment = total_price + shipping_fee

    return render_template('cart_item.html', cart_items=cart_items, soluong=soluong, total_payment = total_payment, total_price = total_price)



@app.route('/buy_now/<int:product_id>', methods=['POST'])
def buy_now(product_id):
    try:
        cur = mysql.connection.cursor()
        accountID = session.get('uID')
        if accountID == None:
            return redirect(url_for('login'))

        check_query = "SELECT * FROM cart WHERE accountID = %s AND productID = %s"
        cur.execute(check_query, (accountID, product_id))
        existing_item = cur.fetchone()

        if existing_item:
            # Nếu sản phẩm đã có trong giỏ hàng, cập nhật số lượng
            update_query = "UPDATE cart SET amount = amount + 1 WHERE accountID = %s AND productID = %s"
            cur.execute(update_query, (accountID, product_id))
            mysql.connection.commit()
        else:
            # Nếu sản phẩm chưa có trong giỏ hàng, thêm mới
            add_query = "INSERT INTO cart (accountID, productID, amount) VALUES (%s, %s, %s)"
            cur.execute(add_query, (accountID, product_id, 1))
            mysql.connection.commit()

        return redirect(url_for('cart'))
    finally:
        cur.close()

@app.route('/delete_cart/<int:cart_id>', methods=['DELETE'])
def delete_cart(cart_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM cart WHERE maCart = %s", (cart_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Cart đã được xóa khỏi cơ sở dữ liệu thành công'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/update_amount', methods=['POST'])
def update_amount():
    # Nhận dữ liệu từ yêu cầu POST
    new_amount = request.json['newAmount']
    print(new_amount)
    ma_cart = request.json['maCart']

    print(ma_cart)

    try:
        cursor = mysql.connection.cursor()
        sql = "UPDATE cart SET amount = %s WHERE maCart = %s"
        val = (new_amount, ma_cart)
        cursor.execute(sql, val)
        mysql.connection.commit()  # Commit thay đổi vào CSDL
        cursor.close()

        cart_items = utils.cart_detail()
        total_price = sum(item['price'] * item['amount'] for item in cart_items)
        shipping_fee = 30000
        total_payment = total_price + shipping_fee

        # Phản hồi với dữ liệu mới bao gồm total_price và total_payment
        return jsonify(success=True, total_price=total_price, total_payment=total_payment)
    except Exception as e:
        # Xử lý nếu có lỗi
        print("Error:", e)
        return jsonify(success=False, error=str(e)), 500




@app.route('/dathang')
def dathang():
    soluong = utils.view_cart()
    return render_template('dathang.html',soluong=soluong)


@app.route('/process_order', methods=['POST'])
def process_order():
    if request.is_json:  # Kiểm tra xem request có phải là JSON hay không
        data = request.json
        accountID = session.get('uID')
        tongGia = utils.tongGia(accountID)
        print(tongGia)
        NgayXuat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ten = data.get('fullName')
        sdt = data.get('phone')
        address = data.get('email')
        email = data.get('address')

        cursor = mysql.connection.cursor()
        if accountID and tongGia and NgayXuat:  # Kiểm tra xem các trường thông tin cần thiết có tồn tại không
            # Thêm thông tin đặt hàng vào bảng invoice
            sql_invoice = "INSERT INTO invoice (accountID, tongGia, ngayXuat, fullName, phone, email, address) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val_invoice = (
                accountID,
                tongGia,
                NgayXuat,
                ten,
                sdt,
                address,
                email
            )
            cursor.execute(sql_invoice, val_invoice)
            mysql.connection.commit()


            # Xóa tất cả sản phẩm khỏi giỏ hàng và cập nhật số lượng giỏ hàng
            sql_update_cart = "DELETE FROM cart WHERE accountID = %s"
            val_update_cart = (accountID,)
            cursor.execute(sql_update_cart, val_update_cart)
            mysql.connection.commit()


            # In ra thông báo đặt hàng thành công
            return jsonify({'message': 'Đặt hàng thành công'})

    return jsonify({'message': 'Dữ liệu không hợp lệ'})

@app.route('/search_sp', methods=['GET'])
def search_sp():
        keyword = request.args.get('keyword')
        print('keyword')
        # Truy vấn SQL để tìm kiếm sản phẩm
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM product WHERE LOWER(title) LIKE %s"
        val = ('%' + keyword.lower() + '%',)

        cursor.execute(sql, val)
        results = cursor.fetchall()
        print(results)
        cursor.close()
        cates = utils.load_catefory()
        soluong = utils.view_cart()
        return render_template('shop.html',categories=cates, products=results, soluong=soluong)


@app.route('/sort_products', methods=['GET'])
def sort_products():
    cates = utils.load_catefory()
    soluong = utils.view_cart()
    sort_option = request.args.get('sort_option')
    if sort_option == 'price_asc':
        # Sắp xếp theo giá tăng dần từ cơ sở dữ liệu
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM product ORDER BY price ASC"
        cursor.execute(sql)
        products = cursor.fetchall()
        cursor.close()
        return render_template('shop.html', categories=cates, products=products, soluong=soluong)
    elif sort_option == 'price_desc':
        # Sắp xếp theo giá giảm dần từ cơ sở dữ liệu
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM product ORDER BY price DESC"
        cursor.execute(sql)
        products = cursor.fetchall()
        cursor.close()
        return render_template('shop.html', categories=cates, products=products, soluong=soluong)

    else:
        products = utils.load_category_products()
        return render_template('shop.html', categories=cates, products=products, soluong=soluong)


# admin






@app.route('/tongquan')
def tongquan():
    tongsanpham = utils.Tongsanpham()
    tonguser = utils.Tonguser()
    tongdh = utils.TongDonHang()
    doanhthungay = utils.Doanhthungay()
    doanhthuthang = utils.Doanhthuthang()
    return jsonify({"tongsanpham": tongsanpham, "tonguser": tonguser, "tongdh": tongdh, "doanhthungay": doanhthungay, "doanhthuthang": doanhthuthang})


@app.route('/sanpham')
def sanpham():
    list_product = utils.getlist()
    return render_template('./admin/sanpham.html', list_product = list_product)

@app.route('/donhang')
def donhang():
    list_donhang = utils.list_donhang()
    print(list_donhang)
    return render_template('./admin/DonHang.html', list_donhang = list_donhang)

@app.route('/listaccount')
def listaccount():
    listaccount = utils.get_listadmin()

    return render_template('./admin/account.html', listaccount = listaccount)

@app.route('/listuser')
def listuser():
    listaccount = utils.get_listuser()
    return render_template('./admin/account.html', listaccount = listaccount)

@app.route('/get_user')
def getuser():
    id = request.args.get('id')
    user = utils.get_user(id)
    if user['isAdmin'] == b'\x01':
        user['isAdmin'] = 1
    else:
        user['isAdmin'] = 0
    return jsonify({"user": user})

@app.route('/get_product')
def getproduct():
    id = request.args.get('id')
    product = utils.get_product(id)
    return jsonify({"product": product})

@app.route('/xoa')
def xoa():
    id = request.args.get('id')
    type_product = request.args.get('type_product')
    utils.Del(id)
    # print(type_product)
    if type_product == '0':
        list_product = utils.getlist()
    else:
        list_product = utils.get_listtypeProduct(type_product)
    return render_template('./admin/sanpham.html', list_product=list_product)

@app.route('/update', methods =['get', 'post'])
def update():
    id = request.form.get('id')
    title = request.form.get('title')
    numtype = request.form.get('numtype')
    price = request.form.get('price')
    isHotChecked = request.form.get('isHotChecked')
    isNewChecked = request.form.get('isNewChecked')
    discount = request.form.get('discount')
    image = request.form.get('image')
    if "base64" in image:
        header, temp = image.split(",", 1)
        data = io.BytesIO(base64.b64decode(temp))
        response = cloudinary.uploader.upload(data)
        image = response['url']
    print(numtype)
    description = request.form.get('description')
    type_product = request.form.get('type_product_update')
    result = utils.update(id, isHotChecked, isNewChecked, title, numtype, price, discount, image, description)
    print(type_product)
    if type_product == '0':
        list_product = utils.getlist()
    else:
        list_product = utils.get_listtypeProduct(type_product)
    return render_template('./admin/sanpham.html', list_product=list_product)

@app.route('/type_list_product')
def type_list_product():
    id = request.args.get('id')
    if id == '0':
        list_product = utils.getlist()
    else:
        list_product = utils.get_listtypeProduct(id)
    return render_template('./admin/sanpham.html', list_product = list_product)

@app.route('/add_product', methods =['get', 'post'])
def add_product():
    title = request.form.get('title')
    type_product = request.form.get('type_product_add')
    numtype = request.form.get('numtype')
    price = request.form.get('price')
    isHotChecked = request.form.get('isHotChecked')
    isNewChecked = request.form.get('isNewChecked')
    discount = request.form.get('discount')
    image = request.form.get('image')
    header, temp = image.split(",", 1)
    data = io.BytesIO(base64.b64decode(temp))
    response = cloudinary.uploader.upload(data)
    # print(response['url'])
    description = request.form.get('description')
    result = utils.add_product(title,price, discount, response['url'], description, isHotChecked, isNewChecked, numtype)
    if type_product == '0':
        list_product = utils.getlist()
    else:
        list_product = utils.get_listtypeProduct(type_product)
    return render_template('./admin/sanpham.html', list_product=list_product)


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    # Truy vấn SQL để tìm kiếm sản phẩm
    list_product = utils.search(keyword)
    return render_template('./admin/sanpham.html', list_product=list_product)

@app.route('/delAcc')
def delAcc():
    id = request.args.get('id')
    type_acc = request.args.get('type_account')
    utils.delAcc(id)
    if type_acc == '0':
        listaccount = utils.get_listuser()
    else:
        listaccount = utils.get_listadmin()
    return render_template('./admin/account.html', listaccount=listaccount)

@app.route('/addAcc')
def addAcc():
    name = request.args.get('name')
    username = request.args.get('username')
    password = request.args.get('password')
    email = request.args.get('email')
    address = request.args.get('address')
    type_acc = request.args.get('type_account')
    isAdmin = request.args.get('temp')
    utils.addAcc(name, username, password, email, address, isAdmin )
    if type_acc == '0':
        listaccount = utils.get_listuser()
    else:
        listaccount = utils.get_listadmin()
    return render_template('./admin/account.html', listaccount=listaccount)

@app.route('/update_acc')
def update_acc():
    id = request.args.get('id')
    name = request.args.get('name')
    username = request.args.get('username')
    password = request.args.get('password')
    email = request.args.get('email')
    address = request.args.get('address')
    isAdmin = request.args.get('isAdmin')
    type_account = request.args.get('type_account')
    utils.update_acc(id, name, username, password, email, address, isAdmin)
    if type_account == 1:
        listaccount = utils.get_listuser()
    else:
        listaccount = utils.get_listadmin()
    return render_template('./admin/account.html', listaccount= listaccount)

@app.route('/search_acc', methods=['GET'])
def search_acc():
    keyword = request.args.get('keyword')
    listaccount = utils.search_acc(keyword)
    return render_template('./admin/account.html', listaccount=listaccount)





if __name__ == '__main__':
    app.run()
