import json
from PetShop import mysql
from flask import render_template, request, jsonify, session, redirect, url_for


def read_json(path):
    with open(path, "r", encoding='utf-8') as f:
        return json.load(f)

def checklogin( username, password):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT account.isAdmin, account.username, account.uID FROM account  WHERE username = '" + username + "' AND password = '" + password + "'")
    acc = None
    acc = cur.fetchone()
    return acc


def load_catefory():
    # return read_json('data/category.json')
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM category")
    categories = cur.fetchall()

    cur.close()

    return categories
def load_products():
    # products = read_json('data/products.json')
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM product")
    products = cur.fetchall()

    # Đóng cursor sau khi hoàn thành
    cur.close()

    return products

def load_category_products():
    # return render_template('shop.html', categories=cates, product=product)
    category_id = request.args.get('category')  # Lấy category từ query string

    cursor = mysql.connection.cursor()

    if category_id:
        # Nếu category_id được chọn, lấy danh sách sản phẩm theo category
        cursor.execute(f"SELECT * FROM product WHERE category_id = {category_id}")
        products = cursor.fetchall()
    else:
        # Nếu không có category_id, lấy tất cả sản phẩm
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()

    cursor.close()
    return products

def product_detail(product_id):
    cursor = mysql.connection.cursor()


    cursor.execute(f"SELECT * FROM product WHERE id = {product_id}")
    product = cursor.fetchone()

    cursor.close()
    return product



def add_to_cart(product_id):
    try:
        cur = mysql.connection.cursor()

        # Lấy thông tin user_id từ session hoặc bất kỳ phương thức nào khác bạn đang sử dụng để xác định người dùng hiện tại
        accountID = session.get('uID')
        print(accountID)

        # Kiểm tra sản phẩm có tồn tại trong CSDL hay không
        cur.execute("SELECT * FROM product WHERE id = %s", (product_id,))
        product = cur.fetchone()

        if product:
            # Thêm thông tin vào bảng cart
            cur.execute("INSERT INTO cart (accountID, productID, amount) VALUES (%s, %s, %s)", (accountID, product_id, 1))
            mysql.connection.commit()

            return jsonify({'message': 'Đã thêm sản phẩm vào giỏ hàng!'})
        else:
            return jsonify({'error': 'Sản phẩm không tồn tại!'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()


def view_cart():
    cur = mysql.connection.cursor()
    accountid = session.get('uID')
    print(accountid)

    cur.execute("SELECT * FROM cart WHERE accountID = %s", (accountid,))
    rows = cur.fetchall()  # Lấy tất cả các dòng có accountID tương ứng

    # Tính tổng số dòng
    count = len(rows)
    print(count)
    return count



def cart_detail():
    cursor = mysql.connection.cursor()
    accountID = session.get('uID')
    # Lấy thông tin các sản phẩm trong giỏ hàng từ cơ sở dữ liệu
    query = "SELECT  cart.maCart,product.title, product.image, product.price, cart.amount FROM cart JOIN product ON cart.productID = product.id WHERE cart.accountID = %s"
    cursor.execute(query, (accountID,))
    cart_items = cursor.fetchall()
    print(cart_items)

    cursor.close()
    return cart_items


def tongGia(account_ID):
    cursor = mysql.connection.cursor()
    sql = "SELECT SUM(product.price * cart.amount) AS total_price FROM cart JOIN product ON cart.productID = product.id WHERE cart.accountID = %s GROUP BY cart.accountID"
    val = (account_ID,)

    cursor.execute(sql, val)
    result = cursor.fetchone()

    cursor.close()

    if result:
        return result['total_price']  # Trả về giá trị total_price từ dictionary result
    else:
        return None  # Trường hợp không có dữ liệu, có thể trả về None hoặc một giá trị khác để xử lý



def latest_products():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM product WHERE new = 1 ORDER BY id DESC LIMIT 8"
    cursor.execute(query)
    latest_products = cursor.fetchall()
    cursor.close()
    return latest_products

def hot_products():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM product WHERE hot = 1 ORDER BY id DESC LIMIT 8"
    cursor.execute(query)
    hot_products = cursor.fetchall()
    cursor.close()
    return hot_products



# admin

def getlist():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM product JOIN category ON product.category_id = category.cid WHERE category.cname in ('Chó cảnh', 'Mèo cảnh', 'Thức ăn ', 'Đồ dùng & Đồ chơi & Phụ kiện', 'Vệ sinh & Chăm sóc', 'Chuồng, Nhà, Balo, Quây, Đệm', 'Thuốc & Thực phẩm chức năng');")
    list_product = cur.fetchall()
    return list_product

def Del(id):
    cur = mysql.connection.cursor()
    result = cur.execute("delete from product where id = " + str(id))
    mysql.connection.commit()

def update(id, hot, new, title, type_product, price, discount, image, description):
    cur = mysql.connection.cursor()
    result = cur.execute("UPDATE product set hot =" + hot + ", new = " + new + ", title = '" + title + "', category_id = " + type_product +", price = " + price + ", discount = " + discount +", image = '" + image + "', description = '" + description +"' where id = " + str(id))
    mysql.connection.commit()
    return "UPDATE product set hot =" + hot + ", new = " + new + ", title = '" + title + "', category_id = " + type_product +", price = " + price + ", discount = " + discount +", image = '" + image + "', description = '" + description +"' where id = " + str(id)
def get_product(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM product JOIN category ON product.category_id = category.cid WHERE product.id = " + str(id))
    product = cur.fetchone()
    return product

def add_product(title, price, discount, image, description, hot, new, type):
    cur = mysql.connection.cursor()
    if hot == "true" :
        hot = '1'
    else:
        hot = '0'
    if new == "true" :
        new = '1'
    else:
        new = '0'
    result = cur.execute("INSERT INTO product (category_id, title, price, discount, image, description, hot, new) VALUES (" + type +",'"+ title +"'," + price + "," + discount + ",'" + image + "','" + description + "'," + hot +"," + new +")")
    mysql.connection.commit()

def get_listtypeProduct(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM product WHERE category_id = " + str(id))
    list_product = cur.fetchall()
    return list_product

def get_listuser():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM account WHERE isAdmin = 0;")
    list_user = cur.fetchall()
    return list_user

def get_listadmin():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM account WHERE isAdmin = 1;")
    list_admin = cur.fetchall()
    return list_admin

def search(keyword):
    cur = mysql.connection.cursor()
    sql = "SELECT * FROM product WHERE LOWER(title) LIKE %s;"
    val = ('%' + keyword.lower() + '%',)
    cur.execute(sql, val)
    list_product = cur.fetchall()
    return list_product

def search_acc(keyword):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM account WHERE LOWER(name) LIKE '%" + keyword + "%'")
    list_acc = cur.fetchall()
    return list_acc

def delAcc(id):
    cur = mysql.connection.cursor()
    result = cur.execute("delete from account where uID = " + str(id))
    mysql.connection.commit()

def addAcc(name, username, password, email, address, isAdmin):
    cur = mysql.connection.cursor()
    result = cur.execute("INSERT INTO Account (username, password, email, address, isAdmin, name) VALUES ('" + username + "','" + password + "','" + email +"','" + address + "'," + str(isAdmin) + ",'" + name + "')")
    mysql.connection.commit()
    return result

def get_user(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM account WHERE uID = " + str(id))
    user = cur.fetchone()
    return user

def update_acc(id, name, username, password, email, address, isAdmin):
    cur = mysql.connection.cursor()
    result = cur.execute("UPDATE account set name ='" + name + "', username = '" + username + "', password = '" + password + "', email = '" + email + "', address = '" + address + "', isAdmin = " + isAdmin + " where uID = " + str(id))
    mysql.connection.commit()

def list_donhang():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT account.name,invoice.* FROM invoice JOIN account ON invoice.accountID = account.uID")
    list_dh = cur.fetchall()
    return list_dh

def Tongsanpham():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT COUNT(*) FROM product")
    tongsanpham = cur.fetchone()
    return tongsanpham['COUNT(*)']

def Tonguser():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT COUNT(*) FROM account WHERE isAdmin = 0")
    tonguser = cur.fetchone()
    return tonguser['COUNT(*)']

def TongDonHang():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT COUNT(*) FROM invoice")
    tongdh = cur.fetchone()
    return tongdh['COUNT(*)']

def Doanhthungay():
    tongdoanhthu = 0
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT tongGia FROM invoice WHERE DATE(ngayXuat) = DATE(CURDATE());")
    doanhthu = cur.fetchall()
    for i in doanhthu:
        tongdoanhthu += i['tongGia']
    return tongdoanhthu

def Doanhthuthang():
    tongdoanhthu = 0
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT tongGia FROM invoice WHERE DATE_FORMAT(ngayXuat, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    doanhthu = cur.fetchall()
    for i in doanhthu:
        tongdoanhthu += i['tongGia']
    return tongdoanhthu

