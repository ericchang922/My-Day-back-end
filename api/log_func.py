import logging

msg_log = logging.getLogger('message')


def log_func(request, status, message='null', code=''):
    if request is None:
        return 'no data'
    method = request.method
    ip = request.META['REMOTE_ADDR']
    data = request.data if method != 'GET' else request.query_params
    uid = data['uid']
    path = request.path_info
    msg_log.info(f'{uid}: {message}')
    return f'{uid}\tIP: {ip} \n\t\t\t\t\t\t{status}:{code} [{method}]{path}'
