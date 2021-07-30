def log_func(request, status, code=''):
    if request is None:
        return ''
    method = request.method
    ip = request.META['REMOTE_ADDR']
    data = request.data if method != 'GET' else request.query_params
    uid = data['uid']
    path = request.path_info
    return f'{uid}\tIP: {ip} \n\t\t\t\t\t\t{status}:{code} [{method}]{path}'
