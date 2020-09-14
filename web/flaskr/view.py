from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from web.flaskr.auth import login_required
from web.flaskr.models import Order, SettingValue, Log, PairSetting
from web.flaskr.database import db_session
from sqlalchemy import desc

bp = Blueprint('admin', __name__)


@bp.route('/', methods=('GET',))
@login_required
def index():
    return render_template('base.html')


@bp.route('/setting', methods=('GET',))
@login_required
def setting_view():
    objs = SettingValue.query.all()
    return render_template('setting.html', objs=objs)


@bp.route('/log', methods=('GET',))
@login_required
def log_view():
    objs = Log.query.order_by(desc(Log.created)).limit(40).all()
    return render_template('log.html', objs=objs)


@bp.route('/pairs', methods=('GET',))
@login_required
def pairs_view():
    objs = PairSetting.query.all()
    return render_template('pair.html', objs=objs)


@bp.route('/orders', methods=('GET',))
@login_required
def orders_view():
    objs = Order.query.order_by(desc(Order.id)).limit(40).all()
    return render_template('orders.html', objs=objs)


@bp.route('/setting/create_or_update', methods=('POST',))
@login_required
def setting_view_update():
    if request.method == 'POST':
        _type = request.form['type']
        slug = request.form['slug']
        value = request.form['value']
        if _type.lower() == 'update':
            SettingValue.query.filter_by(slug=slug).update({'value': value})
            db_session.commit()
        elif _type.lower() == 'create':
            new_setting = SettingValue(slug=slug, value=value)
            db_session.add(new_setting)
            db_session.commit()
        elif _type.lower() == 'delete':
            SettingValue.query.filter_by(slug=slug).delete()
            db_session.commit()
        return redirect(url_for('admin.setting_view'))


@bp.route('/pairs/create_or_update', methods=('POST',))
@login_required
def pairs_view_update():
    def get_request_data():
        to_bool = ['active', 'use_stop_loss']
        to_int = ['id', 'spend_sum']
        to_float = ['profit_markup', 'stop_loss']
        data = {}
        for i in request.form:
            if request.form[i] != '':
                data[i] = request.form[i]
                if i in to_bool:
                    data[i] = bool(request.form[i])
                elif i in to_int:
                    data[i] = int(request.form[i])
                elif i in to_float:
                    data[i] = float(request.form[i])
                else:
                    data[i] = request.form[i]
        if 'type' in data:
            del data['type']
        return data

    if request.method == 'POST':
        if request.form['type'] == 'update':
            data = get_request_data()
            pk = int(request.form['id'])
            PairSetting.query.filter_by(id=pk).update(data)
            db_session.commit()
        elif request.form['type'] == 'create':
            data = get_request_data()
            pair = PairSetting(**data)
            db_session.add(pair)
            db_session.commit()
        elif request.form['type'] == 'delete':
            pk = int(request.form['id'])
            PairSetting.query.filter_by(id=pk).delete()
            db_session.commit()
        return redirect(url_for('admin.pairs_view'))
