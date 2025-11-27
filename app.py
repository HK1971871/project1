from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.secret_key = "supersecretkey"  # đổi thành key riêng của bạn
# Kết nối PostgreSQL (ví dụ)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/mydb'
# Nếu dùng MySQL: 'mysql://username:password@localhost/mydb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://huukhoiapp_user:752J2FDyzVF7DxTWs4q42jam142eH7oC@dpg-d4k0u2vdiees73b76bvg-a/huukhoiapp'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Định nghĩa bảng Users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

# Trang chủ: hiển thị danh sách user
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# Thêm user
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

# Sửa user
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', user=user)

# Xóa user
@app.route('/delete/<int:id>')
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Tạo bảng nếu chưa có
    with app.app_context():
        db.create_all()
    app.run(debug=True)