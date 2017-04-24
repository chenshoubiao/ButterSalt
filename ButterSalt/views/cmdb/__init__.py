from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required
from flask import render_template
from ButterSalt import salt
from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, SelectField


class Mid:
    def __init__(self, tgt):
        self.tgt = tgt

    def get_uptime(self):
        data = salt.execution_command_low(tgt=self.tgt, fun="status.uptime")
        return data

    def get_grains(self):
        data = salt.execution_command_low(tgt=self.tgt, fun="grains.items")
        return data


class StateForm(FlaskForm):
    salt_states = BooleanField('选择模板')
    salt_states_nfs = SelectField('nfs', choices=[('nfs-client', 'nfs-client'), ('nfs-server', 'nfs-server'),
                                                  (None, "")], option_widget=None)
    submit = SubmitField('提交')


cmdb = Blueprint('cmdb', __name__, url_prefix='/cmdb')


@cmdb.route('/')
@login_required
def index():
    data = salt.execution_command_low(client='runner', fun="manage.status")
    return render_template('cmdb/index.html', up=data['up'], down=data['down'])


@cmdb.route('/manage/')
@cmdb.route('/manage/<mid>', methods=['GET', 'POST'])
@login_required
def manage(mid=None):
    form = StateForm()
    if form.salt_states.raw_data or form.salt_states_nfs.data != 'None':
        if form.salt_states_nfs.data != 'None':
            __list = form.salt_states.raw_data.copy()
            __list.append(form.salt_states_nfs.data)
        else:
            __list = form.salt_states.raw_data.copy()

        __list = (','.join(__list))
        jid = salt.execution_command_minions(tgt=mid, fun='state.apply', args=[__list])

        flash('执行完成')
        return redirect(url_for('saltstack.jobs', jid=jid))
    mid_grains = Mid(mid)
    return render_template('cmdb/manage.html', uptime=mid_grains.get_uptime()[mid],
                           grains=mid_grains.get_grains()[mid],
                           form=form)
