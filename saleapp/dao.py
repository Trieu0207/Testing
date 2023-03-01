from saleapp import app, db
from saleapp.models import Tuyen_bay, Chuyen_bay, Nguoi_dung, San_bay, Lich_bay, Ghe, Ve_may_bay, Hoa_don
from sqlalchemy import or_, and_
from flask_login import current_user
import hashlib
import re
from datetime import datetime
import cloudinary.uploader


def load_tuyen_bay():
    return Tuyen_bay.query.all()


def load_tuyen_bay_by_kw(kw=None):
    query = Tuyen_bay.query.all()
    if kw:
        query = Tuyen_bay.query.filter(or_(Tuyen_bay.diem_di.__eq__(kw),
                                           Tuyen_bay.diem_den.__eq__(kw),
                                           Tuyen_bay.ten.__eq__(kw),
                                           Tuyen_bay.id.__eq__(kw))).all()
    return query


def load_ten_diem_di():
    temp = Tuyen_bay.query.all()
    diem_di = []
    for t in temp:
        if t.diem_di not in diem_di:
            diem_di.append(t.diem_di)
    return sorted(diem_di)


def load_ten_diem_den():
    temp = Tuyen_bay.query.all()
    diem_den = []
    for t in temp:
        if t.diem_den not in diem_den:
            diem_den.append(t.diem_den)
    diem_den = sorted(diem_den)
    return sorted(diem_den)


def login(user_name, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    try:
        check_login(user_name, password)
        return Nguoi_dung.query.filter(Nguoi_dung.ten_dang_nhap.__eq__(user_name),
                                       Nguoi_dung.mat_khau.__eq__(password)).first()
    except Exception as ex:
        raise Exception(ex)


def register(ho_va_ten, ngay_sinh, email, sdt, ten_dang_nhap, mat_khau, avatar):
    ds_nguoi_dung = []
    check_pass = mat_khau
    if not strong_pass(check_pass):
        raise Exception("mật khẩu không hợp lệ")
    if not check_sdt(sdt):
        raise Exception("số điện thoại không hợp lệ")
    if not check_birth_day(ngay_sinh):
        raise Exception('Ngày sinh không hợp lệ')
    password = str(hashlib.md5(mat_khau.strip().encode('utf-8')).hexdigest())
    for d in Nguoi_dung.query.all():
        if d.ten_dang_nhap == ten_dang_nhap:
            ds_nguoi_dung.append(d.ten_dang_nhap)
    if ten_dang_nhap not in ds_nguoi_dung:
        nguoi_dung = Nguoi_dung(ho_va_ten=ho_va_ten.strip(),
                                ngay_thang_nam_sinh=ngay_sinh,
                                email=email.strip(),
                                sdt=sdt.strip(),
                                ten_dang_nhap=ten_dang_nhap.strip(),
                                mat_khau=password,
                                avatar=avatar)
        with app.app_context():
            db.session.add(nguoi_dung)
            db.session.commit()
    else:
        raise Exception("tên đăng nhập đã tồn tại")


def search_tuyen_bay(diem_di, diem_den):
    query = Tuyen_bay.query.filter(and_(Tuyen_bay.diem_di.__eq__(diem_di),
                                        Tuyen_bay.diem_den.__eq__(diem_den))).first()
    return query


def load_tuyen_bay_by_id(tuyen_bay_id):
    return Tuyen_bay.query.get(tuyen_bay_id)


def load_chuyen_bay_by_tuyen_bay_id(tuyen_bay_id):
    return Chuyen_bay.query.filter(Chuyen_bay.tuyen_bay_id == tuyen_bay_id).all()


def strong_pass(client_pass):
    pass_lenght = len(client_pass) > 8
    pass_up = re.search(r"[A-Z]", client_pass) is not None
    pass_low = re.search(r"[a-z]", client_pass) is not None
    pass_ok = not (pass_lenght or pass_low or pass_up)
    if (pass_lenght and pass_low and pass_up):
        return True
    else:
        return False


def check_sdt(client_sdt):
    sdt_lenght = len(client_sdt) >= 10
    sdt_char_up = re.search(r"[A-Z]", client_sdt) is None
    sdt_char_spe = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', client_sdt) is None
    sdt_char_low = re.search(r"[a-z]", client_sdt) is None
    if sdt_lenght and sdt_char_low and sdt_char_up and sdt_char_spe:
        return True
    else:
        return False


def check_login(user_name, password):
    temp = Nguoi_dung.query.filter(Nguoi_dung.ten_dang_nhap.__eq__(user_name)).first()
    if temp:
        if temp.mat_khau.__eq__(password):
            return True
        raise Exception("mật khẩu không đúng")
    raise Exception("tên đăng nhập không tồn tại")


def check_birth_day(birth_day):
    temp = datetime.strptime(birth_day, "%Y-%m-%d")
    if temp < datetime.today():
        return True
    else:
        return False


def search_san_bay_by_id(san_bay_id):
    if san_bay_id:
        return San_bay.query.get(san_bay_id)
    else:
        raise Exception("Không có dữ liệu")

def find_lich_bay(chuyen_bay_id):
    return Lich_bay.query.filter(Lich_bay.chuyen_bay_id == chuyen_bay_id).first()
def load_lich_bay(chuyen_bay):
    query = []
    lich_bay = Lich_bay.query.all()
    for c in chuyen_bay:
        for lich in lich_bay:
            if lich.chuyen_bay_id == c.id:
                query.append(lich)
    return query


def load_ds_ghe(chuyen_bay_id):
    return Ghe.query.filter(Ghe.Chiec_may_bay_id == chuyen_bay_id).all()
def reload_ds_ghe(chuyen_bay_id):
    ds_ghe = Ghe.query.filter(Ghe.Chiec_may_bay_id == chuyen_bay_id).all()
    for d in ds_ghe:
        if not d.ve_may_bays:
            d.trang_thai = False
            db.session.add(d)
        db.session.commit()

def load_table_ghe(chuyen_bay_id):
    chuyen = Chuyen_bay.query.get(chuyen_bay_id)
    count_ghe = Ghe.query.filter(Ghe.Chiec_may_bay_id == chuyen.may_bay_id).count()
    ds_ghe = load_ds_ghe(chuyen_bay_id)
    size = int((count_ghe / 3) + 1)
    table = []
    start = 0
    end = 3
    for i in range(size):
        temp = ds_ghe[start:end]
        start = end
        end += 3
        table.append(temp)
    return table
def load_gia_ve_by_chuyen_bay(tuyen_id, hang_ve):
    ds_gia = []
    chuyen = Chuyen_bay.query.filter(Chuyen_bay.tuyen_bay_id == tuyen_id).all()
    for c in chuyen:
        price = Ve_may_bay.query.filter(Ve_may_bay.chuyen_bay_id == c.id,
                                        Ve_may_bay.hang_ve.__eq__(hang_ve)).first()
        ds_gia.append(price)

    if ds_gia:
        return ds_gia
    else: raise Exception("Không tìm được chuyến bay")

def load_gia_ve(chuyen_bay):
    query = []
    ve = Ve_may_bay.query.all()
    for c in chuyen_bay:
        for v in ve:
            if Ve_may_bay.chuyen_bay_id == c.id:
                query.append(v)
    return query
def load_count_chuyen_bay(tuyen_bay_id):
    return Chuyen_bay.query.filter(Chuyen_bay.tuyen_bay_id == tuyen_bay_id).count()
def get_user_by_id(user_id):
    return Nguoi_dung.query.get(user_id)

def get_ve_bay_da_dat(chuyen_bay_id):
    return Ghe.query.filter(Chuyen_bay.id == chuyen_bay_id, Ghe.trang_thai is True).all()
def get_ve_chua_dat(chuyen_bay_id):
    chuyen = Chuyen_bay.query.get(chuyen_bay_id)

    return  Ghe.query.filter(Ghe.Chiec_may_bay_id == chuyen.may_bay_id, Ghe.trang_thai == False).all()
def check_vi_tri(ghe_id):
    if ghe_id:
        ghe = Ghe.query.get(ghe_id)
        if ghe:
           if ghe.trang_thai == False:
               return True
           else:
               return False
    return False


def get_chuyen_bay_by_id(chuyen_bay_id):
    return Chuyen_bay.query.get(chuyen_bay_id)
def get_ten_tuyen_bay_by_chuyen_bay(chuyen_bay_id):
    chuyen = Chuyen_bay.query.get(chuyen_bay_id)
    tuyen_id = chuyen.tuyen_bay_id
    return Tuyen_bay.query.get(tuyen_id)

def get_ve_by_chuyen_bay_id(chuyen_bay_id):
    return Ve_may_bay.query.filter(Ve_may_bay.chuyen_bay_id == chuyen_bay_id).first()

def xoa_ve(ve_id):
    ve_may_bay = Ve_may_bay.query.get(ve_id)
    user_id = current_user.id
    hoa_don = Hoa_don.query.filter(Hoa_don.nguoi_thanh_toan == user_id).first()
    if ve_may_bay:
        ve_may_bay.trang_thai = False
        ve_may_bay.ten = None
        ve_may_bay.ngay_sinh = None
        ve_may_bay.cccd = None
        ve_may_bay.hoa_don_id = None
        ve_may_bay.ghe_id = None
        ve_may_bay.nguoi_mua_id = None
        # cập nhật lại số lượng vé
        so_luong_ve = Ve_may_bay.query.filter(Ve_may_bay.hoa_don_id == hoa_don.id).count()
        hoa_don.so_luong_ve = so_luong_ve
        # cập nhật lại tổng tiền
        tong_tien = hoa_don.tong_tien
        tien_ve = ve_may_bay.gia_tien
        hoa_don.tong_tien = tong_tien - tien_ve

        db.session.add(ve_may_bay)
        db.session.commit()
        db.session.add(hoa_don)
        db.session.commit()



def dat_ve(ten, ngay_sinh, cccd, vi_tri_ngoi, chuyen,current_user):
    if current_user.is_authenticated:
        ghe = Ghe.query.get(vi_tri_ngoi)
        chuyen_bay = Chuyen_bay.query.get(chuyen)
        ve_may_bay = Ve_may_bay.query.filter(Ve_may_bay.chuyen_bay_id == chuyen_bay.id,
                                             Ve_may_bay.trang_thai == False).first()
        if ve_may_bay:
            ve_may_bay.ten = ten
            ve_may_bay.ngay_sinh = ngay_sinh
            ve_may_bay.cccd = cccd
            ve_may_bay.trang_thai = True
            ve_may_bay.ghe_id = ghe.id
            ve_may_bay.nguoi_mua_id = current_user.id
            ghe.trang_thai = True
            thoi_gian_thanh_toan = datetime.now()
            so_luong_ve = 1
            hoa_don = Hoa_don.query.filter(Hoa_don.nguoi_thanh_toan == current_user.id,
                                           Hoa_don.trang_thai == False).first()
            if hoa_don:
                ve_may_bay.hoa_don_id = hoa_don.id
                so_ve = hoa_don.so_luong_ve
                tong_gia = hoa_don.tong_tien
                hoa_don.so_luong_ve = so_ve + 1
                hoa_don.tong_tien = ve_may_bay.gia_tien + tong_gia
                db.session.add(hoa_don)
                db.session.commit()
            else:
                gia = ve_may_bay.gia_tien
                h = Hoa_don(thoi_gian_thanh_toan=thoi_gian_thanh_toan, so_luong_ve=so_luong_ve,
                            nguoi_thanh_toan=current_user.id)
                db.session.add(h)
                db.session.commit()
                new_hoa_don = Hoa_don.query.filter(Hoa_don.nguoi_thanh_toan == current_user.id,
                                                   Hoa_don.trang_thai == False).first()
                ve_may_bay.hoa_don_id = new_hoa_don.id
                db.session.add(ve_may_bay)
                db.session.commit()
            db.session.add(ve_may_bay)
            db.session.commit()
        else: raise Exception("Vé đã được đặt")
    else: raise Exception("chưa được đăng nhập")


def tong_ve(ten):
    count = Ve_may_bay.query.filter(Ve_may_bay.ten.__eq__(ten)).count()
def load_ds_ve_chua_thanh_toan(user):
    hoa_don = Hoa_don.query.filter(Hoa_don.nguoi_thanh_toan == user.id,
                                   Hoa_don.trang_thai == False).first()
    if hoa_don:
        return Ve_may_bay.query.filter(Ve_may_bay.hoa_don_id == hoa_don.id).all()



def tong_tien():
    hoa_don = Hoa_don.query.filter(Hoa_don.nguoi_thanh_toan == current_user.id,
                                   Hoa_don.trang_thai == False).first()
    if hoa_don:
        ds_ve = Ve_may_bay.query.filter(Ve_may_bay.hoa_don_id == hoa_don.id).all()
        tong = 0
        if ds_ve:
            for i in ds_ve:
                tong = tong + i.gia_tien
        hoa_don.tong_tien = tong
        db.session.add(hoa_don)
        db.session.commit()
        return tong
    else: return "Ban chua mua hang"