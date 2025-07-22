from flask import Blueprint, request, render_template, redirect, url_for, flash
from core.config.settings_manager import SettingsManager, SettingsError

settings_bp = Blueprint('settings', __name__)
settings_mgr = SettingsManager('nutpod')  # Or make device_name dynamic

@settings_bp.route('/', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Parse and validate form data
        try:
            ms = float(request.form.get('motion_sensitivity', 0.4))
            ms = min(max(ms, 0.0), 1.0)
            ra = request.form.get('record_audio') == 'true'
            se = request.form.get('streaming_enabled') == 'true'
            # Advanced settings
            duration = int(request.form.get('max_recording_duration', 30))
            if not (5 <= duration <= 300):
                duration = 30
            cleanup_days = int(request.form.get('cleanup_days', 30))
            if not (1 <= cleanup_days <= 90):
                cleanup_days = 30
            pre_buffer = float(request.form.get('pre_record_buffer', 1.0))
            if not (0.0 <= pre_buffer <= 5.0):
                pre_buffer = 1.0
            settings_mgr.update_setting('motion_sensitivity', ms)
            settings_mgr.update_setting('record_audio', ra)
            settings_mgr.update_setting('streaming_enabled', se)
            settings_mgr.update_setting('max_recording_duration', duration)
            settings_mgr.update_setting('cleanup_days', cleanup_days)
            settings_mgr.update_setting('pre_record_buffer', pre_buffer)
            settings_mgr.save_settings()
        except SettingsError as e:
            pass
        return redirect(url_for('settings.settings'))
    # GET: load current config
    settings = {
        'device_name': settings_mgr.get_setting('device_name'),
        'motion_sensitivity': settings_mgr.get_setting('motion_sensitivity'),
        'record_audio': settings_mgr.get_setting('record_audio'),
        'streaming_enabled': settings_mgr.get_setting('streaming_enabled'),
        'max_recording_duration': settings_mgr.get_setting('max_recording_duration'),
        'cleanup_days': settings_mgr.get_setting('cleanup_days'),
        'pre_record_buffer': settings_mgr.get_setting('pre_record_buffer'),
    }
    return render_template('settings.html', settings=settings)
