import cloudinary.uploader
from flask import render_template, request, redirect, url_for, session, jsonify
from saleapp import app, controller, login, utils
from flask_login import current_user
import dao
from cloudinary import uploader
import re
from flask_login import login_user, logout_user
from saleapp.admin import *


@app.route('/', methods=['get', 'post'])
def home():
    global tuyen_bay
    tuyen = dao.load_tuyen_bay_by_kw(kw=request.args.get('keyword'))
    all_tuyen = dao.load_tuyen_bay()
    ten_diem_di = dao.load_ten_diem_di()
    ten_diem_den = dao.load_ten_diem_den()
    if request.method.__eq__('POST'):
        diem_di = request.form['diem_di']
        diem_den = request.form['diem_den']
        tuyen_bay = dao.search_tuyen_bay(diem_di, diem_den)
        return render_template('index.html', tuyen_bay=tuyen_bay,
                               ten_diem_den=ten_diem_den,
                               ten_diem_di=ten_diem_di)
    return render_template('index.html', tuyen=tuyen, all_tuyen=all_tuyen,
                           ten_diem_den=ten_diem_den, ten_diem_di=ten_diem_di)


@app.route('/chuyen_bay/<int:tuyen_bay_id>')
def chuyen_bay(tuyen_bay_id):
    chuyen = dao.load_chuyen_bay_by_tuyen_bay_id(tuyen_bay_id)
    ten_diem_den = dao.load_ten_diem_den()
    ten_diem_di = dao.load_ten_diem_di()
    ex = ""
    try:
        tuyen = dao.load_tuyen_bay_by_id(tuyen_bay_id)
        san_di = dao.search_san_bay_by_id(chuyen[0].san_bay_di_id).ten_san_bay
        san_den = dao.search_san_bay_by_id(chuyen[0].san_bay_den_id).ten_san_bay
        lich_bay = dao.load_lich_bay(chuyen)
        count_chuyen = dao.load_count_chuyen_bay(tuyen_bay_id)
        ds_ve_normal = dao.load_gia_ve_by_chuyen_bay(tuyen_bay_id, "normal")
        ds_ve_vip = dao.load_gia_ve_by_chuyen_bay(tuyen_bay_id, "vip")

        return render_template('chuyenBays.html', ten_diem_den=ten_diem_den,
                               ten_diem_di=ten_diem_di, chuyen=chuyen, tuyen=tuyen,
                               san_di=san_di, san_den=san_den, lich_bay=lich_bay,
                               ds_ve_normal=ds_ve_normal, count_chuyen=count_chuyen, ds_ve_vip=ds_ve_vip)
    except Exception as e:
        ex = str(e)
    return render_template('chuyenBays.html', chuyen_bay=chuyen_bay, ex=ex)


@app.route('/ve/<int:chuyen_bay_id>')
def ve_bay(chuyen_bay_id):
    ds_ghe = dao.load_ds_ghe(chuyen_bay_id)
    dao.reload_ds_ghe(chuyen_bay_id)
    table_ghe = dao.load_table_ghe(chuyen_bay_id)
    ghe_da_dat = dao.get_ve_bay_da_dat(chuyen_bay_id)
    ghe_chua_dat = dao.get_ve_chua_dat(chuyen_bay_id)
    chuyen = dao.get_chuyen_bay_by_id(chuyen_bay_id)
    tuyen = dao.get_ten_tuyen_bay_by_chuyen_bay(chuyen_bay_id)
    lich_bay = dao.find_lich_bay(chuyen_bay_id)
    return render_template('ve.html', ds_ghe=ds_ghe, table_ghe=table_ghe,
                           ghe_da_dat=ghe_da_dat, ghe_chua_dat=ghe_chua_dat,
                           chuyen = chuyen, tuyen = tuyen, lich_bay = lich_bay)


@app.route('/register', methods=['get', 'post'])
def user_register():
    ex = ""
    global ho_ten, ngay_thang_nam_sinh, email, sdt, ten_dang_nhap, mat_khau
    if request.method.__eq__('POST'):
        ho_ten = request.form['first_name']
        ngay_thang_nam_sinh = request.form['birth_day']
        email = request.form['email']
        sdt = request.form['sdt']
        ten_dang_nhap = request.form['user_name']
        mat_khau = request.form['pass']
        file_to_upload = request.files['avatar']
        avt_path = ""
        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload)
            app.logger.info(upload_result)
            avt_path = upload_result['secure_url']
    try:

        dao.register(ho_va_ten=ho_ten, ngay_sinh=ngay_thang_nam_sinh,
                     email=email, sdt=sdt, ten_dang_nhap=ten_dang_nhap,
                     mat_khau=mat_khau, avatar=avt_path)
        return redirect(url_for('user_login'))
    except Exception as e:
        ex = str(e)

    return render_template('register.html', method=['get', 'post'], ex=ex)


@app.route('/login', methods=['get', 'post'])
def user_login():
    ex = ""
    if request.method.__eq__('POST'):
        user_name = request.form['user_name']
        password = request.form['password']
        try:
            user = dao.login(user_name=user_name, password=password)
            if user:
                login_user(user = user)
                return redirect(url_for('home'))
        except Exception as e:
            ex = str(e)
    return render_template('login.html', ex=ex)

@app.route('/laplich')
def lap_lich():
    test = "hello"


    return render_template('laplich.html', test = test)

@app.route('/user-logout')
def user_logout():
    logout_user()
    return redirect('/')


@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/ve', methods=['get', 'post'])
def info_ve():
    if request.method.__eq__('POST'):
        tong_ve = 0
        ten = request.form['name']
        ngay_sinh = request.form['birth_day']
        cccd = request.form['cccd']
        vi_tri_ngoi = request.form['ghe']
        chuyen_bay = request.form['chuyen']
        chuyen_bay_id = dao.get_chuyen_bay_by_id(chuyen_bay)
        err_mess=""
        if current_user.is_authenticated:
            dao.dat_ve(ten, ngay_sinh, cccd, vi_tri_ngoi, chuyen_bay, current_user)
            return redirect(url_for('ve_bay', chuyen_bay_id=chuyen_bay_id.id))
        err_mess = "Yêu cầu cần được đăng nhập"
        return redirect(url_for('ve_bay', chuyen_bay_id=chuyen_bay_id.id))
    return render_template('index.html')
@app.route('/thanh-toan', methods=['get', 'post'])
def thanh_toan():
    err_mess = "Bạn chưa mua vé"
    if current_user.is_authenticated:
        ds_ve = dao.load_ds_ve_chua_thanh_toan(current_user)
        tong_tien = dao.tong_tien()
        if request.method.__eq__('POST'):
            if request.form['ve_id']:
                ve_id = request.form['ve_id']
                dao.xoa_ve(ve_id)
                return redirect(url_for('thanh_toan'))

        if ds_ve:
            return render_template('thanh_toan.html', ds_ve=ds_ve, tong_tien=tong_tien)
        else:

            return render_template('thanh_toan.html', err_mess=err_mess)
    else:
        err_mess = "Bạn chưa đăng nhập"
        return render_template('thanh_toan.html', err_mess=err_mess)




if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
