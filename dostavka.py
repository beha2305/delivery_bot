import sqlite3
from  datetime import datetime
class Database:
    def __init__(self):
        self.connection = sqlite3.connect("delivery.db")
        self.connection.row_factory = sqlite3.Row
        self.cur = self.connection.cursor()
        self.cur.execute("""
            Create table if not exists "User"(
                "id" integer not null primary key autoincrement,
                "chat_id" integer not null,
                "tg_firstname" text not null,
                "tg_username" text,
                "lang" integer,
                "phone_number" text,
                "fullname" text,
                "joined_date" text
            )
        """)
        self.cur.execute("""
            Create table if not exists "Location"(
                "id" integer not null primary key autoincrement,
                "user_id" integer not null,
                "lat" text not null,
                "lon" text not null,
                "name" text 
            )
        """)

        self.cur.execute("""
                    Create table if not exists "Category"(
                        "id" integer not null primary key autoincrement,
                        "name" text not null ,
                        "photo" text
                    )
                """)
        self.cur.execute("""
                    Create table if not exists "Product"(
                        "id" integer not null primary key autoincrement,
                        "name" text ,
                        "photo" text,
                        "price" integer not null,
                        "is_available" integer not null,
                        "description" text,
                        "category_id" integer not null
                    )
                """)
        self.cur.execute("""
                    Create table if not exists "Bucket"(
                        "id" integer not null primary key autoincrement,
                        "user_id" integer not null
                    )
                """)
        self.cur.execute("""
                    Create table if not exists "Order"(
                        "id" integer not null primary key autoincrement,
                        "user_id" integer not null,
                        "location_id" integer not null,
                        "price" integer not null
                    )
                """)
        self.cur.execute("""
                    Create table if not exists "Bucketitem"(
                        "id" integer not null primary key autoincrement,
                        "bucket_id" integer not null,
                        "product_id" integer not null,
                        "count" integer not null
                    )
                """)
        self.cur.execute("""
                    Create table if not exists "Orderitem"(
                        "id" integer not null primary key autoincrement,
                        "order_id" integer not null,
                        "product_id" integer not null,
                        "count" integer not null
                    )
                """)
        self.cur.execute("""
            Create table if not exists "Userlog"(
                "user_id" integer not null,
                "log" text
            )
        """)
        self.connection.commit()

    def get_user(self, chat_id):
        user = self.cur.execute(f"""
            select * from user
            where chat_id = {chat_id}
        """).fetchone()
        if user:
            return user
        else:
            return None

    def add_user(self, **kwargs):
        if kwargs.get("chat_id") and kwargs.get("tg_firstname"):
            date_time = str(datetime.now())
            self.cur.execute("""
            insert into User (chat_id, tg_firstname, tg_username, joined_date)
            values (%d, "%s", " %s", "%s")
            """ % (kwargs.get("chat_id"), kwargs.get("tg_firstname"), kwargs.get("tg_username"), date_time))
            self.connection.commit()
        if kwargs.get("chat_id") and kwargs.get("lang"):
            self.cur.execute(f"""
                update User set lang = {kwargs.get("lang")}
                where chat_id = {kwargs.get("chat_id")}
            """)
            self.connection.commit()
        if kwargs.get("chat_id") and kwargs.get("fullname"):
            self.cur.execute("""
                update User set fullname = ?
                where chat_id = ?
            """, (kwargs.get("fullname"), kwargs.get("chat_id")))
            self.connection.commit()
        if kwargs.get("chat_id") and kwargs.get("phone_number"):
            self.cur.execute(f"""
                update User set phone_number = ?
                where chat_id = ?
            """, [kwargs.get("phone_number"), kwargs.get("chat_id")])
            self.connection.commit()
    def add_log(self, user_id, **kwargs):
        log = self.cur.execute(f"""
            select * from Userlog
            where user_id = {user_id}
        """).fetchone()
        if log:
            self.cur.execute(f"""
                update Userlog set log = ?
                where user_id = ?
            """, (kwargs["log"], user_id))
        else:
            self.cur.execute("""
                insert into Userlog
                values(?, ?)
            """, (user_id, kwargs["log"]))
        self.connection.commit()
    def get_log(self, user_id):
        log = self.cur.execute(f"""
            select log from Userlog
            where user_id = {user_id}
        """).fetchone()
        return log
    def get_category(self):
        categories = self.cur.execute("""
            select * from Category
            order by id asc
        """).fetchall()
        return categories
    def get_product(self, category_id):
        prodcuts = self.cur.execute(f"""
            select Product.*, Category.name as category_name, Category.photo as category_photo 
            from Product
            inner join Category on Product.category_id = Category.id
            where category_id = {category_id}
        """).fetchall()
        return prodcuts
    def get_productinfo(self, product_id):
        product = self.cur.execute(f"""
            select * from Product
            where Product.id = {product_id} and Product.is_available = 1
        """).fetchone()
        return product
    def add_bucket(self, user_id):
        check_bucket = self.cur.execute(f"""
            select * from Bucket
            where user_id = {user_id}
        """).fetchone()
        if not check_bucket:
            self.cur.execute(f"""
                insert into Bucket (user_id)
                values ({user_id})
            """)
        self.connection.commit()
    def get_bucket_id(self, chat_id):
        bucket_id = self.cur.execute(f"""
            select * from Bucket
            where user_id = {chat_id}
        """).fetchone()
        return bucket_id
    def add_item(self,id, item_id, quantity):
        self.cur.execute(f"""
            insert into Bucketitem(bucket_id, product_id, count)
            values ({id}, {item_id}, {quantity})
        """ )
        self.connection.commit()
    def get_item(self, bucket_id):
        bucket_products = self.cur.execute(f"""
            SELECT Bucketitem.* , Product.name as item_name, Product.price as item_price
            from Bucketitem
            inner join Product on Product.id = Bucketitem.product_id
            WHERE bucket_id = {bucket_id}
        """).fetchall()
        return bucket_products
    def plus_count(self, bucket_id, product_id, count):
        count_s = int(count) + 1
        print(f"""
            update Bucketitem set count = {count_s}
            where product_id = {product_id} and bucket_id = {bucket_id}
        """, count_s)
        self.cur.execute(f"""
            update Bucketitem set count = {count_s}
            where product_id = {product_id} and bucket_id = {bucket_id}
        """)
        self.connection.commit()
    def minus_count(self, bucket_id, product_id, count):
        if int(count) > 1:
            self.cur.execute(f"""
                        update Bucketitem set count = {int(count)} - 1
                        where product_id = {product_id} and bucket_id = {bucket_id}
            """)
        self.connection.commit()
    def clear_bucket(self, bucket_id):
        self.cur.execute(f"""
            Delete from Bucketitem
            where bucket_id = {bucket_id}
        """)
        self.connection.commit()
    def add_order(self, id , price, date):
        self.cur.execute(f"""
            insert into "Order_data" (user_id, price, order_date)
            values ({id}, {price}, "{date}")
        """)
        self.connection.commit()
        order_id = self.cur.execute(f"""
            select id from "Order_data" 
            where user_id = {id} and order_date = "{date}"
        """).fetchone()
        return order_id
    def add_order_item(self, order_id, product_id, count):
        self.cur.execute(f"""
            insert into "Orderitem" (order_id, product_id, count)
            values ({order_id}, {product_id}, {count})
        """)
        self.connection.commit()
    def update_item(self, item_id, count):
        self.cur.execute(f"""
            update Bucketitem set count = {count}
            where id = {item_id}
        """)
        self.connection.commit()
    def clear_item(self, item_id):
        self.cur.execute(f"""
            delete from Bucketitem 
            where id = {item_id}
        """)
        self.connection.commit()
    def get_orders(self, user_id):
        orders = self.cur.execute(f"""
            select * from Order_data
            where user_id = {user_id}
        """).fetchall()
        return orders
    def get_order_item(self, order_id):
        order_items = self.cur.execute(f"""
            select * from Orderitem
            where order_id = {order_id}
        """).fetchall()
        return order_items